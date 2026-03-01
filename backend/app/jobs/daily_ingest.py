"""Daily paper ingestion job."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.adapters.arxiv import fetch_recent_papers as fetch_arxiv
from app.adapters.openalex import fetch_recent_works as fetch_openalex
from app.db import async_session
from app.services.ingestion import ingest_batch
from app.services.rate_limit import ingestion_limiter

logger = logging.getLogger(__name__)


async def _run_daily_ingest():
    """Fetch and ingest papers from all sources."""
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    logger.info(f"Starting daily ingest for {yesterday}")

    # Fetch from both sources (rate-limited)
    ingestion_limiter.wait_if_needed("openalex")
    openalex_papers = await fetch_openalex(from_date=yesterday, to_date=today)
    logger.info(f"Fetched {len(openalex_papers)} papers from OpenAlex")

    ingestion_limiter.wait_if_needed("arxiv")
    arxiv_papers = await fetch_arxiv()
    logger.info(f"Fetched {len(arxiv_papers)} papers from arXiv")

    all_papers = openalex_papers + arxiv_papers

    # Ingest
    async with async_session() as db:
        stats = await ingest_batch(db, all_papers)
        logger.info(f"Ingestion complete: {stats}")

    return stats


def daily_ingest_job():
    """RQ-compatible sync wrapper for the daily ingest."""
    return asyncio.run(_run_daily_ingest())
