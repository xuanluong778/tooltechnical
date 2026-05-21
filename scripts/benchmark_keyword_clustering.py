import os
import sys
import time
from pathlib import Path


# Allow running directly: `python scripts/benchmark_keyword_clustering.py`
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def run(n: int) -> None:
    from app.services.keyword_clusterer import cluster_keywords

    # Keep the benchmark realistic but not pathologically hard:
    # generate multiple topics so blocking can do useful work.
    topics = ["sửa laptop", "mua iphone", "báo giá điều hòa", "hướng dẫn excel", "review camera"]
    # Add a stable unique token so dedupe/merge doesn't collapse N too much.
    kws = [f"{topics[i % len(topics)]} quận {i%20} m{i} {i%13}" for i in range(n)]
    recs = [{"keyword": k, "source": "bench"} for k in kws]
    t0 = time.time()
    os.environ.setdefault("CLUSTER_BENCH_LOG", "1")
    out = cluster_keywords(recs, fetch_serp=False, cluster_strictness="normal")
    dt = time.time() - t0
    print(f"n={n} clusters={len(out)} sec={dt:.2f}", flush=True)


if __name__ == "__main__":
    # benchmark defaults (fast + deterministic)
    os.environ.setdefault("SERP_FETCH_ENABLED", "0")
    os.environ.setdefault("KEYWORD_CLUSTER_SCALABLE_N", "800")
    os.environ.setdefault("KEYWORD_CLUSTER_SERP_MAX_N", "200")
    os.environ.setdefault("KEYWORD_CLUSTER_INTENT_STRICT", "1")
    os.environ.setdefault("KW_ENABLE_SYNONYMS", "1")
    os.environ.setdefault("BENCH_FAST", "1")
    os.environ.setdefault("KEYWORD_CLUSTER_BLOCK_TOPK", "10")
    # Keep runtime bounded on dev machines
    os.environ.setdefault("KEYWORD_CLUSTER_BLOCK_MAX", "260")
    os.environ.setdefault("KEYWORD_CLUSTER_BLOCK_HARD_CAP", "600")
    # Provide a small, reliable default run. Increase as needed.
    sizes = os.getenv("BENCH_SIZES", "1000,5000").strip()
    ns = [int(x) for x in sizes.split(",") if x.strip().isdigit()]
    for n in (ns or [1000, 5000]):
        run(n)

