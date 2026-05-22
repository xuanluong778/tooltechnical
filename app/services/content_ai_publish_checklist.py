"""
Checklist SEO trước publish — chạy heuristic trên server, không nhúng vào HTML bài.
"""

from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urlparse

from bs4 import BeautifulSoup

_CHECKLIST_SECTION_RE = re.compile(
    r"checklist\s*seo|checklist\s*trước\s*khi\s*publish|kiểm\s*tra\s*trước\s*khi\s*publish",
    re.I,
)
_KW_TOKEN_RE = re.compile(r"[a-zà-ỹ0-9]+", re.I)
_INTERNAL_HINT_RE = re.compile(r"<!--\s*internal\s*:", re.I)
_GENERIC_ALT_RE = re.compile(r"^(image|img|ảnh|photo|hình|picture|pic)$", re.I)


def _tokens(s: str) -> list[str]:
    return [t for t in _KW_TOKEN_RE.findall((s or "").lower()) if len(t) > 2]


def _kw_in_text(text: str, kw: str) -> bool:
    k = (kw or "").strip().lower()
    if not k:
        return True
    t = (text or "").lower()
    if k in t:
        return True
    parts = _tokens(kw)
    if len(parts) >= 2:
        return all(p in t for p in parts[: min(4, len(parts))])
    return any(p in t for p in parts[:3]) if parts else False


def strip_publish_checklist_from_html(html: str) -> str:
    """Gỡ section Checklist SEO khỏi body bài (LLM đôi khi vẫn sinh ra)."""
    raw = str(html or "").strip()
    if not raw:
        return raw
    try:
        soup = BeautifulSoup(raw[:800_000], "html.parser")
    except Exception:
        return raw
    removed = False
    for h2 in list(soup.find_all("h2")):
        label = h2.get_text(" ", strip=True)
        if not _CHECKLIST_SECTION_RE.search(label):
            continue
        node = h2
        while node is not None:
            nxt = node.next_sibling
            try:
                node.decompose()
                removed = True
            except Exception:
                pass
            if nxt is None:
                break
            if getattr(nxt, "name", None) in ("h1", "h2"):
                break
            node = nxt
    if not removed:
        return raw
    out = str(soup).strip()
    return out or raw


def _item(
    item_id: str,
    label: str,
    status: str,
    detail: str,
) -> dict[str, str]:
    return {
        "id": item_id,
        "label": label,
        "status": status,
        "detail": detail[:400],
    }


