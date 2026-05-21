from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt


SECRET_KEY = "change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except ValueError:
        return False


def create_access_token(user_id: int, expires_hours: int = ACCESS_TOKEN_EXPIRE_HOURS) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=expires_hours)
    payload = {"user_id": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid token") from exc


def create_google_oauth_state(user_id: int) -> str:
    """State chống CSRF cho luồng OAuth Google (GSC + GA)."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    payload = {"google_oauth": True, "user_id": user_id, "exp": expire}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_google_oauth_state(state: str) -> int:
    try:
        data = jwt.decode(state, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError as exc:
        raise ValueError("Invalid oauth state") from exc
    if not data.get("google_oauth"):
        raise ValueError("Invalid oauth state")
    return int(data["user_id"])
