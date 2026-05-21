"""At-rest encryption for API keys, tokens, and passwords stored in JSON files."""

from __future__ import annotations

import base64
import hashlib
import os
from functools import lru_cache

from cryptography.fernet import Fernet, InvalidToken

_ENC_PREFIX = "enc:v1:"


def _master_key_bytes() -> bytes:
    raw = (os.getenv("SECRETS_MASTER_KEY") or "").strip()
    if raw:
        try:
            return base64.urlsafe_b64decode(raw.encode("ascii"))
        except Exception:
            pass
        digest = hashlib.sha256(raw.encode("utf-8")).digest()
        return base64.urlsafe_b64encode(digest)
    from app.core.security import SECRET_KEY

    digest = hashlib.sha256(f"secrets:{SECRET_KEY}".encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


@lru_cache(maxsize=1)
def _fernet() -> Fernet:
    return Fernet(_master_key_bytes())


def encrypt_secret(plain: str) -> str:
    """Encrypt a secret for persistence. Empty strings stay empty."""
    s = str(plain or "")
    if not s:
        return ""
    if s.startswith(_ENC_PREFIX):
        return s
    token = _fernet().encrypt(s.encode("utf-8")).decode("ascii")
    return f"{_ENC_PREFIX}{token}"


def decrypt_secret(stored: str) -> str:
    """Decrypt a stored secret. Legacy plaintext values pass through unchanged."""
    s = str(stored or "")
    if not s:
        return ""
    if not s.startswith(_ENC_PREFIX):
        return s
    blob = s[len(_ENC_PREFIX) :]
    try:
        return _fernet().decrypt(blob.encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError, UnicodeDecodeError):
        return ""
