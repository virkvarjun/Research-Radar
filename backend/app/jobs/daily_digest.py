"""Daily digest job: rank papers per user and send email."""

import asyncio
import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import async_session
from app.models import Digest, DigestPaper, Event, Paper, User
from app.services.email import send_digest_email
from app.services.ranking import mmr_rerank, score_paper, apply_role_constraints

logger = logging.getLogger(__name__)


async def _generate_user_digest(db: AsyncSession, user: User) -> list[dict]:
    """Generate top-K papers for a user's digest."""
    # Get papers already sent or interacted with
    sent_result = await db.execute(
        select(DigestPaper.paper_id)
        .join(Digest)
        .where(Digest.user_id == user.id)
    )
    sent_ids = {row[0] for row in sent_result.fetchall()}

    event_result = await db.execute(
        select(Event.paper_id).where(
            Event.user_id == user.id,
            Event.action.in_(["not_relevant", "skip"]),
        )
    )
    skip_ids = {row[0] for row in event_result.fetchall()}
    exclude_ids = sent_ids | skip_ids

    # Get recent candidates
    cutoff = datetime.now(timezone.utc) - timedelta(days=settings.novelty_days)
    query = select(Paper).where(
        Paper.embedding.isnot(None),
        Paper.created_at >= cutoff,
    )
    if exclude_ids:
        from sqlalchemy import not_
        query = query.where(not_(Paper.id.in_(exclude_ids)))

    result = await db.execute(query.limit(100))
    candidates = result.scalars().all()

    if not candidates:
        return []

    thread_embeddings = [t.embedding for t in user.threads if t.embedding]
    now = datetime.now(timezone.utc)

    scored = []
    for paper in candidates:
        if not paper.embedding:
            continue
        days_old = max(0, (now - paper.created_at).days) if paper.created_at else 0
        score, explanation = score_paper(
            user_embedding=user.embedding,
            thread_embeddings=thread_embeddings,
            paper_embedding=paper.embedding,
            days_old=days_old,
        )
        scored.append({
            "paper": paper,
            "score": score,
            "embedding": paper.embedding,
            "title": paper.title,
            "categories": paper.categories,
            "evidence": paper.evidence,
            "why_matched": explanation,
        })

    scored = apply_role_constraints(scored, user.role)
    top = mmr_rerank(scored, settings.digest_size)

    return [
        {
            "id": str(item["paper"].id),
            "title": item["paper"].title,
            "abstract": item["paper"].abstract,
            "authors": item["paper"].authors,
        }
        for item in top
    ]


async def _run_daily_digest():
    """Generate and send digests for all eligible users."""
    async with async_session() as db:
        result = await db.execute(
            select(User).where(
                User.onboarded == True,
                User.digest_enabled == True,
                User.embedding.isnot(None),
            )
        )
        users = result.scalars().all()

        logger.info(f"Generating digests for {len(users)} users")
        sent_count = 0

        for user in users:
            try:
                papers = await _generate_user_digest(db, user)
                if not papers:
                    continue

                # Record digest
                digest = Digest(user_id=user.id)
                db.add(digest)
                await db.flush()

                for i, p in enumerate(papers):
                    dp = DigestPaper(
                        digest_id=digest.id,
                        paper_id=UUID(p["id"]),
                        rank=i + 1,
                    )
                    db.add(dp)

                # Send email
                success = await send_digest_email(user.email, papers, user.id)
                if success:
                    sent_count += 1

            except Exception as e:
                logger.error(f"Error generating digest for user {user.id}: {e}")

        await db.commit()
        logger.info(f"Daily digest complete: {sent_count}/{len(users)} emails sent")
        return {"users": len(users), "sent": sent_count}


def daily_digest_job():
    """RQ-compatible sync wrapper."""
    return asyncio.run(_run_daily_digest())
