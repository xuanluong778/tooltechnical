"""Standalone worker for Content AI bulk write jobs (optional if auto-worker is off)."""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(ROOT / "env.local")

from app.services.content_ai_bulk_worker_loop import content_ai_bulk_worker_loop  # noqa: E402


def main() -> None:
    print("content_ai_bulk_worker: started", flush=True)
    content_ai_bulk_worker_loop()


if __name__ == "__main__":
    main()
