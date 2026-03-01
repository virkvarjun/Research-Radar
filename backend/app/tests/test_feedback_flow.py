"""Tests for the full feedback → vector update → feed re-ranking flow."""

import uuid

import numpy as np
import pytest

from app.services.embeddings import cosine_similarity, normalize_vector
from app.services.ranking import mmr_rerank, score_paper, update_user_vector


class TestFeedbackVectorUpdates:
    """Test that feedback actions correctly alter user vector and downstream ranking."""

    def _make_papers(self, n=10, dim=1536):
        """Create n papers with random embeddings."""
        np.random.seed(42)
        papers = []
        for i in range(n):
            papers.append({
                "id": str(uuid.uuid4()),
                "title": f"Paper {i}",
                "embedding": normalize_vector(np.random.randn(dim).tolist()),
                "score": 0.0,
                "categories": [],
                "evidence": {},
                "why_matched": {},
            })
        return papers

    def _score_papers(self, user_vec, threads, papers):
        """Score all papers against user vector."""
        for paper in papers:
            score, explanation = score_paper(
                user_embedding=user_vec,
                thread_embeddings=threads,
                paper_embedding=paper["embedding"],
                days_old=0,
            )
            paper["score"] = score
            paper["why_matched"] = explanation
        return papers

    def test_save_moves_toward_paper(self):
        """Saving a paper should make user vector closer to it."""
        np.random.seed(1)
        user_vec = normalize_vector(np.random.randn(1536).tolist())
        paper_emb = normalize_vector(np.random.randn(1536).tolist())

        sim_before = cosine_similarity(user_vec, paper_emb)
        user_vec = update_user_vector(user_vec, paper_emb, "save", alpha=0.3)
        sim_after = cosine_similarity(user_vec, paper_emb)

        assert sim_after > sim_before

    def test_not_relevant_moves_away(self):
        """Not-relevant should move user vector away from paper."""
        np.random.seed(2)
        user_vec = normalize_vector(np.random.randn(1536).tolist())
        paper_emb = normalize_vector(np.random.randn(1536).tolist())

        sim_before = cosine_similarity(user_vec, paper_emb)
        user_vec = update_user_vector(user_vec, paper_emb, "not_relevant", beta=0.3)
        sim_after = cosine_similarity(user_vec, paper_emb)

        assert sim_after < sim_before

    def test_skip_no_change(self):
        """Skip should not alter user vector."""
        np.random.seed(3)
        user_vec = normalize_vector(np.random.randn(1536).tolist())
        paper_emb = normalize_vector(np.random.randn(1536).tolist())

        result = update_user_vector(user_vec, paper_emb, "skip")
        assert result == user_vec

    def test_click_no_change(self):
        """Click should not alter user vector."""
        np.random.seed(4)
        user_vec = normalize_vector(np.random.randn(1536).tolist())
        paper_emb = normalize_vector(np.random.randn(1536).tolist())

        result = update_user_vector(user_vec, paper_emb, "click")
        assert result == user_vec

    def test_repeated_likes_converge(self):
        """Repeatedly liking the same paper should converge user vector to it."""
        np.random.seed(5)
        user_vec = normalize_vector(np.random.randn(1536).tolist())
        paper_emb = normalize_vector(np.random.randn(1536).tolist())

        for _ in range(50):
            user_vec = update_user_vector(user_vec, paper_emb, "like", alpha=0.5)

        sim = cosine_similarity(user_vec, paper_emb)
        assert sim > 0.95

    def test_feedback_affects_ranking_order(self):
        """After liking a paper, similar papers should rank higher."""
        papers = self._make_papers(20)
        np.random.seed(0)
        user_vec = normalize_vector(np.random.randn(1536).tolist())

        # Initial ranking
        papers = self._score_papers(user_vec, [], papers)
        initial_feed = mmr_rerank(papers, k=5, lambda_param=1.0)
        initial_ids = [p["id"] for p in initial_feed]

        # Like a specific paper (not in the top 5)
        target = papers[15]
        user_vec = update_user_vector(user_vec, target["embedding"], "like", alpha=0.8)

        # Re-score
        papers = self._score_papers(user_vec, [], papers)
        new_feed = mmr_rerank(papers, k=5, lambda_param=1.0)
        new_ids = [p["id"] for p in new_feed]

        # The rankings should have changed
        assert initial_ids != new_ids

    def test_output_always_normalized(self):
        """All feedback outputs should be L2-normalized."""
        np.random.seed(6)
        user_vec = normalize_vector(np.random.randn(1536).tolist())
        paper_emb = normalize_vector(np.random.randn(1536).tolist())

        for action in ["like", "save", "not_relevant"]:
            result = update_user_vector(user_vec, paper_emb, action)
            norm = np.linalg.norm(result)
            assert abs(norm - 1.0) < 1e-6, f"Not normalized for {action}"
