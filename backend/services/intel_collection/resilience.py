from __future__ import annotations

import time
from collections import defaultdict
from datetime import datetime
from typing import Callable, TypeVar

T = TypeVar("T")


class RateLimiter:
    """Simple in-process per-source rate limiter."""

    def __init__(self) -> None:
        self._next_allowed_by_key: dict[str, float] = defaultdict(float)

    def wait(self, key: str, rpm: int) -> None:
        if rpm <= 0:
            return
        now = time.time()
        min_interval = 60.0 / max(rpm, 1)
        next_allowed = self._next_allowed_by_key[key]
        if next_allowed > now:
            time.sleep(next_allowed - now)
        self._next_allowed_by_key[key] = max(next_allowed, now) + min_interval


class RetryPolicy:
    def __init__(
        self,
        attempts: int = 2,
        backoff_seconds: float = 1.0,
    ) -> None:
        self.attempts = max(attempts, 1)
        self.backoff_seconds = max(backoff_seconds, 0.0)

    def run(self, fn: Callable[[], T]) -> T:
        last_error: Exception | None = None
        for attempt in range(1, self.attempts + 1):
            try:
                return fn()
            except Exception as exc:  # noqa: BLE001
                last_error = exc
                if attempt < self.attempts:
                    sleep_for = self.backoff_seconds * attempt
                    if sleep_for > 0:
                        time.sleep(sleep_for)
        if last_error is None:
            raise RuntimeError("RetryPolicy exhausted without execution")
        raise last_error


def safe_parse_datetime(
    parse_fn: Callable[[], datetime | None],
) -> datetime | None:
    try:
        return parse_fn()
    except Exception:  # noqa: BLE001
        return None
