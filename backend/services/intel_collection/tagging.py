from __future__ import annotations

import re

from .types import NormalizedItem


DOMAIN_PRIORITY = {
    "geopolitics": 1.0,
    "defense": 0.95,
    "climate": 0.85,
    "economics": 0.8,
    "technology": 0.75,
}

KEYWORDS_BY_DOMAIN = {
    "geopolitics": {
        "sanction",
        "border",
        "diplomat",
        "treaty",
        "summit",
        "embassy",
        "ceasefire",
    },
    "climate": {
        "cyclone",
        "flood",
        "rainfall",
        "heatwave",
        "drought",
        "earthquake",
        "forecast",
    },
    "economics": {
        "inflation", "repo", "gdp", "fiscal", "market", "liquidity", "export"
    },
    "defense": {
        "navy",
        "air force",
        "army",
        "missile",
        "drill",
        "security",
        "operation",
    },
    "technology": {
        "semiconductor",
        "ai",
        "cyber",
        "startup",
        "innovation",
        "digital",
        "data",
    },
}

TOKEN_PATTERN = re.compile(r"[a-zA-Z]{3,}")


def extract_tags(item: NormalizedItem, max_tags: int = 6) -> list[str]:
    text = f"{item.title} {item.summary}".lower()
    tokens = TOKEN_PATTERN.findall(text)
    domain_keywords = KEYWORDS_BY_DOMAIN.get(item.domain, set())

    tags: list[str] = []
    seen: set[str] = set()
    for keyword in domain_keywords:
        if keyword in text and keyword not in seen:
            tags.append(keyword)
            seen.add(keyword)

    for token in tokens:
        if token not in seen and token not in {
            "india",
            "news",
            "today",
            "update",
        }:
            tags.append(token)
            seen.add(token)
        if len(tags) >= max_tags:
            break
    return tags


def compute_priority(item: NormalizedItem) -> float:
    base = DOMAIN_PRIORITY.get(item.domain, 0.6)
    keyword_hits = len(
        [
            tag
            for tag in item.tags
            if tag in KEYWORDS_BY_DOMAIN.get(item.domain, set())
        ]
    )
    score = min(1.0, base + (keyword_hits * 0.03))
    return round(score, 3)
