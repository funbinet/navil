"""Priority task scheduler used by scan workers."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from itertools import count


@dataclass(order=True, slots=True)
class ScheduledTask:
    priority: int
    order: int
    payload: dict[str, object] = field(compare=False)


class TaskScheduler:
    def __init__(self) -> None:
        self._queue: asyncio.PriorityQueue[ScheduledTask] = asyncio.PriorityQueue()
        self._order = count()

    async def put(self, payload: dict[str, object], priority: int = 10) -> None:
        task = ScheduledTask(priority=priority, order=next(self._order), payload=payload)
        await self._queue.put(task)

    async def get(self) -> dict[str, object]:
        task = await self._queue.get()
        return task.payload

    def size(self) -> int:
        return self._queue.qsize()
