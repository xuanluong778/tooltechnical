"""Admin-only SaaS Phase 1 APIs (manual test — no product enforcement)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.user import User
from app.schemas.saas import (
    AdminGrantSubscriptionBody,
    AdminTestRecordUsageBody,
    AdminTestRecordUsageResponse,
    AdminUserSubscriptionStatus,
    EntitlementResult,
    PlanListResponse,
    PlanResponse,
    SubscriptionResponse,
    UsageLimitResponse,
)
from app.services import entitlement_service, plan_service, subscription_service, usage_tracking_service
from app.services.rbac import require_admin_user
from app.services.security_audit_log import log_audit_event

router = APIRouter(prefix="/saas", tags=["admin-saas"])


def _plan_to_response(plan) -> PlanResponse:
    limits = getattr(plan, "usage_limits", None) or plan_service.get_limits_for_plan(plan.id)
    return PlanResponse(
        id=plan.id,
        slug=plan.slug,
        name=plan.name,
        description=plan.description,
        price_amount=plan.price_amount,
        currency=plan.currency,
        billing_cycle=plan.billing_cycle,
        is_active=plan.is_active,
        is_public=plan.is_public,
        sort_order=plan.sort_order,
        usage_limits=[UsageLimitResponse.model_validate(ul) for ul in limits],
    )


def _user_or_404(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == int(user_id)).one_or_none()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get("/plans", response_model=PlanListResponse)
def list_saas_plans(
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin_user),
) -> PlanListResponse:
    plans = plan_service.list_active_plans(db, public_only=False)
    items = []
    for plan in plans:
        full = plan_service.get_plan_with_limits(db, plan.id) or plan
        items.append(_plan_to_response(full))
    return PlanListResponse(items=items, total=len(items))


@router.get("/users/{user_id}/subscription", response_model=AdminUserSubscriptionStatus)
def get_user_subscription(
    user_id: int,
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin_user),
) -> AdminUserSubscriptionStatus:
    _user_or_404(db, user_id)
    sub = subscription_service.get_active_subscription(db, user_id)
    if sub is None:
        return AdminUserSubscriptionStatus(
            user_id=int(user_id),
            message="User chưa có subscription SaaS đang hiệu lực.",
        )

    plan = plan_service.get_plan_by_id(db, sub.plan_id)
    return AdminUserSubscriptionStatus(
        user_id=int(user_id),
        subscription_id=sub.id,
        plan_slug=plan.slug if plan else None,
        plan_name=plan.name if plan else None,
        status=sub.status,
        current_period_start=sub.current_period_start,
        current_period_end=sub.current_period_end,
        cancel_at_period_end=bool(sub.cancel_at_period_end),
        notes=sub.notes,
    )


@router.post("/users/{user_id}/grant-subscription", response_model=SubscriptionResponse)
def grant_user_subscription(
    user_id: int,
    payload: AdminGrantSubscriptionBody,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user),
) -> SubscriptionResponse:
    target = _user_or_404(db, user_id)
    plan = plan_service.get_plan_by_slug(db, payload.plan_slug.strip())
    if plan is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Plan slug không tồn tại: {payload.plan_slug}",
        )

    sub = subscription_service.create_subscription(
        db,
        target.id,
        plan.id,
        months=payload.months,
        status="active",
        source="manual",
        notes=payload.notes,
    )
    db.commit()
    db.refresh(sub)

    log_audit_event(
        action="admin.saas.grant_subscription",
        user_id=admin.id,
        resource_type="subscription",
        resource_id=str(sub.id),
        detail={
            "target_user_id": target.id,
            "target_email": target.email,
            "plan_slug": plan.slug,
            "months": payload.months,
        },
        request=request,
    )

    return subscription_service.subscription_to_response(db, sub)


@router.get("/users/{user_id}/entitlement-check", response_model=EntitlementResult)
def entitlement_check(
    user_id: int,
    feature_key: str = Query(..., min_length=1, max_length=64),
    quantity: int = Query(default=1, ge=1),
    db: Session = Depends(get_db),
    _admin: User = Depends(require_admin_user),
) -> EntitlementResult:
    user = _user_or_404(db, user_id)
    return entitlement_service.check_feature(db, user, feature_key, quantity=quantity)


@router.post("/users/{user_id}/usage/test-record", response_model=AdminTestRecordUsageResponse)
def test_record_usage(
    user_id: int,
    payload: AdminTestRecordUsageBody,
    request: Request,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin_user),
) -> AdminTestRecordUsageResponse:
    user = _user_or_404(db, user_id)
    sub = subscription_service.get_active_subscription(db, user.id)

    existing_id: int | None = None
    if payload.idempotency_key:
        from app.models.usage_event import UsageEvent

        row = (
            db.query(UsageEvent)
            .filter(UsageEvent.idempotency_key == payload.idempotency_key.strip()[:128])
            .one_or_none()
        )
        if row is not None:
            existing_id = row.id

    event = usage_tracking_service.record_successful_usage(
        db,
        user.id,
        payload.feature_key.strip(),
        quantity=payload.quantity,
        subscription_id=sub.id if sub else None,
        plan_id=sub.plan_id if sub else None,
        idempotency_key=payload.idempotency_key,
    )
    db.commit()

    log_audit_event(
        action="admin.saas.test_record_usage",
        user_id=admin.id,
        resource_type="usage_event",
        resource_id=str(event.id),
        detail={
            "target_user_id": user.id,
            "feature_key": payload.feature_key,
            "quantity": payload.quantity,
            "idempotency_key": payload.idempotency_key,
        },
        request=request,
    )

    qty_month = usage_tracking_service.get_monthly_usage(db, user.id, payload.feature_key.strip())
    remaining = usage_tracking_service.get_quota_remaining(
        db, user.id, payload.feature_key.strip()
    )

    return AdminTestRecordUsageResponse(
        event_id=event.id,
        idempotent_replay=existing_id is not None and existing_id == event.id,
        feature_key=payload.feature_key.strip(),
        quantity_used_month=qty_month,
        quota_remaining=remaining,
    )
