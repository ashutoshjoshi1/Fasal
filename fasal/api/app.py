"""FastAPI application factory (requires the ``api`` extra: ``pip install 'fasal[api]'``).

Security is config-driven (see fasal.core.config / fasal.api.security): CORS origins, API-key auth,
and rate limiting all come from settings. In dev (no FASAL_API_KEYS) auth is open so the demo runs.
"""

from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fasal.api.routes import meta_router, router
from fasal.api.security import RateLimitMiddleware, require_api_key
from fasal.core import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="FASAL backend",
        version="0.1.0",
        description="Drone hyperspectral + AI pesticide-residue risk screening (screening, not certification).",
    )

    origins = [o.strip() for o in settings.allowed_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["X-API-Key", "Content-Type", "Authorization"],
    )
    if settings.rate_limit_enabled:
        app.add_middleware(RateLimitMiddleware, limit=settings.rate_limit_per_minute)

    app.include_router(meta_router)  # open: /health, /models
    app.include_router(router, dependencies=[Depends(require_api_key)])  # data + screen: authenticated
    return app


app = create_app()
