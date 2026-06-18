"""Runtime settings, loaded from environment (prefix ``FASAL_``) or a ``.env`` file.

The data/storage layer is intentionally light this phase; defaults are local filesystem
and SQLite so the backend boots with no external services. See docs/02-system-architecture.md
for the production targets (PostgreSQL/PostGIS + S3/MinIO).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from fasal.core import constants as C


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

    # Spectrometer (Avantes AvaSpec point sensor) — placeholders; supply your device's values.
    # Raw output is counts vs detector pixel; pixel→wavelength uses the calibration coefficients.
    spectrometer_pixels: int = C.AVANTES_PIXELS
    spectrometer_wavelength_min_nm: float = C.AVANTES_WAVELENGTH_RANGE[0]
    spectrometer_wavelength_max_nm: float = C.AVANTES_WAVELENGTH_RANGE[1]
    default_integration_time_ms: float = C.DEFAULT_INTEGRATION_TIME_MS
    default_filter: str | None = None
    fov_deg: float = C.DEFAULT_FOV_DEG
    wavelength_coefficients: list[float] | None = None  # AVS_GetLambda (ascending); None → linear default

    # API security. Auth is OPEN in dev when api_keys is unset; set FASAL_API_KEYS="key:role,..."
    # (roles: admin/exporter/lab/...) to require an X-API-Key header. CORS + rate limit are config-driven.
    api_keys: str | None = None
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 120


@lru_cache
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""
    return Settings()
