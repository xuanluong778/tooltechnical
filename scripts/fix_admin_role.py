#!/usr/bin/env python3
"""Promote ADMIN_EMAIL user(s) to role=admin in DB (no password change)."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / "env.local", override=True)

import os
from sqlalchemy import text

from app.db import engine


def main() -> None:
    raw = (os.getenv("ADMIN_EMAIL") or "xuanluong778@gmail.com").strip().lower()
    emails = [e.strip().lower() for e in raw.replace(";", ",").split(",") if e.strip()]
    with engine.begin() as conn:
        for email in emails:
            before = conn.execute(
                text("SELECT id, email, role, status FROM users WHERE lower(email) = :email"),
                {"email": email},
            ).fetchone()
            print("before:", before)
            conn.execute(
                text(
                    "UPDATE users SET role = 'admin', status = 'active', "
                    "api_access_enabled = 1, use_admin_api_pool = 1 "
                    "WHERE lower(email) = :email"
                ),
                {"email": email},
            )
            after = conn.execute(
                text("SELECT id, email, role, status FROM users WHERE lower(email) = :email"),
                {"email": email},
            ).fetchone()
            print("after:", after)
    print("Done.")


if __name__ == "__main__":
    main()
