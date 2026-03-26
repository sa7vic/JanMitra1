from __future__ import annotations

from pathlib import Path

from models.database import Article, db
from services.intel_collection import DomainDataCollector


class DataCollector(DomainDataCollector):
    """Compatibility facade over the modular domain-aware collector engine."""

    def __init__(self, source_registry_path: str | None = None) -> None:
        registry = (
            source_registry_path
            or Path(__file__).resolve().parents[1]
            / "data"
            / "news_sources.json"
        )
        super().__init__(source_registry_path=registry)

    def fetch_articles(self, max_per_source: int = 10) -> int:
        """Collect and persist articles for existing scheduler call sites."""
        # Avoid mutating file config. Adjust per-run max items in memory.
        sources = self.load_sources()
        for source in sources:
            source.max_items = max_per_source

        # Use the same collection flow but with in-memory source override.
        original_loader = self.load_sources
        self.load_sources = lambda: sources  # type: ignore[method-assign]
        try:
            result = self.collect()
            return result.total_persisted
        finally:
            self.load_sources = original_loader  # type: ignore[method-assign]

    def collect_normalized(
        self,
        domains: set[str] | None = None,
    ) -> list[dict]:
        """Collect and return normalized LLM payloads without persistence."""
        captured_items: list[dict] = []

        def _capture(items):
            captured_items.extend(item.to_llm_payload() for item in items)
            return 0

        original_persist = self.persist_items
        self.persist_items = _capture  # type: ignore[method-assign]
        try:
            self.collect(domains=domains)
        finally:
            self.persist_items = original_persist
        return captured_items

    def persist_items(self, items) -> int:
        persisted = 0
        for item in items:
            article = Article(
                title=item.title,
                content=item.summary,
                source=item.source_name,
                url=item.url,
                category=item.category,
                published_at=item.published,
                importance=item.priority_score,
            )
            db.session.add(article)
            persisted += 1

        if persisted:
            db.session.commit()
        return persisted

    def get_latest_articles(self, limit: int = 100):
        query = Article.query.order_by(Article.created_at.desc())
        return query.limit(limit).all()


if __name__ == "__main__":
    collector = DataCollector()
    collector.fetch_articles(max_per_source=5)
