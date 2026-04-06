"""Async token bucket limiter."""

from __future__ import annotations

import asyncio
import time
from collections import defaultdict


class AsyncRateLimiter:
    """Per-key token bucket limiter for async workflows."""

    def __init__(self) -> None:
        self._state: dict[str, tuple[float, float]] = defaultdict(lambda: (0.0, time.monotonic()))
        self._locks: dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

    async def wait(self, key: str, rate_per_second: float) -> None:
        if rate_per_second <= 0:
            return

        async with self._locks[key]:
            tokens, last_refill = self._state[key]
            now = time.monotonic()
            tokens += (now - last_refill) * rate_per_second
            tokens = min(tokens, 1.0)
            if tokens < 1.0:
                sleep_for = (1.0 - tokens) / rate_per_second
                await asyncio.sleep(sleep_for)
                now = time.monotonic()
                tokens, last_refill = 0.0, now
            else:
                tokens -= 1.0
                last_refill = now

            self._state[key] = (tokens, last_refill)
