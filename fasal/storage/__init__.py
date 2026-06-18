"""Light object storage (interface + local filesystem default)."""

from fasal.storage.store import LocalObjectStore, ObjectStore

__all__ = ["ObjectStore", "LocalObjectStore"]
