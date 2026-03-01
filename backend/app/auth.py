"""Authentication: extract + verify Supabase JWTs (HS256 or ES256/JWKS)."""

import logging
import uuid
from typing import Optional

import httpx
from fastapi import Depends, HTTPException, Request
from jose import JWTError, jwt as jose_jwt
from jose.utils import base64url_decode
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db import get_db
from app.models import User

logger = logging.getLogger(__name__)

# ── JWKS cache ───────────────────────────────────────────────────────────────
_jwks_cache: Optional[dict] = None


def _get_jwks() -> dict:
    """Fetch and cache JWKS from Supabase."""
    global _jwks_cache
    if _jwks_cache is not None:
        return _jwks_cache

    jwks_url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
    try:
        resp = httpx.get(jwks_url, timeout=5.0)
        resp.raise_for_status()
        _jwks_cache = resp.json()
        logger.info(f"Fetched JWKS from {jwks_url}")
        return _jwks_cache
    except Exception as e:
        logger.warning(f"Could not fetch JWKS from {jwks_url}: {e}")
        return {"keys": []}


# ── Token extraction ─────────────────────────────────────────────────────────


def _extract_token(request: Request) -> str:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    return auth[7:]


# ── JWT decode ───────────────────────────────────────────────────────────────

def _peek_header(token: str) -> dict:
    """Decode the JWT header without verification."""
    try:
        return jose_jwt.get_unverified_header(token)
    except Exception:
        return {}


def _decode_jwt(token: str) -> dict:
    header = _peek_header(token)
    alg = header.get("alg", "HS256")

    # ── ES256 (JWKS) path ────────────────────────────────────────────────
    if alg == "ES256":
        try:
            import jwt as pyjwt
            from jwt import PyJWKClient

            jwks_url = f"{settings.supabase_url}/auth/v1/.well-known/jwks.json"
            jwk_client = PyJWKClient(jwks_url)
            signing_key = jwk_client.get_signing_key_from_jwt(token)

            payload = pyjwt.decode(
                token,
                signing_key.key,
                algorithms=["ES256"],
                options={"verify_aud": False},
            )
            return payload
        except Exception as e:
            logger.warning(f"ES256 JWT decode failed: {e}")
            raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

    # ── HS256 (shared secret) path ───────────────────────────────────────
    try:
        payload = jose_jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            options={"verify_aud": False},
        )
        return payload
    except JWTError as e:
        logger.warning(f"HS256 JWT decode failed: {e}")
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")


# ── Current-user dependency ──────────────────────────────────────────────────


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    token = _extract_token(request)
    payload = _decode_jwt(token)

    sub = payload.get("sub")
    email = payload.get("email", "")
    if not sub:
        raise HTTPException(status_code=401, detail="Token missing sub claim")

    user_id = uuid.UUID(sub)
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None:
        # Auto-create user on first auth
        user = User(id=user_id, email=email)
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return user
