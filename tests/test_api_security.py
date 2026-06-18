"""API security: key parsing, auth (open-in-dev vs configured), role authz, and rate limiting.

Requires the ``api`` extra (fastapi + httpx for TestClient); skipped otherwise.
"""

from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi import HTTPException  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from fasal.api.app import create_app  # noqa: E402
from fasal.api.security import (  # noqa: E402
    Principal,
    RateLimitMiddleware,
    parse_api_keys,
    require_api_key,
    require_role,
)
from fasal.core import get_settings  # noqa: E402


@pytest.fixture
def settings_env(monkeypatch):
    """Set FASAL_* env vars and clear the cached Settings so changes take effect."""

    def _set(**env: str) -> None:
        for key, value in env.items():
            monkeypatch.setenv(key, value)
        get_settings.cache_clear()

    yield _set
    get_settings.cache_clear()


# --- key parsing (pure) ---


def test_parse_api_keys_basic():
    assert parse_api_keys("k1:admin,k2:exporter") == {"k1": "admin", "k2": "exporter"}


def test_parse_api_keys_default_role_and_blanks():
    assert parse_api_keys("k1, ,k2:lab,") == {"k1": "user", "k2": "lab"}


def test_parse_api_keys_empty():
    assert parse_api_keys(None) == {}
    assert parse_api_keys("") == {}


# --- require_api_key (function-level) ---


def test_require_api_key_open_when_unconfigured(settings_env):
    settings_env(FASAL_API_KEYS="")  # no keys → open dev mode
    principal = require_api_key(x_api_key=None)
    assert principal.role == "admin"


def test_require_api_key_rejects_missing_key(settings_env):
    settings_env(FASAL_API_KEYS="secret:admin")
    with pytest.raises(HTTPException) as exc:
        require_api_key(x_api_key=None)
    assert exc.value.status_code == 401


def test_require_api_key_rejects_wrong_key(settings_env):
    settings_env(FASAL_API_KEYS="secret:admin")
    with pytest.raises(HTTPException) as exc:
        require_api_key(x_api_key="nope")
    assert exc.value.status_code == 401


def test_require_api_key_accepts_valid_key(settings_env):
    settings_env(FASAL_API_KEYS="secret:exporter")
    assert require_api_key(x_api_key="secret").role == "exporter"


# --- require_role (function-level) ---


def test_require_role_admin_always_allowed():
    checker = require_role("exporter")
    assert checker(principal=Principal("k", "admin")).role == "admin"


def test_require_role_allows_listed_role():
    checker = require_role("exporter", "lab")
    assert checker(principal=Principal("k", "lab")).role == "lab"


def test_require_role_forbids_other_role():
    checker = require_role("exporter")
    with pytest.raises(HTTPException) as exc:
        checker(principal=Principal("k", "user"))
    assert exc.value.status_code == 403


# --- rate limiter (unit) ---


def test_rate_limit_allows_then_blocks():
    mw = RateLimitMiddleware(app=None, limit=2, window_s=60.0)
    assert mw._allow("1.1.1.1", 100.0)[0] is True
    assert mw._allow("1.1.1.1", 100.1)[0] is True
    allowed, retry_after = mw._allow("1.1.1.1", 100.2)
    assert allowed is False and retry_after >= 1


def test_rate_limit_window_evicts_old_hits():
    mw = RateLimitMiddleware(app=None, limit=1, window_s=10.0)
    assert mw._allow("x", 0.0)[0] is True
    assert mw._allow("x", 5.0)[0] is False  # within window
    assert mw._allow("x", 11.0)[0] is True  # first hit aged out


# --- end-to-end through the app ---


def test_meta_endpoints_open_even_with_keys(settings_env):
    settings_env(FASAL_API_KEYS="secret:admin")
    client = TestClient(create_app())
    assert client.get("/health").status_code == 200
    assert client.get("/models").status_code == 200


def test_data_endpoint_requires_key_when_configured(settings_env):
    settings_env(FASAL_API_KEYS="secret:admin")
    client = TestClient(create_app())
    assert client.get("/fields").status_code == 401
    assert client.get("/fields", headers={"X-API-Key": "secret"}).status_code == 200


def test_lab_queue_role_enforced(settings_env):
    settings_env(FASAL_API_KEYS="boss:admin,picker:user,lab1:lab")
    client = TestClient(create_app())
    body = {"lot_ids": ["L1"]}
    assert client.post("/lab-queue", json=body, headers={"X-API-Key": "picker"}).status_code == 403
    assert client.post("/lab-queue", json=body, headers={"X-API-Key": "lab1"}).status_code == 200
    assert client.post("/lab-queue", json=body, headers={"X-API-Key": "boss"}).status_code == 200


def test_rate_limit_through_app(settings_env):
    settings_env(FASAL_API_KEYS="", FASAL_RATE_LIMIT_PER_MINUTE="2")
    client = TestClient(create_app())
    assert client.get("/models").status_code == 200
    assert client.get("/models").status_code == 200
    assert client.get("/models").status_code == 429  # third within the window
