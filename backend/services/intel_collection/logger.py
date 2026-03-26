from __future__ import annotations

import json
import logging
from datetime import datetime, UTC
from typing import Any


_logger = logging.getLogger("intel_collection")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        extra = getattr(record, "extra", None)
        if isinstance(extra, dict):
            payload.update(extra)
        return json.dumps(payload, ensure_ascii=True)


def get_logger() -> logging.Logger:
    if not _logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        _logger.addHandler(handler)
        _logger.setLevel(logging.INFO)
    return _logger


def log_event(level: int, message: str, **extra: Any) -> None:
    logger = get_logger()
    logger.log(level, message, extra={"extra": extra})
