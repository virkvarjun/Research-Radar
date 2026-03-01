"""University/institution endpoints."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, not_
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.models import Institution, Paper, User, UserInstitution
from app.schemas.common import InstitutionOut, PaperOut, UniversitySearchResponse
from app.adapters.openalex import search_institutions as openalex_search_institutions
from app.services.embeddings import cosine_similarity

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


@router.get("/{institution_id}/related", response_model=list[PaperOut])
async def get_related_papers(
    institution_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get papers from elsewhere that are related to the institution's works + user threads.

    Uses cosine similarity between (user threads + institution paper embeddings)
    and all other papers to find relevant work from other institutions.
    """
    # Get institution
    result = await db.execute(
        select(Institution).where(Institution.id == institution_id)
    )
    inst = result.scalar_one_or_none()
    if not inst:
        return []

    # Find institution papers to use as query vectors
    cutoff = datetime.now(timezone.utc) - timedelta(days=30)
    result = await db.execute(
        select(Paper)
        .where(Paper.embedding.isnot(None), Paper.created_at >= cutoff)
        .order_by(Paper.published_date.desc().nullslast())
        .limit(200)
    )
    all_papers = result.scalars().all()

    # Split into institution papers and others
    inst_papers = []
    other_papers = []
    for paper in all_papers:
        inst_ids = paper.institution_ids or []
        if inst.openalex_id in inst_ids:
            inst_papers.append(paper)
        else:
            other_papers.append(paper)

    if not other_papers:
        return []

    # Build query vectors: institution paper embeddings + user thread embeddings
    query_vectors = []
    for p in inst_papers:
        if p.embedding is not None:
            query_vectors.append(p.embedding)
    for thread in user.threads:
        if thread.embedding is not None:
            query_vectors.append(thread.embedding)

    if not query_vectors:
        # No vectors to compare against — return recent papers from elsewhere
        return [PaperOut.model_validate(p) for p in other_papers[:20]]

    # Score each other paper by max similarity to any query vector
    scored = []
    for paper in other_papers:
        if paper.embedding is None:
            continue
        max_sim = max(
            cosine_similarity(qv, paper.embedding) for qv in query_vectors
        )
        scored.append((paper, max_sim))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [PaperOut.model_validate(p) for p, _ in scored[:20]]
