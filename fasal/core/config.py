"""Runtime settings, loaded from environment (prefix ``FASAL_``) or a ``.env`` file.

The data/storage layer is intentionally light this phase; defaults are local filesystem
and SQLite so the backend boots with no external services. See docs/02-system-architecture.md
for the production targets (PostgreSQL/PostGIS + S3/MinIO).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Process-wide configuration."""

    model_config = SettingsConfigDict(
        env_prefix="FASAL_", env_file=".env", extra="ignore"
    )

    env: str = "dev"
    data_dir: Path = Path("./.data")
    artifacts_dir: Path = Path("./.artifacts")

    # Light data layer (swap to Postgres/PostGIS + S3/MinIO later).
    database_url: str = "sqlite:///./.data/fasal.db"
    object_store_path: Path = Path("./.data/objects")

    # Optional MLOps.
    mlflow_tracking_uri: str | None = None

    # Determinism for synthetic data, model init, MC-dropout sampling, etc.
    random_seed: int = 1337


@lru_cache
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""
    return Settings()
