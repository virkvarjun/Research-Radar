"""Paper ingestion and deduplication service."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.openalex import title_hash
from app.models import Paper
from app.schemas.common import NormalizedPaper
from app.services.embeddings import embed_text, paper_text_for_embedding

logger = logging.getLogger(__name__)


async def deduplicate_paper(db: AsyncSession, paper: NormalizedPaper) -> Optional[Paper]:
    """Check if paper already exists. Returns existing Paper or None."""
    # 1. Check DOI
    if paper.doi:
        result = await db.execute(select(Paper).where(Paper.doi == paper.doi))
        existing = result.scalar_one_or_none()
        if existing:
            return existing

    # 2. Check arXiv ID
    if paper.arxiv_id:
        result = await db.execute(select(Paper).where(Paper.arxiv_id == paper.arxiv_id))
        existing = result.scalar_one_or_none()
        if existing:
            return existing

    # 3. Check title hash
    t_hash = title_hash(paper.title)
    result = await db.execute(select(Paper).where(Paper.title_hash == t_hash))
    existing = result.scalar_one_or_none()
    if existing:
        return existing

    return None


async def ingest_paper(
    db: AsyncSession,
    paper: NormalizedPaper,
    compute_embedding: bool = True,
) -> tuple[Paper, bool]:
    """Ingest a normalized paper. Returns (Paper, is_new).

    Deduplicates, creates if new, optionally computes embedding.
    """
    existing = await deduplicate_paper(db, paper)
    if existing:
        return existing, False

    t_hash = title_hash(paper.title)
    embedding = None
    if compute_embedding:
        text = paper_text_for_embedding(paper.title, paper.abstract)
        embedding = await embed_text(text)

    db_paper = Paper(
        title=paper.title,
        abstract=paper.abstract,
        authors=paper.authors,
        doi=paper.doi,
        arxiv_id=paper.arxiv_id,
        openalex_id=paper.openalex_id,
        title_hash=t_hash,
        source=paper.source,
        pdf_url=paper.pdf_url,
        published_date=paper.published_date,
        categories=paper.categories,
        institution_ids=paper.institution_ids,
        embedding=embedding,
    )
    db.add(db_paper)
    await db.flush()
    return db_paper, True


async def ingest_batch(
    db: AsyncSession,
    papers: list[NormalizedPaper],
    compute_embedding: bool = True,
) -> dict:
    """Ingest a batch of papers. Returns stats dict."""
    stats = {"total": len(papers), "new": 0, "duplicate": 0, "errors": 0}

    for paper in papers:
        try:
            _, is_new = await ingest_paper(db, paper, compute_embedding=compute_embedding)
            if is_new:
                stats["new"] += 1
            else:
                stats["duplicate"] += 1
        except Exception as e:
            logger.error(f"Error ingesting paper '{paper.title[:50]}': {e}")
            stats["errors"] += 1

    await db.commit()
    return stats
