"""Repository pattern (common patterns): a storage-agnostic interface + an in-memory default.

Intentionally light this phase (docs decision). The interface lets a Postgres/PostGIS-backed
repository drop in later without touching services. See docs/02-system-architecture.md.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Generic, Protocol, TypeVar

T = TypeVar("T")


class Repository(Protocol[T]):
    def add(self, item: T) -> T: ...
    def get(self, id: str) -> T | None: ...
    def list(self) -> list[T]: ...
    def delete(self, id: str) -> bool: ...


class InMemoryRepository(Generic[T]):
    """Dict-backed repository keyed by a caller-supplied id getter."""

    def __init__(self, id_getter: Callable[[T], str]):
        self._items: dict[str, T] = {}
        self._id = id_getter

    def add(self, item: T) -> T:
        self._items[self._id(item)] = item
        return item

    def get(self, id: str) -> T | None:
        return self._items.get(id)

    def list(self) -> list[T]:
        return list(self._items.values())

    def delete(self, id: str) -> bool:
        return self._items.pop(id, None) is not None

    def __len__(self) -> int:
        return len(self._items)
