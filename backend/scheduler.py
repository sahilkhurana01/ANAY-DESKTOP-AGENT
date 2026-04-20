"""
Local reminder scheduler for ANAY Desktop.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, List

from memory import memory_store

logger = logging.getLogger(__name__)


def _parse_iso(value: str) -> datetime:
    normalized = value.replace("Z", "+00:00")
    dt = datetime.fromisoformat(normalized)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


class ReminderScheduler:
    def __init__(self):
        self._running = False
        self._fired: set[str] = set()
        self._callbacks: List = []

    def register_callback(self, callback):
        self._callbacks.append(callback)

    async def start(self):
        if self._running:
            return
        self._running = True
        while self._running:
            try:
                now = datetime.now(timezone.utc)
                due_items: List[Dict] = []
                for item in memory_store.list_reminders(limit=100):
                    if item["status"] != "scheduled" or item["id"] in self._fired:
                        continue
                    due_at = _parse_iso(item["due_at"])
                    if due_at <= now:
                        due_items.append(item)

                for item in due_items:
                    self._fired.add(item["id"])
                    logger.info("Reminder due: %s", item["task"])
                    for callback in self._callbacks:
                        try:
                            result = callback(item)
                            if asyncio.iscoroutine(result):
                                await result
                        except Exception as exc:
                            logger.error("Reminder callback failed: %s", exc)
                await asyncio.sleep(10)
            except Exception as exc:
                logger.error("Reminder scheduler error: %s", exc)
                await asyncio.sleep(10)

    def stop(self):
        self._running = False


reminder_scheduler = ReminderScheduler()
