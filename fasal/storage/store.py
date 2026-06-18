"""Object storage (docs/02 Component L): interface + a local-filesystem default.

Spectral cubes/orthomosaics will be cloud-optimized GeoTIFF on S3/MinIO in production; this light
local store keeps the backend runnable with no external services.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Protocol

import numpy as np


class ObjectStore(Protocol):
    def put(self, key: str, data: bytes) -> str: ...
    def get(self, key: str) -> bytes: ...
    def exists(self, key: str) -> bool: ...


class LocalObjectStore:
    """Filesystem-backed object store rooted at a directory."""

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        path = self.root / key
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def put(self, key: str, data: bytes) -> str:
        path = self._path(key)
        path.write_bytes(data)
        return str(path)

    def get(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def exists(self, key: str) -> bool:
        return (self.root / key).exists()

    def put_array(self, key: str, array: np.ndarray) -> str:
        buffer = io.BytesIO()
        np.save(buffer, np.asarray(array))
        return self.put(key, buffer.getvalue())

    def get_array(self, key: str) -> np.ndarray:
        return np.load(io.BytesIO(self.get(key)))
