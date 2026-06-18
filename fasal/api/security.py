"""API authentication (API key), simple authorization (role per key), and rate limiting.

Dev-friendly: when no API keys are configured, authentication is **open** (with a one-time warning)
so the synthetic demo runs locally with no setup. Configure ``FASAL_API_KEYS`` (e.g.
``"key1:admin,key2:exporter"``) to require an ``X-API-Key`` header in production.

Rate limiting is a single-process sliding window (suitable for dev / a single worker). Behind
multiple workers use a shared store (e.g. ``slowapi`` + Redis).
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from collections.abc import Callable
from threading import Lock

from fastapi import Depends, Header, HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from fasal.core import get_logger, get_settings

_logger = get_logger(__name__)
_warned_open = False


def parse_api_keys(raw: str | None) -> dict[str, str]:
    """Parse ``"key:role,key2:role2"`` into ``{key: role}`` (role defaults to ``"user"``)."""
    keys: dict[str, str] = {}
    for item in (raw or "").split(","):
        item = item.strip()
        if not item:
            continue
        key, _, role = item.partition(":")
        if key.strip():
            keys[key.strip()] = role.strip() or "user"
    return keys


class Principal:
    """The authenticated caller (API key + role)."""

    def __init__(self, key: str, role: str):
        self.key = key
        self.role = role


def require_api_key(x_api_key: str | None = Header(default=None, alias="X-API-Key")) -> Principal:
    """Authenticate via ``X-API-Key``. Open (dev) when no keys are configured."""
    keys = parse_api_keys(get_settings().api_keys)
    if not keys:
        global _warned_open
        if not _warned_open:
            _logger.warning("No FASAL_API_KEYS configured — API authentication is OPEN (dev mode).")
            _warned_open = True
        return Principal(key="dev", role="admin")
    if x_api_key is None or x_api_key not in keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    return Principal(key=x_api_key, role=keys[x_api_key])


def require_role(*roles: str) -> Callable[[Principal], Principal]:
    """Authorization dependency: caller must hold one of ``roles`` (``admin`` always allowed)."""
    allowed = set(roles)

    def checker(principal: Principal = Depends(require_api_key)) -> Principal:
        if principal.role != "admin" and principal.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"role '{principal.role}' is not permitted for this operation",
            )
        return principal

    return checker


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Single-process sliding-window rate limit per client IP (dev / single worker)."""

    def __init__(self, app, *, limit: int, window_s: float = 60.0, exempt: tuple[str, ...] = ("/health",)):
        super().__init__(app)
        self.limit = limit
        self.window_s = window_s
        self.exempt = exempt
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def _allow(self, client: str, now: float) -> tuple[bool, int]:
        with self._lock:
            hits = self._hits[client]
            while hits and hits[0] <= now - self.window_s:
                hits.popleft()
            if len(hits) >= self.limit:
                return False, max(1, int(self.window_s - (now - hits[0])))
            hits.append(now)
            return True, 0

    async def dispatch(self, request: Request, call_next) -> Response:
        if self.limit <= 0 or request.url.path in self.exempt:
            return await call_next(request)
        client = request.client.host if request.client else "unknown"
        allowed, retry_after = self._allow(client, time.monotonic())
        if not allowed:
            return JSONResponse(
                {"detail": "rate limit exceeded"},
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                headers={"Retry-After": str(retry_after)},
            )
        return await call_next(request)
