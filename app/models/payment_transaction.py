"""Payment records — Phase 1 schema only; no gateway integration yet."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text, UniqueConstraint, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    __table_args__ = (
        Index("ix_payment_transactions_user_id", "user_id"),
        Index("ix_payment_transactions_status", "status"),
        UniqueConstraint(
            "provider",
            "provider_transaction_id",
            name="uq_payment_provider_tx",
        ),
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
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, server_default=text("'VND'"))
    status: Mapped[str] = mapped_column(String(24), nullable=False, server_default=text("'pending'"))
    provider: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'manual'"))
    provider_transaction_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    provider_payload_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    paid_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
