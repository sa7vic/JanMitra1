from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class SourceConfig:
    source_id: str
    name: str
    domain: str
    category: str
    source_type: str
    url: str | None = None
    enabled: bool = True
    priority_weight: float = 1.0
    rate_limit_rpm: int = 30
    timeout_seconds: int = 15
    max_items: int = 20
    retry_attempts: int = 2
    retry_backoff_seconds: float = 1.0
    headers: dict[str, str] = field(default_factory=dict)
    parser: dict[str, Any] = field(default_factory=dict)
    api_config: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class NormalizedItem:
    source_id: str
    source_name: str
    category: str
    domain: str
    title: str
    url: str
    published: datetime | None
    summary: str
    tags: list[str] = field(default_factory=list)
    priority_score: float = 0.5
    raw: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "source_name": self.source_name,
            "category": self.category,
            "domain": self.domain,
            "title": self.title,
            "url": self.url,
            "published": (
                self.published.isoformat() if self.published else None
            ),
            "summary": self.summary,
            "tags": self.tags,
            "priority_score": self.priority_score,
            "raw": self.raw,
        }

    def to_llm_payload(self) -> dict[str, Any]:
        return {
            "headline": self.title,
            "domain": self.domain,
            "category": self.category,
            "summary": self.summary,
            "key_tags": self.tags,
            "priority": self.priority_score,
            "published": (
                self.published.isoformat() if self.published else None
            ),
            "url": self.url,
            "source": self.source_name,
        }


@dataclass(slots=True)
class CollectionResult:
    total_collected: int
    total_persisted: int
    total_failed_sources: int
    by_source: dict[str, int] = field(default_factory=dict)
