"""Thin HTTP surface (light this phase). Requires the ``api`` extra (FastAPI/uvicorn)."""

from fasal.api.app import app, create_app

__all__ = ["create_app", "app"]
