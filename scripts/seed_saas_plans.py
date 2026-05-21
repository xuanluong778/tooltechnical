#!/usr/bin/env python3
"""Seed SaaS plans + usage_limits (Phase 1 — idempotent, no enforcement)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / "env.local", override=True)

from app.db import SessionLocal
from app.models.plan import Plan
from app.models.subscription import Subscription  # noqa: F401 — resolve Plan.subscriptions
from app.models.usage_limit import UsageLimit

PLANS: list[dict[str, Any]] = [
    {
        "slug": "free_trial",
        "name": "Free Trial",
        "price_amount": 0,
        "currency": "VND",
        "billing_cycle": "none",
        "is_active": True,
        "is_public": True,
        "sort_order": 1,
    },
    {
        "slug": "starter",
        "name": "Starter",
        "price_amount": 199_000,
        "currency": "VND",
        "billing_cycle": "monthly",
        "is_active": True,
        "is_public": True,
        "sort_order": 2,
    },
    {
        "slug": "pro",
        "name": "Pro",
        "price_amount": 499_000,
        "currency": "VND",
        "billing_cycle": "monthly",
        "is_active": True,
        "is_public": True,
        "sort_order": 3,
    },
    {
        "slug": "agency",
        "name": "Agency",
        "price_amount": 1_499_000,
        "currency": "VND",
        "billing_cycle": "monthly",
        "is_active": True,
        "is_public": True,
        "sort_order": 4,
    },
]

# (plan_slug, feature_key, limit_value, period, is_hard_limit)
USAGE_LIMITS: list[tuple[str, str, int, str, bool]] = [
    ("free_trial", "content_ai_article", 3, "monthly", True),
    ("free_trial", "technical_audit", 3, "monthly", True),
    ("free_trial", "keyword_research", 50, "monthly", True),
    ("free_trial", "content_ai_bulk_article", 0, "monthly", True),
    ("starter", "content_ai_article", 30, "monthly", True),
    ("pro", "content_ai_article", 150, "monthly", True),
    ("agency", "content_ai_article", -1, "monthly", True),
]

PLAN_FIELDS = (
    "name",
    "price_amount",
    "currency",
    "billing_cycle",
    "is_active",
    "is_public",
    "sort_order",
)
LIMIT_FIELDS = ("limit_value", "period", "is_hard_limit")


def _upsert_plan(db, data: dict[str, Any]) -> tuple[Plan, str]:
    slug = data["slug"]
    plan = db.query(Plan).filter(Plan.slug == slug).one_or_none()
    if plan is None:
        plan = Plan(slug=slug, **{k: data[k] for k in PLAN_FIELDS})
        db.add(plan)
        db.flush()
        return plan, "created"
    changed = False
    for key in PLAN_FIELDS:
        if getattr(plan, key) != data[key]:
            setattr(plan, key, data[key])
            changed = True
    return plan, "updated" if changed else "unchanged"


def _upsert_usage_limit(
    db,
    plan_id: int,
    feature_key: str,
    limit_value: int,
    period: str,
    is_hard_limit: bool,
) -> str:
    row = (
        db.query(UsageLimit)
        .filter(
            UsageLimit.plan_id == plan_id,
            UsageLimit.feature_key == feature_key,
            UsageLimit.period == period,
        )
        .one_or_none()
    )
    if row is None:
        db.add(
            UsageLimit(
                plan_id=plan_id,
                feature_key=feature_key,
                limit_value=limit_value,
                period=period,
                is_hard_limit=is_hard_limit,
            )
        )
        return "created"
    changed = False
    for key, val in (
        ("limit_value", limit_value),
        ("period", period),
        ("is_hard_limit", is_hard_limit),
    ):
        if getattr(row, key) != val:
            setattr(row, key, val)
            changed = True
    return "updated" if changed else "unchanged"


def main() -> None:
    db = SessionLocal()
    try:
        plans_by_slug: dict[str, Plan] = {}
        print("Plans:")
        for data in PLANS:
            plan, status = _upsert_plan(db, data)
            plans_by_slug[data["slug"]] = plan
            print(f"  {data['slug']}: {status}")

        print("Usage limits:")
        for plan_slug, feature_key, limit_value, period, is_hard_limit in USAGE_LIMITS:
            plan = plans_by_slug[plan_slug]
            status = _upsert_usage_limit(
                db, plan.id, feature_key, limit_value, period, is_hard_limit
            )
            print(f"  {plan_slug}/{feature_key}/{period}: {status}")

        db.commit()
        print("OK — seed_saas_plans completed (idempotent).")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