def evaluate_publish_checklist(
    *,
    title: str = "",
    meta_description: str = "",
    content_html: str = "",
    primary_keyword: str = "",
) -> dict[str, Any]:
    """6 mục checklist chuẩn Content AI — kết quả chỉ dùng UI, không ghi vào bài."""
    pk = (primary_keyword or "").strip()
    title_s = (title or "").strip()
    meta_s = (meta_description or "").strip()
    from app.services.content_table_format import enhance_tables_in_html

    html = enhance_tables_in_html(strip_publish_checklist_from_html(content_html or ""))

    try:
        soup = BeautifulSoup(html[:800_000], "html.parser")
    except Exception:
        soup = BeautifulSoup("", "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    body_text = soup.get_text(" ", strip=True)
    words = re.findall(r"[\wà-ỹ]+", body_text, re.I)
    word_n = max(len(words), 1)

    # 1) Title + meta có từ khóa chính
    title_ok = _kw_in_text(title_s, pk) if pk else bool(title_s)
    meta_ok = _kw_in_text(meta_s, pk) if pk else bool(meta_s)
    if not pk:
        t1_status, t1_detail = "warn", "Chưa có từ khóa chính để đối chiếu."
    elif title_ok and meta_ok:
        t1_status, t1_detail = "ok", "Tiêu đề và meta description đều chứa từ khóa chính (hoặc cụm tương đương)."
    elif title_ok or meta_ok:
        t1_status, t1_detail = "warn", (
            "Chỉ "
            + ("tiêu đề" if title_ok else "meta")
            + " có từ khóa; bổ sung vào "
            + ("meta description" if title_ok else "tiêu đề")
            + "."
        )
    else:
        t1_status, t1_detail = "fail", "Tiêu đề và meta chưa thấy từ khóa chính."

    # 2) Không nhồi từ khóa
    if not pk:
        t2_status, t2_detail = "warn", "Chưa có từ khóa chính."
    else:
        pk_low = pk.lower()
        exact = len(re.findall(re.escape(pk_low), body_text.lower()))
        density = (exact / word_n) * 100.0
        if exact == 0:
            t2_status, t2_detail = "warn", "Từ khóa chính chưa xuất hiện trong thân bài."
        elif density > 4.5 or exact > max(12, word_n // 80):
            t2_status, t2_detail = (
                "fail",
                f"Có thể nhồi từ khóa (~{exact} lần, ~{density:.1f}% mật độ). Rải tự nhiên hơn.",
            )
        elif density > 2.8 or exact > max(8, word_n // 120):
            t2_status, t2_detail = (
                "warn",
                f"Mật độ từ khóa hơi cao ({exact} lần). Kiểm tra lại câu chữ.",
            )
        else:
            t2_status, t2_detail = "ok", f"Mật độ từ khóa ổn ({exact} lần trong ~{word_n} từ)."

    # 3) Liên kết nội bộ / ngoài
    internal_n = 0
    external_n = 0
    for a in soup.find_all("a", href=True):
        href = str(a.get("href") or "").strip()
        if not href or href.startswith("#"):
            continue
        if href.startswith("/") or "internal" in href.lower():
            internal_n += 1
            continue
        try:
            p = urlparse(href)
            if p.scheme in ("http", "https"):
                external_n += 1
        except Exception:
            pass
    if _INTERNAL_HINT_RE.search(html):
        internal_n = max(internal_n, 1)
    if internal_n >= 1 and external_n >= 1:
        t3_status, t3_detail = "ok", f"Có {internal_n} liên kết nội bộ/gợi ý và {external_n} liên kết ngoài."
    elif internal_n >= 1 or external_n >= 1:
        t3_status, t3_detail = (
            "warn",
            f"Nội bộ: {internal_n}, ngoài: {external_n}. Nên có cả hai khi phù hợp chủ đề.",
        )
    else:
        t3_status, t3_detail = "fail", "Chưa thấy <a href> nội bộ hoặc ngoài trong HTML."

    # 4) Alt ảnh
    imgs = soup.find_all("img")
    if not imgs:
        t4_status, t4_detail = "warn", "Chưa có thẻ <img> — mỗi H2 nên có figure/ảnh minh họa."
    else:
        bad: list[str] = []
        good = 0
        for img in imgs:
            alt = str(img.get("alt") or "").strip()
            if len(alt) < 4 or _GENERIC_ALT_RE.match(alt):
                bad.append(alt[:40] or "(trống)")
            else:
                good += 1
        if bad and good:
            t4_status, t4_detail = (
                "warn",
                f"{good}/{len(imgs)} ảnh có alt tốt; cần sửa: {', '.join(bad[:3])}.",
            )
        elif bad:
            t4_status, t4_detail = "fail", f"{len(imgs)} ảnh thiếu alt mô tả phù hợp."
        else:
            t4_status, t4_detail = "ok", f"Tất cả {len(imgs)} ảnh có alt text mô tả."

    # 5) Schema JSON-LD
    schema_ok = False
    for script in soup.find_all("script", type=re.compile(r"application/ld\+json", re.I)):
        raw_js = script.string or script.get_text() or ""
        if not raw_js.strip():
            continue
        try:
            data = json.loads(raw_js)
            if isinstance(data, list):
                types = {
                    str(x.get("@type", "")).lower()
                    for x in data
                    if isinstance(x, dict)
                }
            elif isinstance(data, dict):
                types = {str(data.get("@type", "")).lower()}
                graph = data.get("@graph")
                if isinstance(graph, list):
                    types |= {
                        str(x.get("@type", "")).lower()
                        for x in graph
                        if isinstance(x, dict)
                    }
            else:
                types = set()
            if types & {"article", "blogposting", "newsarticle", "faqpage", "question"}:
                schema_ok = True
                break
        except Exception:
            continue
    if not schema_ok and re.search(r"gợi\s*ý\s*schema|application/ld\+json", html, re.I):
        schema_ok = True
    if schema_ok:
        t5_status, t5_detail = "ok", "Có khối JSON-LD (Article/FAQ) hoặc gợi ý schema trong bài."
    else:
        t5_status, t5_detail = (
            "warn",
            "Chưa thấy <script type=\"application/ld+json\"> hợp lệ — thêm Article + FAQ khi publish.",
        )

    # 6) Chính tả / ngữ pháp — không tự động hoàn toàn
    t6_status, t6_detail = (
        "manual",
        "Hệ thống không tự sửa chính tả — đọc lại bài hoặc dùng công cụ hiệu đính trước khi đăng.",
    )

    items = [
        _item(
            "title_meta_keyword",
            "Tiêu đề và mô tả có từ khóa chính",
            t1_status,
            t1_detail,
        ),
        _item("keyword_stuffing", "Không nhồi nhét từ khóa", t2_status, t2_detail),
        _item("internal_external_links", "Liên kết nội bộ và bên ngoài", t3_status, t3_detail),
        _item("image_alt", "Hình ảnh có alt text phù hợp", t4_status, t4_detail),
        _item("schema_format", "Định dạng schema cho bài viết", t5_status, t5_detail),
        _item("proofread", "Chính tả và ngữ pháp", t6_status, t6_detail),
    ]
    counts = {"ok": 0, "warn": 0, "fail": 0, "manual": 0}
    for it in items:
        st = it.get("status") or "warn"
        if st in counts:
            counts[st] += 1
    return {"items": items, "summary": counts, "content_html_stripped": html}
