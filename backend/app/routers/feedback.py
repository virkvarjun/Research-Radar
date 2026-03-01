"""Feedback endpoint for recording user actions."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.config import settings
from app.db import get_db
from app.models import Event, Paper, SavedPaper, User
from app.schemas.common import FeedbackRequest, FeedbackResponse
from app.services.email import verify_feedback_signature
from app.services.ranking import update_user_vector

router = APIRouter(tags=["feedback"])


@router.post("/feedback", response_model=FeedbackResponse)
async def record_feedback(
    body: FeedbackRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Record user feedback on a paper and update user vector."""
    # Verify paper exists
    result = await db.execute(select(Paper).where(Paper.id == body.paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    # Record event
    event = Event(
        user_id=user.id,
        paper_id=body.paper_id,
        action=body.action,
        source=body.source,
    )
    db.add(event)

    # If save action, also add to saved_papers
    if body.action == "save":
        existing = await db.execute(
            select(SavedPaper).where(
                SavedPaper.user_id == user.id,
                SavedPaper.paper_id == body.paper_id,
            )
        )
        if not existing.scalar_one_or_none():
            saved = SavedPaper(user_id=user.id, paper_id=body.paper_id)
            db.add(saved)

    # Update user vector
    if paper.embedding is not None and body.action in ("like", "save", "not_relevant"):
        new_vector = update_user_vector(
            current=user.embedding,
            paper_embedding=paper.embedding,
            action=body.action,
            alpha=settings.alpha_like,
            beta=settings.beta_dislike,
        )
        user.embedding = new_vector

    await db.commit()
    return FeedbackResponse(status="ok")


@router.get("/api/feedback")
async def email_feedback(
    u: str = Query(...),
    p: str = Query(...),
    a: str = Query(...),
    sig: str = Query(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle feedback from email click-through links."""
    if not verify_feedback_signature(u, p, a, sig):
        raise HTTPException(status_code=403, detail="Invalid signature")

    user_id = UUID(u)
    paper_id = UUID(p)

    # Verify paper exists
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    # Record event
    event = Event(
        user_id=user_id,
        paper_id=paper_id,
        action=a,
        source="email",
    )
    db.add(event)

    # If save, add to saved_papers
    if a == "save":
        existing = await db.execute(
            select(SavedPaper).where(
                SavedPaper.user_id == user_id,
                SavedPaper.paper_id == paper_id,
            )
        )
        if not existing.scalar_one_or_none():
            saved = SavedPaper(user_id=user_id, paper_id=paper_id)
            db.add(saved)

    # Update user vector
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user and paper.embedding is not None and a in ("save", "skip", "not_relevant"):
        action_map = {"save": "save", "skip": "skip", "not_relevant": "not_relevant"}
        new_vector = update_user_vector(
            current=user.embedding,
            paper_embedding=paper.embedding,
            action=action_map.get(a, a),
            alpha=settings.alpha_like,
            beta=settings.beta_dislike,
        )
        user.embedding = new_vector

    await db.commit()

    # Redirect to paper page
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"{settings.app_url}/paper/{paper_id}")
