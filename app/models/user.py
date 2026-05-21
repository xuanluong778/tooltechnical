from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    has_password: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("1"))
    credit_balance: Mapped[int] = mapped_column(Integer, nullable=False, server_default=text("0"))
    role: Mapped[str] = mapped_column(String(32), nullable=False, server_default=text("'user'"), default="user")
    status: Mapped[str] = mapped_column(String(16), nullable=False, server_default=text("'active'"), default="active")
    api_access_enabled: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("0"), default=False
    )
    use_admin_api_pool: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default=text("0"), default=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    projects: Mapped[list["Project"]] = relationship("Project", backref="user", cascade="all, delete-orphan")
    knowledge_bases: Mapped[list["KnowledgeBase"]] = relationship(
        "KnowledgeBase",
        back_populates="user",
        foreign_keys="KnowledgeBase.user_id",
        cascade="all, delete-orphan",
    )
