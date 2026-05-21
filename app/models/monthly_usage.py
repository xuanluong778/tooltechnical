"""Monthly usage rollup for fast quota checks (Phase 1 — schema only)."""

from datetime import datetime

from sqlalchemy import CHAR, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class MonthlyUsage(Base):
    __tablename__ = "monthly_usage"
    __table_args__ = (
        UniqueConstraint("user_id", "usage_month", "feature_key", name="uq_monthly_usage_user_month_feature"),
        Index("ix_monthly_usage_user_month", "user_id", "usage_month"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    subscription_id: Mapped[int | None] = mapped_column(
        ForeignKey("subscriptions.id", ondelete="SET NULL"), nullable=True
    )
    plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("plans.id", ondelete="SET NULL"), nullable=True
    )
    usage_month: Mapped[str] = mapped_column(CHAR(7), nullable=False)
    feature_key: Mapped[str] = mapped_column(String(64), nullable=False)
    quantity_used: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    credits_used: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
