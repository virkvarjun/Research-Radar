"""Tests for rate limiting utility."""

import time

import pytest

from app.services.rate_limit import RateLimiter


class TestRateLimiter:
    def test_allows_within_limit(self):
        limiter = RateLimiter(max_calls=5, window_seconds=10.0)
        for _ in range(5):
            assert limiter.allow("test") is True

    def test_blocks_over_limit(self):
        limiter = RateLimiter(max_calls=3, window_seconds=10.0)
        assert limiter.allow("test") is True
        assert limiter.allow("test") is True
        assert limiter.allow("test") is True
        assert limiter.allow("test") is False

    def test_separate_keys(self):
        limiter = RateLimiter(max_calls=2, window_seconds=10.0)
        assert limiter.allow("a") is True
        assert limiter.allow("a") is True
        assert limiter.allow("a") is False
        # Different key should still be allowed
        assert limiter.allow("b") is True

    def test_window_expiry(self):
        limiter = RateLimiter(max_calls=1, window_seconds=0.1)
        assert limiter.allow("test") is True
        assert limiter.allow("test") is False
        time.sleep(0.15)
        assert limiter.allow("test") is True

    def test_default_key(self):
        limiter = RateLimiter(max_calls=2, window_seconds=10.0)
        assert limiter.allow() is True
        assert limiter.allow() is True
        assert limiter.allow() is False
