"""Pydantic schemas for SaaS Phase 1 (plans, subscriptions, entitlements)."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class UsageLimitResponse(BaseModel):
    id: int
    plan_id: int
    feature_key: str
    limit_value: int
    period: str
    is_hard_limit: bool

    model_config = {"from_attributes": True}


class PlanResponse(BaseModel):
    id: int
    slug: str
    name: str
    description: str | None = None
    price_amount: int
    currency: str
    billing_cycle: str
    is_active: bool
    is_public: bool
    sort_order: int
    usage_limits: list[UsageLimitResponse] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class SubscriptionResponse(BaseModel):
    id: int
    user_id: int
    plan_id: int
    status: str
    started_at: datetime
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
    cancelled_at: datetime | None = None
    ended_at: datetime | None = None
    source: str
    notes: str | None = None
    plan_slug: str | None = None
    plan_name: str | None = None

    model_config = {"from_attributes": True}


class UserPlanSnapshot(BaseModel):
    user_id: int
    has_active_subscription: bool
    subscription: SubscriptionResponse | None = None
    plan: PlanResponse | None = None
    effective_plan_slug: str | None = None


class EntitlementResult(BaseModel):
    allowed: bool
    reason_code: str
    message: str
    plan_slug: str | None = None
    subscription_id: int | None = None
    quota_remaining: int | None = None
    feature_key: str


class GrantSubscriptionRequest(BaseModel):
    user_id: int
    plan_id: int
    months: int = Field(default=1, ge=1, le=36)
    status: str = Field(default="active", description="active | trialing")
    source: str = "manual"
    notes: str | None = None


class RecordUsageRequest(BaseModel):
    user_id: int
    feature_key: str
    quantity: int = Field(default=1, ge=1)
    subscription_id: int | None = None
    plan_id: int | None = None
    credits_used: int = Field(default=0, ge=0)
    idempotency_key: str | None = None
    metadata: dict[str, Any] | None = None


class AdminGrantSubscriptionBody(BaseModel):
    plan_slug: str = Field(..., min_length=1, max_length=64)
    months: int = Field(default=1, ge=1, le=36)
    notes: str | None = None


class AdminTestRecordUsageBody(BaseModel):
    feature_key: str = Field(..., min_length=1, max_length=64)
    quantity: int = Field(default=1, ge=1)
    idempotency_key: str | None = Field(default=None, max_length=128)


class AdminUserSubscriptionStatus(BaseModel):
    user_id: int
    subscription_id: int | None = None
    plan_slug: str | None = None
    plan_name: str | None = None
    status: str | None = None
    current_period_start: datetime | None = None
    current_period_end: datetime | None = None
    cancel_at_period_end: bool | None = None
    notes: str | None = None
    message: str | None = None


class AdminTestRecordUsageResponse(BaseModel):
    ok: bool = True
    event_id: int
    idempotent_replay: bool = False
    feature_key: str
    quantity_used_month: int
    quota_remaining: int | None = None


class PlanListResponse(BaseModel):
    items: list[PlanResponse]
    total: int


class MonthlyUsageRow(BaseModel):
    feature_key: str
    quantity_used: int
    credits_used: int = 0
    limit_value: int | None = None
    quota_remaining: int | None = None
    period: str | None = None


class AdminUserUsageResponse(BaseModel):
    user_id: int
    usage_month: str
    plan_slug: str | None = None
    subscription_id: int | None = None
    items: list[MonthlyUsageRow] = Field(default_factory=list)
    message: str | None = None
