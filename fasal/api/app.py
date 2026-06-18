"""FastAPI application factory (requires the ``api`` extra: ``pip install 'fasal[api]'``)."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fasal.api.routes import router

# Dev origins for the Next.js console (configure for real deployments).
_ALLOWED_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]


def create_app() -> FastAPI:
    app = FastAPI(
        title="FASAL backend",
        version="0.1.0",
        description="Drone hyperspectral + AI pesticide-residue risk screening (screening, not certification).",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_ALLOWED_ORIGINS,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(router)
    return app


app = create_app()
