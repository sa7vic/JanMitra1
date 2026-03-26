from __future__ import annotations

from hashlib import sha256

from models.database import Article
from .types import NormalizedItem


class Deduplicator:
    """Deduplicates both in-memory and against persisted URLs."""

    def __init__(self) -> None:
        self._seen_signatures: set[str] = set()

    def _signature(self, item: NormalizedItem) -> str:
        key = f"{item.url.strip().lower()}|{item.title.strip().lower()}"
        return sha256(key.encode("utf-8")).hexdigest()

    def is_duplicate(self, item: NormalizedItem) -> bool:
        if Article.query.filter_by(url=item.url).first():
            return True
        signature = self._signature(item)
        if signature in self._seen_signatures:
            return True
        self._seen_signatures.add(signature)
        return False
