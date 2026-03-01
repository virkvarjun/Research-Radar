"""Tests for ranking, MMR, and feedback vector update."""

import numpy as np
import pytest

from app.services.embeddings import cosine_similarity, normalize_vector
from app.services.ranking import (
    apply_role_constraints,
    mmr_rerank,
    score_paper,
    update_user_vector,
)


class TestUpdateUserVector:
    def test_like_from_none(self, sample_embedding):
        """Like with no prior vector → normalized paper embedding."""
        result = update_user_vector(None, sample_embedding, "like")
        assert result is not None
        assert len(result) == len(sample_embedding)
        # Should be normalized
        norm = np.linalg.norm(result)
        assert abs(norm - 1.0) < 1e-6

    def test_like_moves_toward_paper(self, sample_embedding, sample_embedding_2):
        """Like should move user vector closer to paper."""
        user_vec = normalize_vector(sample_embedding)
        result = update_user_vector(user_vec, sample_embedding_2, "like", alpha=0.5)
        sim_before = cosine_similarity(user_vec, sample_embedding_2)
        sim_after = cosine_similarity(result, sample_embedding_2)
        assert sim_after > sim_before

    def test_save_same_as_like(self, sample_embedding, sample_embedding_2):
        """Save action should move vector same as like."""
        user_vec = normalize_vector(sample_embedding)
        result_like = update_user_vector(user_vec, sample_embedding_2, "like")
        result_save = update_user_vector(user_vec, sample_embedding_2, "save")
        # Should be identical
        assert np.allclose(result_like, result_save, atol=1e-10)

    def test_dislike_moves_away(self, sample_embedding, sample_embedding_2):
        """Not-relevant should move user vector away from paper."""
        user_vec = normalize_vector(sample_embedding)
        result = update_user_vector(user_vec, sample_embedding_2, "not_relevant", beta=0.5)
        sim_before = cosine_similarity(user_vec, sample_embedding_2)
        sim_after = cosine_similarity(result, sample_embedding_2)
        assert sim_after < sim_before

    def test_skip_no_change(self, sample_embedding, sample_embedding_2):
        """Skip should not change user vector."""
        user_vec = normalize_vector(sample_embedding)
        result = update_user_vector(user_vec, sample_embedding_2, "skip")
        assert result == user_vec

    def test_result_is_normalized(self, sample_embedding, sample_embedding_2):
        """Result should always be L2-normalized."""
        user_vec = normalize_vector(sample_embedding)
        for action in ["like", "save", "not_relevant"]:
            result = update_user_vector(user_vec, sample_embedding_2, action)
            norm = np.linalg.norm(result)
            assert abs(norm - 1.0) < 1e-6, f"Not normalized for action={action}"

    def test_dislike_from_none(self, sample_embedding):
        """Dislike with no prior vector → returns paper embedding unchanged."""
        result = update_user_vector(None, sample_embedding, "not_relevant")
        assert result == sample_embedding


class TestScorePaper:
    def test_basic_scoring(self, sample_embedding, sample_embedding_2):
        score, explanation = score_paper(
            user_embedding=sample_embedding,
            thread_embeddings=[sample_embedding_2],
            paper_embedding=sample_embedding,
            days_old=0,
        )
        assert score > 0
        assert "user_similarity" in explanation
        assert "thread_similarity" in explanation
        assert "novelty" in explanation
        assert "total_score" in explanation

    def test_no_user_embedding(self, sample_embedding):
        score, explanation = score_paper(
            user_embedding=None,
            thread_embeddings=[],
            paper_embedding=sample_embedding,
            days_old=0,
        )
        assert explanation["user_similarity"] == 0.0
        # Novelty still contributes
        assert score >= 0

    def test_novelty_decreases_with_age(self, sample_embedding):
        score_new, _ = score_paper(None, [], sample_embedding, days_old=0)
        score_old, _ = score_paper(None, [], sample_embedding, days_old=7)
        assert score_new > score_old

    def test_self_similarity_highest(self, sample_embedding, sample_embedding_2):
        score_self, _ = score_paper(sample_embedding, [], sample_embedding, days_old=0)
        score_other, _ = score_paper(sample_embedding, [], sample_embedding_2, days_old=0)
        assert score_self > score_other


class TestMMRRerank:
    def _make_candidates(self, n, dim=1536):
        np.random.seed(42)
        return [
            {
                "score": np.random.random(),
                "embedding": np.random.randn(dim).tolist(),
                "id": i,
            }
            for i in range(n)
        ]

    def test_empty_candidates(self):
        assert mmr_rerank([], k=5) == []

    def test_fewer_than_k(self):
        candidates = self._make_candidates(3)
        result = mmr_rerank(candidates, k=5)
        assert len(result) == 3

    def test_returns_k(self):
        candidates = self._make_candidates(20)
        result = mmr_rerank(candidates, k=5)
        assert len(result) == 5

    def test_highest_score_first(self):
        candidates = self._make_candidates(10)
        result = mmr_rerank(candidates, k=5, lambda_param=1.0)
        # With lambda=1.0, should be pure score ranking
        scores = [c["score"] for c in result]
        assert scores == sorted(scores, reverse=True)

    def test_diversity_lambda_zero(self):
        """With lambda=0, should maximize diversity."""
        np.random.seed(42)
        # Create candidates where some are very similar
        base = np.random.randn(1536)
        candidates = [
            {"score": 0.9, "embedding": (base + 0.01 * np.random.randn(1536)).tolist(), "id": 0},
            {"score": 0.85, "embedding": (base + 0.01 * np.random.randn(1536)).tolist(), "id": 1},
            {"score": 0.5, "embedding": np.random.randn(1536).tolist(), "id": 2},
        ]
        result = mmr_rerank(candidates, k=2, lambda_param=0.0)
        # Should pick diverse papers, not just highest-scoring similar ones
        ids = {c["id"] for c in result}
        assert 2 in ids  # The diverse paper should be selected

    def test_single_paper(self):
        candidates = self._make_candidates(1)
        result = mmr_rerank(candidates, k=1)
        assert len(result) == 1


class TestApplyRoleConstraints:
    def test_student_boost_survey(self):
        papers = [{"title": "A Survey of Deep Learning", "score": 0.5, "categories": [], "evidence": {}, "why_matched": {}}]
        result = apply_role_constraints(papers, "student")
        assert result[0]["score"] > 0.5

    def test_student_no_boost_regular(self):
        papers = [{"title": "Novel Architecture for NLP", "score": 0.5, "categories": [], "evidence": {}, "why_matched": {}}]
        result = apply_role_constraints(papers, "student")
        assert result[0]["score"] == 0.5

    def test_builder_boost_code(self):
        papers = [{"title": "Test", "score": 0.5, "categories": [], "evidence": {"code_link": "https://github.com/test"}, "why_matched": {}}]
        result = apply_role_constraints(papers, "builder")
        assert result[0]["score"] > 0.5

    def test_lab_boost_datasets(self):
        papers = [{"title": "Test", "score": 0.5, "categories": [], "evidence": {"datasets": ["ImageNet"]}, "why_matched": {}}]
        result = apply_role_constraints(papers, "lab")
        assert result[0]["score"] > 0.5

    def test_no_evidence_no_boost(self):
        papers = [{"title": "Test", "score": 0.5, "categories": [], "evidence": None, "why_matched": {}}]
        result = apply_role_constraints(papers, "builder")
        assert result[0]["score"] == 0.5
