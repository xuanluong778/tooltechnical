"""
Ensure Knowledge Base tables exist (additive; does not touch JSON legacy store).

Called after model import + Base.metadata.create_all in main.py.
"""

from __future__ import annotations

from sqlalchemy import inspect

from app.db import Base, engine

KNOWLEDGE_TABLES = (
    "knowledge_bases",
    "knowledge_categories",
    "knowledge_items",
    "knowledge_embeddings",
    "knowledge_versions",
)


def ensure_knowledge_tables() -> dict[str, bool]:
    """
    create_all only creates missing tables; existing tables/columns are unchanged.
    Returns {table_name: exists_after_call}.
    """
    # Import full model graph so FK targets (users, projects) resolve.
    from app.models import knowledge  # noqa: F401
    from app.models import seo  # noqa: F401
    from app.models.user import User  # noqa: F401

    Base.metadata.create_all(bind=engine)
    insp = inspect(engine)
    names = set(insp.get_table_names())
    return {name: name in names for name in KNOWLEDGE_TABLES}


def list_knowledge_table_columns(table: str) -> list[str]:
    insp = inspect(engine)
    if table not in insp.get_table_names():
        return []
    return [c["name"] for c in insp.get_columns(table)]
