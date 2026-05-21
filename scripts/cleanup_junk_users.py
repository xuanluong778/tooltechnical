#!/usr/bin/env python3
"""
Xóa user rác (test @example.com, …) — chỉ giữ Gmail thật + ADMIN_EMAIL.

Usage:
  python scripts/cleanup_junk_users.py          # dry-run (mặc định)
  python scripts/cleanup_junk_users.py --apply  # thực hiện xóa
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / "env.local", override=True)

from sqlalchemy import text

from app.db import SessionLocal, engine
from app.models import knowledge as _km  # noqa: F401
from app.models import seo as _sm  # noqa: F401
from app.models.user import User
from app.services.user_account_policy import is_retained_user_email, retained_user_emails


def _delete_user_data(conn, user_id: int) -> None:
    """Xóa dữ liệu liên quan trước khi xóa user (SQLite FK)."""
    tables = [
        "trial_key_claims",
        "user_trials",
        "user_api_keys",
        "credit_ledger",
        "keyword_cluster_projects",
        "keyword_research_projects",
        "keyword_cluster_jobs",
        "projects",
    ]
    for tbl in tables:
        try:
            conn.execute(text(f"DELETE FROM {tbl} WHERE user_id = :uid"), {"uid": user_id})
        except Exception:
            pass
    try:
        conn.execute(
            text("DELETE FROM security_audit_logs WHERE user_id = :uid"),
            {"uid": user_id},
        )
    except Exception:
        pass
    try:
        conn.execute(text("DELETE FROM knowledge_bases WHERE user_id = :uid"), {"uid": user_id})
    except Exception:
        pass


def main() -> None:
    parser = argparse.ArgumentParser(description="Cleanup junk users — keep real Gmail only")
    parser.add_argument("--apply", action="store_true", help="Thực hiện xóa (mặc định: chỉ xem trước)")
    args = parser.parse_args()

    keep = retained_user_emails()

    db = SessionLocal()
    try:
        users = db.query(User).order_by(User.id).all()
        to_keep = [u for u in users if is_retained_user_email(u.email)]
        to_delete = [u for u in users if not is_retained_user_email(u.email)]

        print(f"Total users in DB: {len(users)}")
        print(f"Keep ({len(to_keep)}):")
        for u in to_keep:
            print(f"  [KEEP] id={u.id} {u.email} role={u.role}")

        print(f"\nDelete ({len(to_delete)}):")
        for u in to_delete[:30]:
            print(f"  [DEL]  id={u.id} {u.email}")
        if len(to_delete) > 30:
            print(f"  ... and {len(to_delete) - 30} more")

        if not args.apply:
            print("\nRe-run with --apply to delete.")
            return

        if not to_delete:
            print("No junk users to delete.")
            return

        with engine.begin() as conn:
            for u in to_delete:
                _delete_user_data(conn, u.id)
                conn.execute(text("DELETE FROM users WHERE id = :uid"), {"uid": u.id})
        print(f"\nDeleted {len(to_delete)} junk users. Remaining: {len(to_keep)}.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
