from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Iterable

from .adapters import ApiAdapter, RssAdapter, SourceAdapter, WebAdapter
from .dedup import Deduplicator
from .logger import log_event
from .resilience import RateLimiter, RetryPolicy
from .tagging import compute_priority, extract_tags
from .types import CollectionResult, NormalizedItem, SourceConfig


class DomainDataCollector:
    """Domain-aware, JSON-driven collector orchestrator."""

    def __init__(self, source_registry_path: str | Path) -> None:
        self.source_registry_path = Path(source_registry_path)
        self.rate_limiter = RateLimiter()
        self.deduplicator = Deduplicator()
        self.adapters: dict[str, SourceAdapter] = {
            "rss": RssAdapter(),
            "web": WebAdapter(),
            "api": ApiAdapter(),
        }

    def load_sources(self) -> list[SourceConfig]:
        if not self.source_registry_path.exists():
            return []
        content = self.source_registry_path.read_text(encoding="utf-8").strip()
        if not content:
            return []

        rows = json.loads(content)
        sources: list[SourceConfig] = []
        for row in rows:
            if not row.get("enabled", True):
                continue
            sources.append(
                SourceConfig(
                    source_id=row["source_id"],
                    name=row["name"],
                    domain=row["domain"],
                    category=row.get("category", row["domain"]),
                    source_type=row["type"],
                    url=row.get("url"),
                    enabled=row.get("enabled", True),
                    priority_weight=float(row.get("priority_weight", 1.0)),
                    rate_limit_rpm=int(row.get("rate_limit_rpm", 30)),
                    timeout_seconds=int(row.get("timeout_seconds", 15)),
                    max_items=int(row.get("max_items", 20)),
                    retry_attempts=int(row.get("retry_attempts", 2)),
                    retry_backoff_seconds=float(
                        row.get("retry_backoff_seconds", 1.0)
                    ),
                    headers=row.get("headers", {}),
                    parser=row.get("parser", {}),
                    api_config=row.get("api", {}),
                )
            )
        return sources

    def collect(self, domains: set[str] | None = None) -> CollectionResult:
        sources = self.load_sources()
        if domains:
            sources = [s for s in sources if s.domain in domains]

        total_collected = 0
        total_failed_sources = 0
        by_source: dict[str, int] = {}
        all_items: list[NormalizedItem] = []

        for source in sources:
            adapter = self.adapters.get(source.source_type)
            if not adapter:
                log_event(
                    logging.WARNING,
                    "source_adapter_missing",
                    source_id=source.source_id,
                    source_type=source.source_type,
                )
                total_failed_sources += 1
                continue

            retry = RetryPolicy(
                attempts=source.retry_attempts,
                backoff_seconds=source.retry_backoff_seconds,
            )

            try:
                self.rate_limiter.wait(source.source_id, source.rate_limit_rpm)
                items = retry.run(lambda: adapter.fetch(source))
                prepared = list(
                    self._prepare_items(items, source.priority_weight)
                )
                all_items.extend(prepared)
                by_source[source.source_id] = len(prepared)
                total_collected += len(prepared)

                log_event(
                    logging.INFO,
                    "source_collection_completed",
                    source_id=source.source_id,
                    domain=source.domain,
                    count=len(prepared),
                )
            except Exception as exc:  # noqa: BLE001
                total_failed_sources += 1
                log_event(
                    logging.ERROR,
                    "source_collection_failed",
                    source_id=source.source_id,
                    domain=source.domain,
                    error=str(exc),
                )

        persisted = self.persist_items(all_items)
        return CollectionResult(
            total_collected=total_collected,
            total_persisted=persisted,
            total_failed_sources=total_failed_sources,
            by_source=by_source,
        )

    def _prepare_items(
        self, items: list[NormalizedItem], priority_weight: float
    ) -> Iterable[NormalizedItem]:
        for item in items:
            if self.deduplicator.is_duplicate(item):
                continue
            item.tags = extract_tags(item)
            item.priority_score = round(
                compute_priority(item) * priority_weight,
                3,
            )
            yield item

    def persist_items(self, items: list[NormalizedItem]) -> int:
        raise NotImplementedError("Implement persistence in subclass/facade")
