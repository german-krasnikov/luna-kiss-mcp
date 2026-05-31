"""SchemaCache: LRU cache for component props. BatchPathCache: per-batch path existence."""
from collections import OrderedDict
from typing import Optional


class SchemaCache:
    """LRU 256 — key=component_type, value=frozenset[prop]. Invalidate on reconnect."""

    def __init__(self, max_size: int = 256) -> None:
        self._max = max_size
        self._data: OrderedDict[str, frozenset] = OrderedDict()

    def get(self, type_name: str) -> Optional[frozenset]:
        if type_name not in self._data:
            return None
        self._data.move_to_end(type_name)
        return self._data[type_name]

    def put(self, type_name: str, props: frozenset) -> None:
        if type_name in self._data:
            self._data.move_to_end(type_name)
        else:
            if len(self._data) >= self._max:
                self._data.popitem(last=False)
        self._data[type_name] = props

    def invalidate_all(self) -> None:
        self._data.clear()


class BatchPathCache(dict):
    """Lives within a single batch call. Path → bool exists."""

    def invalidate(self) -> None:
        self.clear()
