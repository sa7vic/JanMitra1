from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
import importlib
from typing import Any

import requests
from bs4 import BeautifulSoup
from dateutil import parser as date_parser

from .resilience import safe_parse_datetime
from .types import NormalizedItem, SourceConfig


class SourceAdapter(ABC):
    @abstractmethod
    def fetch(self, source: SourceConfig) -> list[NormalizedItem]:
        raise NotImplementedError


class RssAdapter(SourceAdapter):
    def fetch(self, source: SourceConfig) -> list[NormalizedItem]:
        if not source.url:
            return []

        feedparser = importlib.import_module("feedparser")
        parsed = feedparser.parse(source.url)
        items: list[NormalizedItem] = []
        for entry in parsed.entries[: source.max_items]:
            title = (entry.get("title") or "").strip()
            link = (entry.get("link") or "").strip()
            if not title or not link:
                continue

            summary = (
                entry.get("summary")
                or entry.get("description")
                or (
                    entry.get("content", [{}])[0].get("value")
                    if entry.get("content")
                    else ""
                )
                or title
            )
            summary = BeautifulSoup(
                summary,
                "html.parser",
            ).get_text(" ", strip=True)

            published = safe_parse_datetime(
                lambda: _parse_feed_datetime(entry)
            )

            items.append(
                NormalizedItem(
                    source_id=source.source_id,
                    source_name=source.name,
                    category=source.category,
                    domain=source.domain,
                    title=title,
                    url=link,
                    published=published,
                    summary=summary,
                    raw={"source_type": "rss"},
                )
            )
        return items


class WebAdapter(SourceAdapter):
    def fetch(self, source: SourceConfig) -> list[NormalizedItem]:
        if not source.url:
            return []

        timeout = source.timeout_seconds
        response = requests.get(
            source.url,
            headers=source.headers or None,
            timeout=timeout,
        )
        response.raise_for_status()

        parser_cfg = source.parser or {}
        article_selector = parser_cfg.get("article_selector", "article")
        title_selector = parser_cfg.get("title_selector", "h1, h2, h3, a")
        link_selector = parser_cfg.get("link_selector", "a")
        summary_selector = parser_cfg.get("summary_selector", "p")

        soup = BeautifulSoup(response.text, "html.parser")
        article_nodes = soup.select(article_selector)
        items: list[NormalizedItem] = []

        for node in article_nodes[: source.max_items]:
            title_node = node.select_one(title_selector)
            link_node = node.select_one(link_selector)
            summary_node = node.select_one(summary_selector)

            title = title_node.get_text(" ", strip=True) if title_node else ""
            url = ""
            if link_node and link_node.get("href"):
                href = link_node.get("href").strip()
                if href.startswith("http"):
                    url = href
                elif source.url:
                    url = requests.compat.urljoin(source.url, href)

            summary = (
                summary_node.get_text(" ", strip=True)
                if summary_node
                else title
            )

            if not title or not url:
                continue

            items.append(
                NormalizedItem(
                    source_id=source.source_id,
                    source_name=source.name,
                    category=source.category,
                    domain=source.domain,
                    title=title,
                    url=url,
                    published=None,
                    summary=summary,
                    raw={"source_type": "web"},
                )
            )

        return items


