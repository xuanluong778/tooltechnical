from __future__ import annotations

import base64
import os
import re
from functools import lru_cache
from pathlib import Path
from typing import Any
from uuid import uuid4

import requests
from dotenv import dotenv_values

from app.services.content_ai_project_store import get_content_ai_project, update_content_ai_project_fields


@lru_cache(maxsize=1)
def _env_map() -> dict[str, str | None]:
    env_file = Path(__file__).resolve().parents[2] / "env.local"
    return dotenv_values(env_file) if env_file.exists() else {}


def _getenv(name: str, default: str = "") -> str:
    return str((os.getenv(name) or _env_map().get(name) or default)).strip()


def _clean_label(text: str, *, max_len: int = 200) -> str:
    s = re.sub(r"\s+", " ", str(text or "").strip())
    s = re.sub(r"[|]+", " ", s)
    return s[:max_len].strip()


def build_section_image_prompt(
    *,
    title: str,
    primary_keyword: str,
    section_heading: str = "",
    section_content: str = "",
    brand_name: str = "",
    target_audience: str = "",
    industry: str = "",
    image_style: str = "",
) -> str:
    """Prompt ảnh minh họa trong bài — delegate tới build_seo_image_generation_prompt."""
    from app.services.content_image_context import (
        build_seo_image_generation_prompt,
        get_default_content_ai_image_style,
    )

    return build_seo_image_generation_prompt(
        main_keyword=primary_keyword,
        article_title=title,
        section_heading=section_heading or title,
        section_summary=section_content,
        brand_name=brand_name,
        industry=industry,
        target_audience=target_audience,
        image_style=image_style or get_default_content_ai_image_style(),
        language="vi",
        include_brand_logo=False,
    )


def build_thumbnail_prompt(*, title: str, primary_keyword: str) -> str:
    from app.services.content_image_context import (
        build_seo_image_generation_prompt,
        get_default_content_ai_image_style,
    )

    return build_seo_image_generation_prompt(
        main_keyword=primary_keyword,
        article_title=title,
        section_heading="",
        section_summary="",
        image_style=get_default_content_ai_image_style(),
        language="vi",
        include_brand_logo=False,
    )


def _save_image_bytes(data: bytes, *, stem: str = "ai-thumb") -> str:
    ext = ".png"
    if data[:3] == b"\xff\xd8\xff":
        ext = ".jpg"
    elif data[:8] == b"\x89PNG\r\n\x1a\n":
        ext = ".png"
    elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        ext = ".webp"
    safe_stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", stem).strip("-").lower() or "ai-thumb"
    target_dir = Path("static") / "uploads" / "content-ai"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_name = f"{safe_stem}-{uuid4().hex[:10]}{ext}"
    target_file = target_dir / target_name
    target_file.write_bytes(data)
    return f"/static/uploads/content-ai/{target_name}"


def _openai_generate_image_bytes(*, prompt: str) -> bytes:
    api_key = _getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Thiếu OPENAI_API_KEY trong env.local để tạo ảnh AI.")
    model = _getenv("OPENAI_IMAGE_MODEL", "gpt-image-1")
    default_size = "1536x1024" if model.startswith("gpt-image") else "1024x1024"
    size = _getenv("OPENAI_IMAGE_SIZE", default_size)
    body: dict[str, Any] = {
        "model": model,
        "prompt": prompt[:3900],
        "n": 1,
        "size": size,
    }
    try:
        r = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json=body,
            timeout=120,
        )
    except Exception as exc:
        raise ValueError(f"Không gọi được OpenAI Images: {exc}") from exc
    if r.status_code != 200:
        detail = (r.text or "")[:400]
        raise ValueError(f"OpenAI Images lỗi HTTP {r.status_code}: {detail}")
    data = r.json() if r.content else {}
    items = data.get("data") or []
    if not items:
        raise ValueError("OpenAI Images không trả về ảnh.")
    first = items[0] if isinstance(items[0], dict) else {}
    b64 = str(first.get("b64_json") or "").strip()
    if b64:
        return base64.b64decode(b64)
    url = str(first.get("url") or "").strip()
    if not url:
        raise ValueError("OpenAI Images không có URL ảnh.")
    try:
        img = requests.get(url, timeout=60, headers={"User-Agent": "Mozilla/5.0"})
    except Exception as exc:
        raise ValueError(f"Không tải ảnh từ OpenAI: {exc}") from exc
    if img.status_code != 200:
        raise ValueError(f"Không tải ảnh từ OpenAI (HTTP {img.status_code}).")
    return img.content


def generate_and_attach_project_thumbnail(project_id: str, *, user_id: int) -> dict[str, Any]:
    project = get_content_ai_project(project_id, user_id=user_id)
    if not project:
        raise ValueError("Không tìm thấy dự án.")
    title = str(project.get("title") or "").strip()
    pk = str(project.get("primary_keyword") or "").strip()
    prompt = build_thumbnail_prompt(title=title, primary_keyword=pk)
    image_bytes = _openai_generate_image_bytes(prompt=prompt)
    stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", pk or title or "thumb")[:40].strip("-") or "thumb"
    url = _save_image_bytes(image_bytes, stem=stem)
    updated = update_content_ai_project_fields(project_id, {"featured_image": url}, user_id=user_id)
    if not updated:
        raise ValueError("Không cập nhật được featured_image cho dự án.")
    return {
        "ok": True,
        "project_id": project_id,
        "featured_image": url,
        "prompt": prompt,
        "project": updated,
    }
