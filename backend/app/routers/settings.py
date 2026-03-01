"""User settings endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import get_current_user
from app.db import get_db
from app.models import Institution, User, UserInstitution
from app.schemas.common import InstitutionOut, UpdateSettings, UserSettings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=UserSettings)
async def get_settings(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current user settings."""
    institutions = []
    for ui in user.institutions:
        result = await db.execute(
            select(Institution).where(Institution.id == ui.institution_id)
        )
        inst = result.scalar_one_or_none()
        if inst:
            institutions.append(InstitutionOut.model_validate(inst))

    return UserSettings(
        role=user.role,
        topics=user.topics,
        digest_enabled=user.digest_enabled,
        institutions=institutions,
    )


@router.post("")
async def update_settings(
    body: UpdateSettings,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update user settings."""
    if body.role is not None:
        user.role = body.role
    if body.topics is not None:
        user.topics = body.topics
    if body.digest_enabled is not None:
        user.digest_enabled = body.digest_enabled

    if body.institution_ids is not None:
        # Clear existing and set new
        for ui in user.institutions:
            await db.delete(ui)
        for inst_id in body.institution_ids:
            ui = UserInstitution(user_id=user.id, institution_id=inst_id)
            db.add(ui)

    await db.commit()
    return {"status": "ok"}
