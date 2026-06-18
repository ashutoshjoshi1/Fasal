"""Light storage + repository tests."""

import numpy as np

from fasal.db import InMemoryRepository
from fasal.storage import LocalObjectStore


def test_local_object_store_bytes(tmp_path):
    store = LocalObjectStore(tmp_path)
    store.put("cubes/a.bin", b"hello")
    assert store.exists("cubes/a.bin")
    assert store.get("cubes/a.bin") == b"hello"


def test_local_object_store_array_roundtrip(tmp_path):
    store = LocalObjectStore(tmp_path)
    arr = np.arange(6).reshape(2, 3)
    store.put_array("cubes/x.npy", arr)
    assert np.array_equal(store.get_array("cubes/x.npy"), arr)


def test_in_memory_repository_crud():
    repo: InMemoryRepository[dict] = InMemoryRepository(lambda item: item["id"])
    repo.add({"id": "x", "v": 1})
    repo.add({"id": "y", "v": 2})
    assert repo.get("x")["v"] == 1
    assert len(repo.list()) == 2
    assert repo.delete("x") is True
    assert repo.delete("missing") is False
    assert len(repo) == 1
