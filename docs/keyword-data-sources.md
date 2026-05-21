## Keyword data sources (Volume/CPC + SERP)

This app supports **real** keyword metrics via external providers, with safe fallbacks.

### 1) Feature flags

- **`VOLUME_API_ENABLED`**: enable real Search Volume/CPC providers (default: off)
- **`SERP_FETCH_ENABLED`**: enable SERP fetch (top 10 URLs/titles/snippets + features, default: off)

Recommended local defaults:

```bash
VOLUME_API_ENABLED=0
SERP_FETCH_ENABLED=0
```

### 2) DataForSEO (Search Volume + CPC)

Provider: `app/services/volume_providers/dataforseo.py`

Required env:

```bash
VOLUME_API_ENABLED=1
DATAFORSEO_LOGIN=your_login
DATAFORSEO_PASSWORD=your_password

# Prefer explicit codes (no hardcoded mapping in app):
DATAFORSEO_LOCATION_CODE=2840
DATAFORSEO_LANGUAGE_CODE=vi
```

Optional:

```bash
DATAFORSEO_BASE_URL=https://api.dataforseo.com
VOLUME_BATCH_SIZE=100
VOLUME_CACHE_TTL_SECONDS=2592000
REDIS_URL=redis://127.0.0.1:6379/0
```

Notes:
- If DataForSEO is not configured or fails, the app will **fallback** to deterministic heuristic volumes/CPC.
- Volume rows are cached in **Redis** when available, and also stored as a **DB fallback** table: `keyword_volume_cache`.

### 3) SERP fetch (top 10 + features)

Implementation: `app/services/serp_fetcher.py`

Env:

```bash
SERP_FETCH_ENABLED=1
SERP_TOP_N=10
SERP_CACHE_TTL_SECONDS=604800
REDIS_URL=redis://127.0.0.1:6379/0
```

Providers (in order, configurable):
- Custom JSON proxy: `SERP_PROXY_URL`
- SerpAPI: `SERPAPI_KEY`
- Google CSE: `GOOGLE_CSE_API_KEY` + `GOOGLE_CSE_ID`

`SERP_FETCH_PROVIDER_ORDER` example:

```bash
SERP_FETCH_PROVIDER_ORDER=custom,serpapi,cse
```

What you get:
- `fetch_serp_for_keyword(...)` returns `serp_urls`, `titles`, `snippets`, and `features` (best-effort from SerpAPI or custom proxy).
- Keyword Research API attaches `meta.seed_serp_top10` when `SERP_FETCH_ENABLED=1`.

