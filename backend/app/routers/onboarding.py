"""Onboarding endpoints."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.models import Paper, Thread, User
from app.schemas.common import OnboardingAnswers, PaperOut
from app.services.embeddings import embed_text, normalize_vector
from app.services.ranking import update_user_vector

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/onboarding", tags=["onboarding"])


@router.post("/answers")
async def submit_onboarding(
    answers: OnboardingAnswers,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Process onboarding answers and produce user + thread vectors."""
    # Update role and topics
    user.role = answers.role
    user.topics = answers.topics

    # Create thread vectors from topics (graceful if embedding fails)
    for topic in answers.topics:
        try:
            topic_embedding = await embed_text(topic)
        except Exception as e:
            logger.warning(f"Could not embed topic '{topic}': {e}")
            topic_embedding = None
        thread = Thread(
            user_id=user.id,
            label=topic,
            embedding=topic_embedding,
        )
        db.add(thread)

    # Process anchor paper labels
    user_vector = user.embedding
    for paper_id_str, label in answers.anchor_labels.items():
        result = await db.execute(
            select(Paper).where(Paper.id == paper_id_str)
        )
        paper = result.scalar_one_or_none()
        if paper and paper.embedding is not None:
            if label == "interested":
                user_vector = update_user_vector(user_vector, paper.embedding, "like")
            elif label == "not_interested":
                user_vector = update_user_vector(user_vector, paper.embedding, "not_relevant")

    # Process pairwise choices
    for choice in answers.pairwise_choices:
        winner_id = choice.get("winner_id")
        loser_id = choice.get("loser_id")
        if winner_id:
            result = await db.execute(select(Paper).where(Paper.id == winner_id))
            winner = result.scalar_one_or_none()
            if winner and winner.embedding is not None:
                user_vector = update_user_vector(user_vector, winner.embedding, "like")
        if loser_id:
            result = await db.execute(select(Paper).where(Paper.id == loser_id))
            loser = result.scalar_one_or_none()
            if loser and loser.embedding is not None:
                user_vector = update_user_vector(user_vector, loser.embedding, "not_relevant")

    user.embedding = user_vector
    user.onboarded = True
    await db.commit()

    return {"status": "ok", "message": "Onboarding complete"}


@router.get("/anchor-papers", response_model=list[PaperOut])
async def get_anchor_papers(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return 12 diverse anchor papers for onboarding step 3."""
    result = await db.execute(
        select(Paper)
        .where(Paper.embedding.isnot(None))
        .order_by(Paper.created_at.desc())
        .limit(12)
    )
    papers = result.scalars().all()
    return papers


@router.get("/pairwise-papers", response_model=list[dict])
async def get_pairwise_papers(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return 10 pairs of papers for pairwise comparison (step 4)."""
    result = await db.execute(
        select(Paper)
        .where(Paper.embedding.isnot(None))
        .order_by(Paper.created_at.desc())
        .limit(20)
    )
    papers = result.scalars().all()

    pairs = []
    for i in range(0, min(len(papers), 20), 2):
        if i + 1 < len(papers):
            pairs.append({
                "paper_a": PaperOut.model_validate(papers[i]),
                "paper_b": PaperOut.model_validate(papers[i + 1]),
            })

    return pairs[:10]
