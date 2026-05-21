from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AdminUserSummary(BaseModel):
    id: int
    email: str
    role: str
    status: str
    credit_balance: int = 0
    has_password: bool = True
    api_access_enabled: bool = False
    use_admin_api_pool: bool = False
    created_at: datetime | None = None
    account_activated: bool = False
    trial_status: str = "none"
    trial_started_at: str | None = None
    trial_ends_at: str | None = None
    trial_days_remaining: int = 0
    trial_is_active: bool = False
    trial_never_used: bool = True
    trial_message: str = ""

    model_config = {"from_attributes": True}


class AdminUserListResponse(BaseModel):
    items: list[AdminUserSummary]
    total: int


class AdminUserRoleUpdate(BaseModel):
    role: str = Field(..., description="admin | user | editor | viewer")


class AdminUserStatusUpdate(BaseModel):
    status: str = Field(..., description="active | inactive | banned")


class AdminUserApiAccessUpdate(BaseModel):
    api_access_enabled: bool | None = None
    use_admin_api_pool: bool | None = None


class AdminUserDetailResponse(BaseModel):
    user: AdminUserSummary
    seo_projects: list[dict[str, Any]]
    content_ai_projects: list[dict[str, Any]]
    knowledge_bases: list[dict[str, Any]]
    bulk_jobs: list[dict[str, Any]]
    api_keys: list[dict[str, Any]]
    publishing_sites: list[dict[str, Any]]
    trial: dict[str, Any]
    audit_logs: list[dict[str, Any]]


class AdminAuditLogRow(BaseModel):
    id: int
    user_id: int | None
    action: str
    resource_type: str
    resource_id: str
    detail_json: str
    ip_address: str
    created_at: datetime | None = None

    model_config = {"from_attributes": True}


class AdminAuditListResponse(BaseModel):
    items: list[AdminAuditLogRow]
