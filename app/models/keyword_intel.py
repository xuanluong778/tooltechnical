"""Persistent keyword intelligence (clusters, volumes, URL mapping)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class SEOKeywordEntity(Base):
    """One normalized keyword phrase tied to a project (optional)."""

    __tablename__ = "seo_keyword_entities"
    __table_args__ = (Index("ix_seo_kw_project_norm", "project_id", "normalized_keyword"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), index=True, nullable=True)
    keyword: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_keyword: Mapped[str] = mapped_column(String(512), nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(32), nullable=False, default="page")
    page_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    search_volume: Mapped[int | None] = mapped_column(Integer, nullable=True)
    volume_source: Mapped[str | None] = mapped_column(String(24), nullable=True)
    volume_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    intent: Mapped[str | None] = mapped_column(String(32), nullable=True)
    intent_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    cluster_uid: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    details_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SEOKeywordClusterEntity(Base):
    """Topic cluster row."""

    __tablename__ = "seo_keyword_clusters"
    __table_args__ = (Index("ix_seo_kc_project_uid", "project_id", "cluster_uid"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), index=True, nullable=True)
    cluster_uid: Mapped[str] = mapped_column(String(64), nullable=False)
    cluster_name: Mapped[str] = mapped_column(String(512), nullable=False)
    dominant_intent: Mapped[str | None] = mapped_column(String(32), nullable=True)
    intent_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_search_volume: Mapped[int | None] = mapped_column(Integer, nullable=True)
    explain_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SEOKeywordUrlMapping(Base):
    """Best URL target per cluster for a project."""

    __tablename__ = "seo_keyword_url_mappings"
    __table_args__ = (Index("ix_seo_ku_project_cluster", "project_id", "cluster_uid"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), index=True, nullable=True)
    cluster_uid: Mapped[str] = mapped_column(String(64), nullable=False)
    target_url: Mapped[str] = mapped_column(Text, nullable=False)
    match_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
