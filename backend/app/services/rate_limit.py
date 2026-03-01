"""Simple in-memory rate limiter for ingestion and model calls."""

import logging
import time
from collections import defaultdict

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token-bucket rate limiter keyed by caller ID.

    Args:
        max_calls: Maximum calls per window.
        window_seconds: Time window in seconds.
    """

    def __init__(self, max_calls: int = 60, window_seconds: float = 60.0):
        self.max_calls = max_calls
        self.window = window_seconds
        self._calls: dict[str, list[float]] = defaultdict(list)

    def allow(self, key: str = "default") -> bool:
        """Return True if the call is allowed under the rate limit."""
        now = time.monotonic()
        cutoff = now - self.window
        self._calls[key] = [t for t in self._calls[key] if t > cutoff]
        if len(self._calls[key]) >= self.max_calls:
            logger.warning(f"Rate limit exceeded for key={key} ({self.max_calls}/{self.window}s)")
            return False
        self._calls[key].append(now)
        return True

    def wait_if_needed(self, key: str = "default") -> None:
        """Block until a call is allowed."""
        while not self.allow(key):
            time.sleep(0.5)


# Shared limiters
ingestion_limiter = RateLimiter(max_calls=100, window_seconds=60.0)
embedding_limiter = RateLimiter(max_calls=50, window_seconds=60.0)
