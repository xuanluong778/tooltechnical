from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.services.rbac import normalize_role
from app.services.user_scope import belongs_to_user, entry_user_id

KB_FILE = Path("data/ai_knowledge_bases.json")
SCOPES = frozenset({"user", "global"})
MAX_BASES = 50

TONES = {
    "professional": "Chuyên nghiệp",
    "friendly": "Thân thiện",
    "expert": "Chuyên gia / uy tín",
    "casual": "Gần gũi, đời thường",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_all() -> list[dict[str, Any]]:
    if not KB_FILE.exists():
        return []
    try:
        raw = json.loads(KB_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(raw, list):
        return []
    return [x for x in raw if isinstance(x, dict)]


def _write_all(items: list[dict[str, Any]]) -> None:
    KB_FILE.parent.mkdir(parents=True, exist_ok=True)
    KB_FILE.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


def _norm_url(url: str) -> str:
    s = str(url or "").strip()
    if not s:
        return ""
    if not s.lower().startswith(("http://", "https://")):
        s = "https://" + s
    return s.rstrip("/")


def _normalize(entry: dict[str, Any]) -> dict[str, Any]:
    tone = str(entry.get("tone") or "professional").strip().lower()
    if tone not in TONES:
        tone = "professional"
    lang = str(entry.get("language") or "vi").strip().lower()[:8] or "vi"
    scope = str(entry.get("scope") or "user").strip().lower()
    if scope not in SCOPES:
        scope = "user"
    uid = entry_user_id(entry) if scope == "user" else 0
    return {
        "id": str(entry.get("id") or uuid.uuid4()),
        "user_id": uid,
        "scope": scope,
        "name": str(entry.get("name") or "").strip(),
        "brand_name": str(entry.get("brand_name") or "").strip(),
        "website_url": _norm_url(entry.get("website_url") or ""),
        "tone": tone,
        "tone_label": TONES[tone],
        "language": lang,
        "products_services": str(entry.get("products_services") or "").strip(),
        "target_audience": str(entry.get("target_audience") or "").strip(),
        "key_facts": str(entry.get("key_facts") or "").strip(),
        "avoid_topics": str(entry.get("avoid_topics") or "").strip(),
        "custom_instructions": str(entry.get("custom_instructions") or "").strip(),
        "enabled": bool(entry.get("enabled", True)),
        "is_default": bool(entry.get("is_default", False)),
        "created_at": str(entry.get("created_at") or _now()),
        "updated_at": str(entry.get("updated_at") or _now()),
    }


def _public(entry: dict[str, Any], *, can_edit: bool | None = None) -> dict[str, Any]:
    row = dict(entry)
    row["tone_label"] = TONES.get(row.get("tone") or "", row.get("tone") or "")
    if can_edit is not None:
        row["can_edit"] = bool(can_edit)
    return row


def _readable(entry: dict[str, Any], user_id: int) -> bool:
    row = _normalize(entry)
    if row.get("scope") == "global":
        return True
    return belongs_to_user(entry, user_id)


def _writable(entry: dict[str, Any], user_id: int, role: str) -> bool:
    row = _normalize(entry)
    if row.get("scope") == "global":
        return normalize_role(role) == "admin"
    return belongs_to_user(entry, user_id)


def _writable_or_raise(entry: dict[str, Any], user_id: int, role: str) -> None:
    if _writable(entry, user_id, role):
        return
    row = _normalize(entry)
    if row.get("scope") == "global":
        raise PermissionError("Knowledge Base toàn cục (Global) chỉ tài khoản admin mới được sửa hoặc xóa.")
    raise PermissionError("Bạn không có quyền sửa Knowledge Base này.")


def list_bases(*, user_id: int, role: str = "user") -> list[dict[str, Any]]:
    r = normalize_role(role)
    items = [_normalize(x) for x in _read_all() if _readable(x, user_id)]
    items.sort(key=lambda x: (x.get("scope") != "user", not x.get("is_default"), x.get("name", "").lower()))
    return [_public(x, can_edit=_writable(x, user_id, r)) for x in items]


def get_base(kb_id: str, *, user_id: int, role: str = "user") -> dict[str, Any] | None:
    kid = str(kb_id or "").strip()
    if not kid:
        return None
    r = normalize_role(role)
    for raw in _read_all():
        if str(raw.get("id")) == kid and _readable(raw, user_id):
            return _public(_normalize(raw), can_edit=_writable(raw, user_id, r))
    return None


def get_default_base(*, user_id: int) -> dict[str, Any] | None:
    for item in list_bases(user_id=user_id):
        if item.get("enabled") and item.get("is_default"):
            return item
    for item in list_bases(user_id=user_id):
        if item.get("enabled"):
            return item
    return None


def create_base(payload: dict[str, Any], *, user_id: int, role: str = "user") -> dict[str, Any]:
    scope = str(payload.get("scope") or "user").strip().lower()
    if scope == "global" and normalize_role(role) != "admin":
        raise ValueError("Chỉ admin mới tạo knowledge base toàn cục.")
    items = [_normalize(x) for x in _read_all() if belongs_to_user(x, user_id) and _normalize(x).get("scope") == "user"]
    if scope != "global" and len(items) >= MAX_BASES:
        raise ValueError(f"Tối đa {MAX_BASES} knowledge base.")
    row = _normalize(
        {
            **payload,
            "id": uuid.uuid4(),
            "user_id": 0 if scope == "global" else int(user_id),
            "scope": scope,
            "created_at": _now(),
            "updated_at": _now(),
        }
    )
    if not row["name"]:
        raise ValueError("Cần đặt tên knowledge base.")
    if row["is_default"]:
        for it in items:
            it["is_default"] = False
    elif not items:
        row["is_default"] = True
    all_items = _read_all()
    all_items.append(row)
    _write_all(all_items)
    return _public(row)


def update_base(kb_id: str, payload: dict[str, Any], *, user_id: int, role: str = "user") -> dict[str, Any] | None:
    kid = str(kb_id or "").strip()
    if not kid:
        return None
    items = _read_all()
    found: dict[str, Any] | None = None
    for i, it in enumerate(items):
        if str(it.get("id")) != kid:
            continue
        _writable_or_raise(it, user_id, role)
        merged = {**it, **{k: v for k, v in payload.items() if v is not None}}
        merged["id"] = kid
        merged["updated_at"] = _now()
        row = _normalize(merged)
        if not row["name"]:
            raise ValueError("Cần đặt tên knowledge base.")
        if payload.get("is_default") is True:
            for j, other in enumerate(items):
                if j == i or not belongs_to_user(other, user_id):
                    continue
                other["is_default"] = False
        items[i] = _normalize(row)
        found = _public(items[i])
        break
    if not found:
        return None
    _write_all(items)
    return found


def delete_base(kb_id: str, *, user_id: int, role: str = "user") -> bool:
    kid = str(kb_id or "").strip()
    if not kid:
        return False
    items = _read_all()
    deleted = False
    new_items: list[dict[str, Any]] = []
    for x in items:
        if str(x.get("id")) == kid:
            _writable_or_raise(x, user_id, role)
            deleted = True
            continue
        new_items.append(x)
    if not deleted:
        return False
    user_items = [x for x in new_items if belongs_to_user(x, user_id)]
    if user_items and not any(x.get("is_default") for x in user_items):
        for x in new_items:
            if belongs_to_user(x, user_id):
                x["is_default"] = True
                x["updated_at"] = _now()
                break
    _write_all(new_items)
    try:
        from app.services.ai_knowledge_docs import delete_kb_docs

        delete_kb_docs(kid)
    except Exception:
        pass
    return True
