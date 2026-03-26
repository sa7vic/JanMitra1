# Intel Collection Extension Guide

## Add a new domain

1. Add one or more entries in `backend/data/news_sources.json` with a new `domain` value.
2. Optionally add domain keywords and base priority in `backend/services/intel_collection/tagging.py`.
3. No core orchestrator changes are required.

## Add a new source

Add a JSON object with:
- `source_id`: unique stable id
- `name`: display name
- `domain`: logical domain (`geopolitics`, `climate`, `economics`, etc.)
- `category`: sub-topic
- `type`: `rss`, `web`, or `api`
- `url`: feed URL or endpoint (optional for API if inside `api.url`)

Optional controls:
- `enabled` (default `true`)
- `rate_limit_rpm` (requests per minute)
- `retry_attempts`
- `retry_backoff_seconds`
- `timeout_seconds`
- `max_items`
- `priority_weight`

For `web` sources, add `parser` selectors:
- `article_selector`
- `title_selector`
- `link_selector`
- `summary_selector`

For `api` sources, add `api` config:
- `provider`: `reliefweb`, `worldbank`, or `json_list`
- provider-specific fields (for `json_list`: `items_path`, `title_key`, `url_key`, `summary_key`, `published_key`)

## Add a new API provider

1. Implement `_fetch_<provider>` in `backend/services/intel_collection/adapters.py`.
2. Register the provider handler in `ApiAdapter.__init__`.
3. Configure source in JSON with `"api": {"provider": "<provider>"}`.

## Operational recommendations

- Keep `rate_limit_rpm` conservative for web sources.
- Use retries only for transient failures; avoid large retry counts.
- Keep collectors stateless; persistence should be a separate concern.
- Store API keys in environment variables and inject through headers.
