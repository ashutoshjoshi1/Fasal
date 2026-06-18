"""FastAPI application factory (requires the ``api`` extra: ``pip install 'fasal[api]'``)."""

from __future__ import annotations

from fastapi import FastAPI

from fasal.api.routes import router


def create_app() -> FastAPI:
    app = FastAPI(
        title="FASAL backend",
        version="0.1.0",
        description="Drone hyperspectral + AI pesticide-residue risk screening (screening, not certification).",
    )
    app.include_router(router)
    return app


app = create_app()
