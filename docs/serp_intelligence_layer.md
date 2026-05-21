# SERP intelligence layer

Models **competition and difficulty** using relative signals (your crawl vs SERP snapshot), not a generic checklist.

## Modules

| File | Role |
|------|------|
| `serp_fetcher.py` | `fetch_serp(keyword, location, device)` — **SerpAPI** when `SERPAPI_KEY` is set; otherwise a **deterministic mock** (stable URLs/titles for tests and dev). |
| `serp_competitor_analysis.py` | `analyze_serp_competitors(serp_results, crawl_data, keyword=...)` — internal **PageRank** when the SERP URL was crawled; else **domain frequency + path depth + title quality** proxy. |
| `keyword_difficulty.py` | `compute_keyword_difficulty(serp_analysis)` — 0–100 score; rewards **weak competitors**, penalises **high max/p90 authority** and **homogeneous** SERPs. |
| `serp_features.py` | `detect_serp_features(serp_payload)` — uses SerpAPI extras when present; else **title/snippet heuristics** (FAQ/video hints). |
| `ranking_gap.py` | `analyze_ranking_gap(keyword, your_pages, serp_data)` — best URL match, **authority/content/topical** gaps vs SERP. |
| `keyword_opportunity.py` | `compute_keyword_opportunity(...)` — blends **volume**, **difficulty**, **your ranking_score**, **topical authority**. |
| `serp_simulation.py` | `simulate_serp_ranking(keyword, your_page, competitors)` — **probability_top10** + **position range** from strength vs top-10 bench. |
| `serp_intel_bundle.py` | `build_serp_keyword_report(...)` — **Task 8** single JSON object. |

## API

`POST /api/serp/keyword-intelligence` with JSON body (`keyword`, optional `search_volume`, `your_pages`, `crawl_data`, `topical_authority_score`, `location`, `device`).

## Integration (keyword → page → ranking)

1. Run your crawl + **ranking pipeline** → collect per-URL `ranking_score`, `pagerank`, `word_count`, **topic extraction** `primary_topic`, `title`.
2. Build `crawl_data[url] = { "pagerank_score", "word_count" }` for URLs that appear in both crawl and SERP (improves authority overlap).
3. Call `build_serp_keyword_report` or the API with `your_pages` and optional **cluster authority** from the topical layer as `topical_authority_score`.

## Principles

- **Relative**: difficulty compares **you vs this SERP snapshot**, not absolute third-party KD.
- **Explainable**: `reasoning`, `actionable_gap`, `limiting_factors` carry *why* conclusions.
- **Realistic**: without SerpAPI, mock data is clearly tagged `source: mock` — do not treat as live SERP.

## Example

See `data/examples/serp_keyword_report_example.json`.
