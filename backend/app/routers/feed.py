"""Feed endpoint with ranking + MMR."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, and_, not_
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.models import Event, Paper, User
from app.schemas.common import FeedResponse, PaperOut
from app.services.ranking import (
    apply_role_constraints,
    mmr_rerank,
    score_paper,
)
from app.config import settings

router = APIRouter(tags=["feed"])


@router.get("/feed", response_model=FeedResponse)
async def get_feed(
    refresh: bool = Query(False, description="Return alternative diverse set"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get personalized paper feed for the user."""
    # Get papers the user has already interacted with
    seen_result = await db.execute(
        select(Event.paper_id).where(Event.user_id == user.id)
    )
    seen_ids = {row[0] for row in seen_result.fetchall()}

    # If refresh, also exclude papers from previous feed views
    exclude_ids = seen_ids

    # Get recent candidate papers
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    query = select(Paper).where(
        Paper.embedding.isnot(None),
        Paper.created_at >= cutoff,
    )
    if exclude_ids:
        query = query.where(not_(Paper.id.in_(exclude_ids)))

    query = query.order_by(Paper.created_at.desc()).limit(200)
    result = await db.execute(query)
    candidate_papers = result.scalars().all()

    if not candidate_papers:
        return FeedResponse(papers=[], has_more=False)

    # Get thread embeddings
    thread_embeddings = []
    for thread in user.threads:
        if thread.embedding:
            thread_embeddings.append(thread.embedding)

    # Score each candidate
    scored = []
    now = datetime.now(timezone.utc)
    for paper in candidate_papers:
        if not paper.embedding:
            continue

        days_old = max(0, (now - paper.created_at).days) if paper.created_at else 0
        score, explanation = score_paper(
            user_embedding=user.embedding,
            thread_embeddings=thread_embeddings,
            paper_embedding=paper.embedding,
            days_old=days_old,
            novelty_days=settings.novelty_days,
        )

        scored.append({
            "paper": paper,
            "score": score,
            "embedding": paper.embedding,
            "why_matched": explanation,
            "title": paper.title,
            "categories": paper.categories,
            "evidence": paper.evidence,
        })

    # Apply role constraints
    scored = apply_role_constraints(scored, user.role)

    # MMR re-ranking
    feed_size = settings.feed_size
    if refresh:
        # For refresh, use lower lambda for more diversity
        reranked = mmr_rerank(scored, feed_size, lambda_param=0.4)
    else:
        reranked = mmr_rerank(scored, feed_size, lambda_param=settings.mmr_lambda)

    # Build response
    papers_out = []
    for item in reranked:
        paper = item["paper"]
        paper_out = PaperOut.model_validate(paper)
        paper_out.why_matched = item.get("why_matched")
        papers_out.append(paper_out)

    return FeedResponse(
        papers=papers_out,
        has_more=len(scored) > feed_size,
    )
