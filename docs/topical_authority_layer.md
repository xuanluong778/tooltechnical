# Topical authority layer

This layer approximates how search systems reward **topical depth**, **coherent clusters**, and **internal reinforcement**—without running a full NLP stack.

## Modules

| File | Role |
|------|------|
| `app/services/topic_extraction.py` | Tokens from title, H1–H2, main-like body; stopwords + light stemming; `primary_topic`, `secondary_topics`, `topic_confidence`, `keywords`. |
| `app/services/topic_clustering.py` | Greedy union by similarity = max(Jaccard on token sets, blended cosine on weighted bags). |
| `app/services/topical_authority.py` | Cluster score from size, intra-cluster internal links, mean PageRank mass, content depth. |
| `app/services/topic_relevance.py` | Page token bag vs cluster `topic_label`; `topic_alignment` if primary equals label. |
| `app/services/topic_gap_analysis.py` | Flags small / low-authority / weak-link / shallow clusters; expansion hints. |
| `app/services/topical_site_layer.py` | Orchestrates extraction → cluster → authority → relevance → gaps for one crawl. |

## Ranking integration

`compute_ranking_score(..., topical_signals=...)` in `ranking_engine.py`:

- **Boost:** `+ 7 × cluster_authority_normalized` (0–1) and `+ 9 × topic_relevance_score` (0–1).
- **Penalize:** −8 if `outside_main_cluster` (page not in the largest cluster when that cluster holds ≥28% of URLs). −5 if `weak_topic_coverage` (cluster authority “low” or coverage score &lt; 0.3).

`build_page_insights_for_crawl` attaches:

- Per row: `topic`, `authority`, and topical-aware `ranking`.
- `site_graph_summary`: `topic_clusters`, `authority_summary`, `topic_gaps`.

## Design choices

1. **Clusters &gt; single pages:** authority is computed on the cluster graph slice and PageRank mass of member URLs—not on isolated on-page terms alone.
2. **Internal links matter:** directed edges whose target stays inside the cluster increase `internal_linking_score`.
3. **Depth:** word count + `thin` / `normal` / `deep` bucket from existing `analyze_content` heuristics.
4. **Efficiency:** no embeddings; bags are small counters suitable for crawls in the hundreds of URLs.

## Tuning

- `cluster_topics(..., merge_threshold=0.18)` — lower → more clusters; higher → broader themes.
- Authority weights inside `compute_topical_authority` can be adjusted to match your vertical (news vs e-commerce).

## Example JSON

See `data/examples/topical_authority_example_output.json`.
