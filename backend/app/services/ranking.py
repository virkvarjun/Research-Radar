"""Ranking, MMR diversity, and user vector update logic."""

import logging
from typing import Optional

import numpy as np

from app.services.embeddings import cosine_similarity, normalize_vector

logger = logging.getLogger(__name__)


def update_user_vector(
    current: Optional[list[float]],
    paper_embedding: list[float],
    action: str,
    alpha: float = 0.1,
    beta: float = 0.05,
) -> list[float]:
    """Update user vector based on feedback action.

    like/save: u ← normalize(u + α·p)
    dislike (not_relevant): u ← normalize(u − β·p)
    skip: no change
    """
    if current is None:
        if action in ("like", "save"):
            return normalize_vector(paper_embedding)
        return paper_embedding  # Can't subtract from nothing

    u = np.array(current, dtype=np.float64)
    p = np.array(paper_embedding, dtype=np.float64)

    if action in ("like", "save"):
        u = u + alpha * p
    elif action == "not_relevant":
        u = u - beta * p
    else:
        # skip or click: no change to vector
        return current

    return normalize_vector(u.tolist())


def score_paper(
    user_embedding: Optional[list[float]],
    thread_embeddings: list[list[float]],
    paper_embedding: list[float],
    days_old: int = 0,
    novelty_days: int = 7,
) -> tuple[float, dict]:
    """Score a paper for a user. Returns (score, explanation_dict)."""
    explanation: dict = {}

    # User similarity
    user_sim = 0.0
    if user_embedding:
        user_sim = cosine_similarity(user_embedding, paper_embedding)
    explanation["user_similarity"] = round(user_sim, 4)

    # Thread similarity (max across threads)
    thread_sim = 0.0
    best_thread_idx = -1
    for i, t_emb in enumerate(thread_embeddings):
        sim = cosine_similarity(t_emb, paper_embedding)
        if sim > thread_sim:
            thread_sim = sim
            best_thread_idx = i
    explanation["thread_similarity"] = round(thread_sim, 4)
    explanation["best_thread_index"] = best_thread_idx

    # Novelty: newer papers get a boost
    novelty = max(0.0, 1.0 - (days_old / max(novelty_days, 1)))
    explanation["novelty"] = round(novelty, 4)

    score = user_sim + thread_sim + 0.2 * novelty
    explanation["total_score"] = round(score, 4)

    return score, explanation


def mmr_rerank(
    candidates: list[dict],
    k: int,
    lambda_param: float = 0.7,
) -> list[dict]:
    """Maximal Marginal Relevance re-ranking for diversity.

    Each candidate dict must have 'embedding' (list[float]) and 'score' (float).
    Returns top-k candidates re-ranked by MMR.
    """
    if not candidates:
        return []
    if len(candidates) <= k:
        return sorted(candidates, key=lambda c: c["score"], reverse=True)

    selected: list[dict] = []
    remaining = list(candidates)

    # Pick highest score first
    remaining.sort(key=lambda c: c["score"], reverse=True)
    selected.append(remaining.pop(0))

    while len(selected) < k and remaining:
        best_mmr = -float("inf")
        best_idx = 0

        for i, cand in enumerate(remaining):
            relevance = cand["score"]

            # Max similarity to already selected
            max_sim = 0.0
            for sel in selected:
                if cand.get("embedding") and sel.get("embedding"):
                    sim = cosine_similarity(cand["embedding"], sel["embedding"])
                    max_sim = max(max_sim, sim)

            mmr = lambda_param * relevance - (1 - lambda_param) * max_sim
            if mmr > best_mmr:
                best_mmr = mmr
                best_idx = i

        selected.append(remaining.pop(best_idx))

    return selected


def apply_role_constraints(papers: list[dict], role: str) -> list[dict]:
    """Apply role-based filtering/boosting.

    student: boost survey/review papers
    builder: boost papers with code links
    lab: boost papers with datasets/baselines
    """
    for paper in papers:
        boost = 0.0
        categories = paper.get("categories", []) or []
        evidence = paper.get("evidence", {}) or {}

        if role == "student":
            title_lower = paper.get("title", "").lower()
            if any(kw in title_lower for kw in ["survey", "review", "tutorial", "overview"]):
                boost = 0.15
        elif role == "builder":
            if evidence.get("code_link"):
                boost = 0.15
        elif role == "lab":
            if evidence.get("datasets") or evidence.get("baselines"):
                boost = 0.1

        paper["score"] = paper.get("score", 0) + boost
        paper.get("why_matched", {})["role_boost"] = round(boost, 4)

    return papers
