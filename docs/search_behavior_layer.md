# Search engine behavior layer (`search_behavior.py`)

Single pass that resolves **conflicting SEO signals** into one coherent verdict, aligned with common Google prioritisation (HTTP → headers → HTML → fallbacks).

## Functions

| Function | Role |
|----------|------|
| `resolve_final_indexability(data)` | Strict stack: HTTP ≥400 → not indexable; then `X-Robots-Tag` on final document (Playwright headers); then rendered `meta robots`; raw header noindex when doc header differs; else crawler `indexability`. Sets `confidence` lower when `conflict_detected`. |
| `resolve_canonical_behavior(data, idx)` | If not indexable → canonical irrelevant (invalid). Else self / declared / ignored (loop, non-indexable target, low similarity from `canonical_target_analysis`). |
| `resolve_primary_url(data, canon)` | Valid declared canonical → primary is canonical; else **final effective URL**. |
| `simulate_indexing_behavior(...)` | `will_index`, human-readable `indexation_reason`, `duplicate_cluster` URLs when modeled as duplicate of canonical, `trust_score` from reliability + cloaking penalties. |
| `compute_signal_reliability(data)` | Tiered reliability for HTTP, headers, meta, DOM (raw vs rendered). |
| `detect_signal_conflicts(data, idx_res)` | Header vs meta, raw vs rendered canonical, redirect vs `final_effective_url`; severity heuristic. |
| `resolve_search_engine_decision(data)` | Full object + `signals_snapshot` for debug. |
| `flatten_for_resolved_signals(decision, data)` | Maps into legacy `resolved_signals` keys used by rules + `simulate_google_indexing`. |
| `compute_rendering_signals(data)` | `js_dependency_level` + `content_reliability` (legacy heuristics). |

## Integration (`decision_engine_v2`)

1. `pre_signals = resolve_seo_truth(data)` — only to pick **declared canonical** for `crawl_canonical_target` before the target probe (same URL selection as before).
2. After `canonical_target_analysis` is attached to `data`, **`resolve_search_engine_decision(data)`** runs.
3. `resolved_signals = {**pre_signals, **flatten_for_resolved_signals(...)}` — **search layer overrides** indexability, canonical truth/type/valid, JS/rendering hints.
4. `simulate_google_indexing` still runs for `ranking_eligibility` / `ignored_signals`; **`will_index`**, **`index_decision_reason`**, **`trust_score`**, **`duplicate_cluster`** are overwritten from `indexing_simulation` when present.
5. Audit debug: with `AUDIT_DEBUG_DIR`, each URL folder gets **`search_behavior.json`** (full decision + snapshot), written **after** the decision (see `pipeline.py`).

## Principles

- **No single signal**: conflicts reduce confidence; canonical to another URL requires target probe + similarity + chain checks.
- **Reasoning**: every branch sets `canonical_reason`, `indexation_reason`, etc.
- **Consistency over dogma**: low similarity or bad chain → treat declared canonical as **ignored** (Google-selected self URL behavior).

## Example JSON

See `data/examples/search_behavior_example_output.json`.
