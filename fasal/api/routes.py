"""Thin HTTP routes (intentionally light this phase).

A demo screening endpoint trains a small baseline on synthetic data once (cached) and screens a
synthetic cube — so the API is runnable end-to-end without uploads, real data, or a database.
"""

from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter

from fasal.models import available, create
from fasal.pipeline import PipelineConfig, preprocess_spectra
from fasal.services import ScreeningConfig, ScreeningService
from fasal.shared.outputs import RiskPrediction
from fasal.synth import default_wavelengths, make_cube, make_dataset

router = APIRouter()


@lru_cache(maxsize=1)
def _service() -> ScreeningService:
    config = PipelineConfig()
    wavelengths = default_wavelengths()
    spectra, _, labels, _ = make_dataset(400, wavelengths, seed=0)
    prepared, _ = preprocess_spectra(spectra, wavelengths, config)  # train/inference parity
    model = create("rf").fit(prepared, labels)
    return ScreeningService(model, config=ScreeningConfig(pipeline_config=config))


@router.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "fasal", "note": "screening, not certification"}


@router.get("/models")
def models() -> dict:
    return {"available": available()}


@router.post("/screen/synthetic", response_model=RiskPrediction)
def screen_synthetic(seed: int = 1) -> RiskPrediction:
    """Screen a synthetic field and return the risk prediction (demo without real data)."""
    cube, _ = make_cube(24, 24, default_wavelengths(), seed=seed)
    return _service().screen_cube(cube, flight_id=f"sim-{seed}", zone_id="sim-field").prediction
