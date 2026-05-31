from __future__ import annotations

import asyncio
import re
from collections import deque
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Subscription:
    kinds: set
    pattern: re.Pattern
    max_events: int
    matches: list = field(default_factory=list)
    future: asyncio.Future = field(default=None)

    def try_match(self, kind: str, evt: dict):
        if kind not in self.kinds:
            return
        text = evt.get("text", "")
        if self.pattern.search(text):
            self.matches.append(evt)
            if len(self.matches) >= self.max_events and not self.future.done():
                self.future.set_result(self.matches)


class EventBus:
    KINDS = ("console", "network", "exception", "frame")

    def __init__(self):
        self._buf: dict[str, deque] = {k: deque(maxlen=200) for k in self.KINDS}
        self._subs: list[Subscription] = []
        self._filters: dict[str, re.Pattern] = {}
        self._seq = 0

    def publish(self, kind: str, evt: dict) -> None:
        if kind not in self.KINDS:
            return
        f = self._filters.get(kind)
        if f and f.search(evt.get("text", "")):
            return
        evt["seq"] = self._seq
        self._seq += 1
        self._buf[kind].append(evt)
        for sub in list(self._subs):
            sub.try_match(kind, evt)

    def snapshot(self, kind: str, count: int = 20, since_seq: int = -1) -> list:
        if kind not in self.KINDS:
            return []
        items = [e for e in self._buf[kind] if e["seq"] > since_seq]
        return items[-count:]

    def subscribe(self, kinds: set, pattern: re.Pattern, max_events: int = 1) -> Subscription:
        sub = Subscription(
            kinds=kinds,
            pattern=pattern,
            max_events=max_events,
            future=asyncio.get_running_loop().create_future(),
        )
        self._subs.append(sub)
        return sub

    def unsubscribe(self, sub: Subscription) -> None:
        try:
            self._subs.remove(sub)
        except ValueError:
            pass

    def set_filter(self, kind: str, drop_regex: Optional[str]) -> None:
        if drop_regex is None:
            self._filters.pop(kind, None)
        else:
            self._filters[kind] = re.compile(drop_regex, re.IGNORECASE)

    def cancel_all(self) -> None:
        for sub in self._subs:
            if not sub.future.done():
                sub.future.cancel()
        self._subs.clear()
