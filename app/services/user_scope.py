"""Helpers for per-user data isolation in JSON stores and async jobs."""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException, status


def entry_user_id(entry: dict[str, Any]) -> int:
    try:
        return int(entry.get("user_id") or 0)
    except (TypeError, ValueError):
        return 0


def belongs_to_user(entry: dict[str, Any], user_id: int) -> bool:
    """Only rows with an explicit owner are visible (legacy rows without user_id are hidden)."""
    if "user_id" not in entry:
        return False
    try:
        return int(entry.get("user_id")) == int(user_id)
    except (TypeError, ValueError):
        return False


def job_owner_user_id(payload: dict[str, Any] | None) -> int:
    if not payload:
        return 0
    try:
        return int(payload.get("user_id") or 0)
    except (TypeError, ValueError):
        return 0


def assert_job_access(payload: dict[str, Any] | None, user_id: int) -> None:
    owner = job_owner_user_id(payload)
    if not owner or owner != int(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Không tìm thấy job.")
