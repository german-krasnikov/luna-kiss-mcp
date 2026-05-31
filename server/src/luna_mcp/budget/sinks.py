"""Metric sinks: NullSink (default) and JsonlSink (file-based)."""
import json
import pathlib
from typing import Protocol, runtime_checkable


@runtime_checkable
class Sink(Protocol):
    def emit(self, event: dict) -> None: ...


class NullSink:
    def emit(self, event: dict) -> None:
        pass


class JsonlSink:
    """Buffers events, flushes on batch_size or close(). Fire-and-forget."""

    def __init__(self, path: pathlib.Path, batch_size: int = 10):
        self._path = path
        self._batch: list = []
        self._batch_size = batch_size
        path.parent.mkdir(parents=True, exist_ok=True)

    def emit(self, event: dict) -> None:
        self._batch.append(event)
        if len(self._batch) >= self._batch_size:
            self._flush()

    def _flush(self) -> None:
        if not self._batch:
            return
        try:
            with self._path.open("a") as f:
                for e in self._batch:
                    f.write(json.dumps(e) + "\n")
        except Exception:
            pass
        self._batch.clear()

    def close(self) -> None:
        self._flush()
