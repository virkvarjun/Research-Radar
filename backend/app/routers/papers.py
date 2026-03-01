"""Paper detail, save, and chat endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.models import Paper, SavedPaper, User
from app.schemas.common import ChatRequest, ChatResponse, PaperDetail
from app.services.chat import chat_with_paper
from app.services.evidence import build_rigour_panel

router = APIRouter(prefix="/papers", tags=["papers"])


@router.get("/{paper_id}", response_model=PaperDetail)
async def get_paper(
    paper_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get paper details with rigour panel."""
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    paper = result.scalar_one_or_none()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    detail = PaperDetail.model_validate(paper)
    detail.chunks_available = bool(paper.chunks)

    if paper.evidence:
        detail.rigour_panel = build_rigour_panel(paper.evidence)
    else:
        # Return "not found" indicators
        detail.rigour_panel = {
            key: {"status": "not_found", "indicator": "❌", "items": [], "count": 0}
            for key in ["datasets", "metrics", "baselines", "limitations"]
        }
        detail.rigour_panel["code_link"] = {
            "status": "not_found",
            "indicator": "❌",
            "url": None,
        }

    return detail


@router.post("/{paper_id}/save")
async def save_paper(
    paper_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Save a paper to user's library."""
    # Verify paper exists
    result = await db.execute(select(Paper).where(Paper.id == paper_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Paper not found")

    # Check if already saved
    result = await db.execute(
        select(SavedPaper).where(
            SavedPaper.user_id == user.id,
            SavedPaper.paper_id == paper_id,
        )
    )
    if result.scalar_one_or_none():
        return {"status": "already_saved"}

    saved = SavedPaper(user_id=user.id, paper_id=paper_id)
    db.add(saved)
    await db.commit()
    return {"status": "saved"}


@router.post("/{paper_id}/chat", response_model=ChatResponse)
async def chat_paper(
    paper_id: UUID,
    body: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Chat with a saved paper using RAG."""
    try:
        response = await chat_with_paper(db, user.id, paper_id, body.question)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