class ApiAdapter(SourceAdapter):
    def __init__(self) -> None:
        self._handlers: dict[str, Any] = {
            "reliefweb": self._fetch_reliefweb,
            "worldbank": self._fetch_worldbank,
            "json_list": self._fetch_json_list,
        }

    def fetch(self, source: SourceConfig) -> list[NormalizedItem]:
        provider = (source.api_config or {}).get("provider", "json_list")
        handler = self._handlers.get(provider)
        if not handler:
            raise ValueError(f"Unsupported API provider: {provider}")
        return handler(source)

    def _fetch_reliefweb(self, source: SourceConfig) -> list[NormalizedItem]:
        url = source.api_config.get("url") or source.url
        if not url:
            return []

        payload = source.api_config.get("payload") or {}
        response = requests.post(
            url,
            json=payload,
            timeout=source.timeout_seconds,
        )
        response.raise_for_status()

        data = response.json().get("data", [])
        items: list[NormalizedItem] = []
        for row in data[: source.max_items]:
            fields = row.get("fields", {})
            title = (fields.get("title") or "").strip()
            item_url = fields.get("url") or ""
            summary = fields.get("body-html") or fields.get("body") or title
            summary = BeautifulSoup(
                summary,
                "html.parser",
            ).get_text(" ", strip=True)
            published = safe_parse_datetime(
                lambda: date_parser.parse(
                    fields.get("date", {}).get("created")
                )
            )
            if not title or not item_url:
                continue
            items.append(
                NormalizedItem(
                    source_id=source.source_id,
                    source_name=source.name,
                    category=source.category,
                    domain=source.domain,
                    title=title,
                    url=item_url,
                    published=published,
                    summary=summary,
                    raw={"source_type": "api", "provider": "reliefweb"},
                )
            )
        return items

    def _fetch_worldbank(self, source: SourceConfig) -> list[NormalizedItem]:
        url = source.api_config.get("url") or source.url
        if not url:
            return []

        response = requests.get(url, timeout=source.timeout_seconds)
        response.raise_for_status()
        body = response.json()
        rows = body[1] if isinstance(body, list) and len(body) > 1 else []

        items: list[NormalizedItem] = []
        for row in rows[: source.max_items]:
            country = row.get("country", {}).get("value", "Unknown")
            indicator = row.get("indicator", {}).get("value", "Indicator")
            title = f"{country} - {indicator}"
            year = row.get("date")
            value = row.get("value")
            if value is None:
                continue
            item_url = f"{url}#year={year}"
            summary = f"Value {value} reported for year {year}."
            published = safe_parse_datetime(
                lambda: datetime(int(year), 1, 1, tzinfo=UTC)
            )

            items.append(
                NormalizedItem(
                    source_id=source.source_id,
                    source_name=source.name,
                    category=source.category,
                    domain=source.domain,
                    title=title,
                    url=item_url,
                    published=published,
                    summary=summary,
                    raw={
                        "source_type": "api",
                        "provider": "worldbank",
                        "row": row,
                    },
                )
            )
        return items

    def _fetch_json_list(self, source: SourceConfig) -> list[NormalizedItem]:
        cfg = source.api_config or {}
        url = cfg.get("url") or source.url
        if not url:
            return []

        response = requests.get(
            url,
            headers=source.headers or None,
            timeout=source.timeout_seconds,
        )
        response.raise_for_status()
        body = response.json()

        path = cfg.get("items_path", [])
        rows = _drill_path(body, path) if path else body
        if not isinstance(rows, list):
            return []

        title_key = cfg.get("title_key", "title")
        url_key = cfg.get("url_key", "url")
        summary_key = cfg.get("summary_key", "summary")
        published_key = cfg.get("published_key", "published")

        items: list[NormalizedItem] = []
        for row in rows[: source.max_items]:
            if not isinstance(row, dict):
                continue
            title = str(row.get(title_key, "")).strip()
            item_url = str(row.get(url_key, "")).strip()
            summary = str(row.get(summary_key, title)).strip()
            published = safe_parse_datetime(
                lambda: date_parser.parse(str(row.get(published_key)))
            )

            if not title or not item_url:
                continue

            items.append(
                NormalizedItem(
                    source_id=source.source_id,
                    source_name=source.name,
                    category=source.category,
                    domain=source.domain,
                    title=title,
                    url=item_url,
                    published=published,
                    summary=summary,
                    raw={
                        "source_type": "api",
                        "provider": "json_list",
                        "row": row,
                    },
                )
            )
        return items


def _drill_path(payload: Any, path: list[Any]) -> Any:
    cursor = payload
    for key in path:
        if isinstance(cursor, list) and isinstance(key, int):
            if key >= len(cursor):
                return []
            cursor = cursor[key]
        elif isinstance(cursor, dict):
            cursor = cursor.get(key, [])
        else:
            return []
    return cursor


def _parse_feed_datetime(entry: Any) -> datetime | None:
    published = entry.get("published") or entry.get("updated")
    if published:
        try:
            return date_parser.parse(published)
        except Exception:  # noqa: BLE001
            parsed = parsedate_to_datetime(published)
            return parsed
    return None
