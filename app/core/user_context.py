"""Request-scoped user id for per-user secrets (API keys, LLM config)."""

from __future__ import annotations

from contextvars import ContextVar

_current_user_id: ContextVar[int | None] = ContextVar("current_user_id", default=None)


def get_request_user_id() -> int | None:
    return _current_user_id.get()


def bind_request_user_id(user_id: int | None):
    """Returns a token for unbind_request_user_id()."""
    return _current_user_id.set(user_id)


def unbind_request_user_id(token) -> None:
    _current_user_id.reset(token)
