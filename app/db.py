import os
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# PostgreSQL in production: DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/dbname
# Default remains SQLite for local / XAMPP.
_default_sqlite = "sqlite:///./app.db"
DATABASE_URL = (os.getenv("DATABASE_URL") or _default_sqlite).strip()

def _resolve_sqlite_relative_url(url: str) -> str:
    """
    Make SQLite DB path stable across uvicorn reload / different cwd.

    Without this, `sqlite:///./app.db` depends on the current working directory,
    which can differ between processes (common on Windows/Laragon), causing
    "Job not found" and other persistence issues.
    """
    if not url.startswith("sqlite:///"):
        return url
    path_part = url[len("sqlite:///") :]
    # Already absolute (Unix) or absolute Windows drive path (C:/...)
    if path_part.startswith("/") or (len(path_part) >= 3 and path_part[1:3] == ":/"):
        return url
    base_dir = Path(__file__).resolve().parents[1]  # project root (folder containing `app/`)
    abs_path = (base_dir / path_part).resolve()
    # SQLAlchemy expects forward slashes in sqlite URLs on Windows
    return "sqlite:///" + abs_path.as_posix()


if DATABASE_URL.startswith("sqlite"):
    DATABASE_URL = _resolve_sqlite_relative_url(DATABASE_URL)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
