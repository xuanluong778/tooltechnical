"""User-facing SaaS read APIs (Phase 1c — no enforcement)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.schemas.saas import SaasMeResponse
from app.services.auth import get_current_user
from app.services.saas_user_service import build_saas_me_response

router = APIRouter(prefix="/saas", tags=["saas"])


@router.get("/me", response_model=SaasMeResponse)
def saas_me(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SaasMeResponse:
    """Current user's plan, subscription period, and monthly quotas (read-only)."""
    return build_saas_me_response(db, current_user)
