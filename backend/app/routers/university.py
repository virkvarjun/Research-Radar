"""University/institution endpoints."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.models import Institution, Paper, User, UserInstitution
from app.schemas.common import InstitutionOut, PaperOut, UniversitySearchResponse
from app.adapters.openalex import search_institutions as openalex_search_institutions

router = APIRouter(prefix="/university", tags=["university"])


@router.get("/search", response_model=UniversitySearchResponse)
async def search_institutions(
    q: str = Query(..., min_length=2, description="Search query"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Search for institutions via OpenAlex."""
    results = await openalex_search_institutions(q)

    institutions = []
    for r in results:
        # Upsert institution in our DB
        result = await db.execute(
            select(Institution).where(Institution.openalex_id == r["openalex_id"])
        )
        inst = result.scalar_one_or_none()
        if not inst:
            inst = Institution(
                openalex_id=r["openalex_id"],
                name=r["name"],
                country=r.get("country"),
                ror_id=r.get("ror_id"),
            )
            db.add(inst)
            await db.flush()

        institutions.append(InstitutionOut.model_validate(inst))

    await db.commit()
    return UniversitySearchResponse(institutions=institutions)


@router.get("/{institution_id}/new", response_model=list[PaperOut])
async def get_institution_papers(
    institution_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get new papers from a specific institution."""
    # Get institution
    result = await db.execute(
        select(Institution).where(Institution.id == institution_id)
    )
    inst = result.scalar_one_or_none()
    if not inst:
        return []

    # Find papers with this institution's OpenAlex ID
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    result = await db.execute(
        select(Paper)
        .where(Paper.created_at >= cutoff)
        .order_by(Paper.published_date.desc().nullslast())
        .limit(50)
    )
    all_papers = result.scalars().all()

    # Filter by institution ID
    papers = []
    for paper in all_papers:
        inst_ids = paper.institution_ids or []
        if inst.openalex_id in inst_ids:
            papers.append(paper)

    return papers
