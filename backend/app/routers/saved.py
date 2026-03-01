"""Saved papers endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.auth import get_current_user
from app.db import get_db
from app.models import SavedPaper, User
from app.schemas.common import SavedPaperOut

router = APIRouter(tags=["saved"])


@router.get("/saved", response_model=list[SavedPaperOut])
async def get_saved_papers(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all saved papers for the current user."""
    result = await db.execute(
        select(SavedPaper)
        .options(joinedload(SavedPaper.paper))
        .where(SavedPaper.user_id == user.id)
        .order_by(SavedPaper.saved_at.desc())
    )
    saved = result.scalars().unique().all()
    return saved
