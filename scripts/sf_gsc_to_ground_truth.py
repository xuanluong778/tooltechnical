"""
Convert Screaming Frog / GSC-style CSV rows into ground_truth pairs for audit evaluation.

Expected columns (case-insensitive headers): url, status_code, h1, meta_description, alt_text, indexability
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


def _norm_url(u: str) -> str:
    return (u or "").strip().lower().rstrip("/")


def _empty(s: object) -> bool:
    t = ("" if s is None else str(s)).strip()
    return t in ("", "-", "n/a", "na")


def _intish(v: object) -> int | None:
    if v is None:
        return None
    s = str(v).strip()
    if not s or s.lower() in ("false", "no", "none"):
        return 0
    try:
        return int(float(s))
    except ValueError:
        return None


def _indexability_blocked(val: object) -> bool:
    t = ("" if val is None else str(val)).strip().lower()
    if not t:
        return False
    needles = (
        "noindex",
        "none",
        "non-indexable",
        "non indexable",
        "not indexed",
        "blocked",
        "no: index",
        "excluded",
    )
    return any(n in t for n in needles)


def _alt_missing_issue(alt_text: object) -> bool:
    if alt_text is None:
        return False
    s = str(alt_text).strip().lower()
    if s in ("", "-", "n/a", "na", "0", "false", "no", "none"):
        return False
    n = _intish(alt_text)
    if n is not None:
        return n > 0
    return s in ("true", "yes", "y", "1")


def row_to_issues(row: dict[str, str]) -> list[dict[str, str]]:
    keymap = {k.strip().lower(): v for k, v in row.items() if k is not None}
    url = _norm_url(str(keymap.get("url", "")))
    if not url:
        return []

    issues: list[dict[str, str]] = []

    sc_raw = keymap.get("status_code", keymap.get("status", ""))
    try:
        sc = int(float(str(sc_raw).strip())) if str(sc_raw).strip() else 0
    except ValueError:
        sc = 0
    if sc >= 400:
        issues.append({"url": url, "issue_type": "broken_internal_link"})

    h1 = keymap.get("h1", keymap.get("h1-1", ""))
    if _empty(h1):
        issues.append({"url": url, "issue_type": "missing_h1"})

    md = keymap.get("meta_description", keymap.get("meta description 1", ""))
    if _empty(md):
        issues.append({"url": url, "issue_type": "missing_meta_description"})

    if _alt_missing_issue(keymap.get("alt_text", keymap.get("images missing alt text", ""))):
        issues.append({"url": url, "issue_type": "images_missing_alt"})

    if _indexability_blocked(keymap.get("indexability", "")):
        issues.append({"url": url, "issue_type": "indexability_blocked"})

    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description="CSV (SF/GSC export) → ground_truth JSON array")
    ap.add_argument("csv_path", type=Path, help="Path to UTF-8 CSV")
    args = ap.parse_args()

    out: list[dict[str, str]] = []
    with args.csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            out.extend(row_to_issues({str(k): ("" if v is None else str(v)) for k, v in row.items()}))

    json.dump(out, sys.stdout, ensure_ascii=False)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
