"""Integration test: seed user + papers → feed → feedback → verify changes."""

import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import numpy as np
import pytest

from app.services.embeddings import cosine_similarity, normalize_vector
from app.services.ranking import (
    mmr_rerank,
    score_paper,
    update_user_vector,
    apply_role_constraints,
)


class TestEndToEndRanking:
    """Integration test simulating the full flow without DB."""

    def _make_paper(self, seed: int, title: str = "Paper"):
        np.random.seed(seed)
        return {
            "id": str(uuid.uuid4()),
            "title": f"{title} {seed}",
            "embedding": normalize_vector(np.random.randn(1536).tolist()),
            "score": 0.0,
            "categories": [],
            "evidence": {},
            "why_matched": {},
        }

    def test_full_flow(self):
        """Seed user + papers → rank → feedback → re-rank → verify changes."""
        # 1. Create user vector from "onboarding"
        np.random.seed(0)
        user_vec = normalize_vector(np.random.randn(1536).tolist())
        threads = [normalize_vector(np.random.randn(1536).tolist()) for _ in range(2)]

        # 2. Create papers
        papers = [self._make_paper(i) for i in range(1, 21)]

        # 3. Score papers
        for paper in papers:
            score, explanation = score_paper(
                user_embedding=user_vec,
                thread_embeddings=threads,
                paper_embedding=paper["embedding"],
                days_old=0,
            )
            paper["score"] = score
            paper["why_matched"] = explanation

        # 4. MMR re-rank
        feed = mmr_rerank(papers, k=5)
        assert len(feed) == 5

        # Record which paper was top
        top_paper = feed[0]
        original_top_score = top_paper["score"]

        # 5. Simulate "not_relevant" feedback on top paper
        user_vec = update_user_vector(
            user_vec,
            top_paper["embedding"],
            "not_relevant",
            beta=0.3,
        )

        # 6. Re-score
        for paper in papers:
            score, explanation = score_paper(
                user_embedding=user_vec,
                thread_embeddings=threads,
                paper_embedding=paper["embedding"],
                days_old=0,
            )
            paper["score"] = score

        # 7. Re-rank
        new_feed = mmr_rerank(papers, k=5)

        # The previously top paper should now have a lower score
        for paper in papers:
            if paper["id"] == top_paper["id"]:
                assert paper["score"] < original_top_score

    def test_like_improves_similar_papers(self):
        """Liking a paper should improve scores of similar papers."""
        np.random.seed(42)
        user_vec = normalize_vector(np.random.randn(1536).tolist())

        # Create a "target" paper and some similar/different papers
        target = normalize_vector(np.random.randn(1536).tolist())
        similar = normalize_vector(
            (np.array(target) + 0.1 * np.random.randn(1536)).tolist()
        )
        different = normalize_vector(np.random.randn(1536).tolist())

        # Score before like
        sim_score_before, _ = score_paper(user_vec, [], similar, 0)
        diff_score_before, _ = score_paper(user_vec, [], different, 0)

        # Like the target
        user_vec = update_user_vector(user_vec, target, "like", alpha=0.5)

        # Score after like
        sim_score_after, _ = score_paper(user_vec, [], similar, 0)
        diff_score_after, _ = score_paper(user_vec, [], different, 0)

        # Similar paper should improve more than different paper
        sim_improvement = sim_score_after - sim_score_before
        diff_improvement = diff_score_after - diff_score_before
        assert sim_improvement > diff_improvement

    def test_role_constraints_integration(self):
        """Role constraints should affect final ranking."""
        papers = [
            {"title": "A Survey of Deep Learning", "score": 0.5, "categories": [], "evidence": {}, "why_matched": {}, "embedding": [0]*10, "id": "1"},
            {"title": "Novel Architecture", "score": 0.55, "categories": [], "evidence": {}, "why_matched": {}, "embedding": [1]*10, "id": "2"},
        ]

        result = apply_role_constraints(papers.copy(), "student")
        # Survey should get boosted for students
        survey = [p for p in result if "Survey" in p["title"]][0]
        assert survey["score"] > 0.5

    def test_refresh_increases_diversity(self):
        """Refresh with lower lambda should produce more diverse results."""
        np.random.seed(42)
        base = np.random.randn(1536)

        # Create candidates: some similar, some different
        candidates = []
        for i in range(10):
            if i < 5:
                emb = (base + 0.01 * np.random.randn(1536)).tolist()
            else:
                emb = np.random.randn(1536).tolist()
            candidates.append({
                "score": 1.0 - i * 0.05,
                "embedding": emb,
                "id": i,
            })

        # Normal feed (high lambda = relevance-focused)
        normal = mmr_rerank(candidates, k=5, lambda_param=0.9)
        # Refresh (low lambda = diversity-focused)
        refresh = mmr_rerank(candidates, k=5, lambda_param=0.3)

        # Calculate avg pairwise similarity
        def avg_sim(results):
            sims = []
            for i in range(len(results)):
                for j in range(i + 1, len(results)):
                    if results[i].get("embedding") and results[j].get("embedding"):
                        sims.append(cosine_similarity(results[i]["embedding"], results[j]["embedding"]))
            return np.mean(sims) if sims else 0

        normal_sim = avg_sim(normal)
        refresh_sim = avg_sim(refresh)
        # Refresh should have lower avg similarity (more diverse)
        assert refresh_sim <= normal_sim + 0.1  # Allow small tolerance
