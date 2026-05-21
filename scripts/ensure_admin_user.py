#!/usr/bin/env python3
"""Tạo hoặc cập nhật tài khoản admin (email + mật khẩu, không OTP)."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / "env.local", override=True)

from app.core.security import hash_password
from app.db import SessionLocal
from app.models import knowledge as _knowledge_models  # noqa: F401
from app.models import seo as _seo_models  # noqa: F401
from app.models.user import User
from app.services.admin_auth import admin_emails_from_env, ensure_admin_user_fields


def main() -> None:
    email = (os.getenv("ADMIN_EMAIL") or "xuanluong778@gmail.com").strip().lower()
    password = (os.getenv("ADMIN_BOOTSTRAP_PASSWORD") or "").strip()
    if len(sys.argv) >= 2:
        email = sys.argv[1].strip().lower()
    if len(sys.argv) >= 3:
        password = sys.argv[2]
    if not password:
        print("Usage: python scripts/ensure_admin_user.py [email] [password]")
        print("Or set ADMIN_BOOTSTRAP_PASSWORD in env.local")
        sys.exit(1)

    configured = admin_emails_from_env()
    if configured and email not in configured:
        print(f"Warning: {email} not in ADMIN_EMAIL={configured}")

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.password_hash = hash_password(password)
            user.has_password = True
            ensure_admin_user_fields(user)
            db.commit()
            print(f"Updated admin user id={user.id} email={email}")
        else:
            user = User(
                email=email,
                password_hash=hash_password(password),
                has_password=True,
            )
            ensure_admin_user_fields(user)
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created admin user id={user.id} email={email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
