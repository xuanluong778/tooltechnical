from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class SecurityAuditLog(Base):
    __tablename__ = "security_audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True)
    action: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    resource_id: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    detail_json: Mapped[str] = mapped_column(Text, default="", nullable=False)
    ip_address: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
