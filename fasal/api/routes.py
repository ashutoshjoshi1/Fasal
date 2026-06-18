"""Thin HTTP routes (intentionally light this phase).

A demo screening endpoint trains a small baseline on synthetic data once (cached) and screens a
synthetic cube — so the API is runnable end-to-end without uploads, real data, or a database.
"""

from __future__ import annotations

from functools import lru_cache

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

from fasal.api.dataset import (
    DatasetSample,
    DatasetSampleDetail,
    get_dataset,
    render_image,
    sample_detail,
)
from fasal.api.demo_data import (
    BatchRow,
    FieldDetail,
    FieldSummary,
    FlightRow,
    RegionalStat,
    SampleRequest,
    ZoneDetail,
    get_store,
    make_sample_request,
    regional_stats,
    zone_detail,
)
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


# --- console data endpoints (backed by the deterministic demo store) ---


class LabQueueBody(BaseModel):
    lot_ids: list[str]


@router.get("/fields", response_model=list[FieldSummary])
def list_fields():
    return get_store().fields


@router.get("/fields/{field_id}", response_model=FieldDetail)
def get_field(field_id: str):
    for f in get_store().fields:
        if f.id == field_id:
            return f
    raise HTTPException(status_code=404, detail="field not found")


@router.get("/fields/{field_id}/zones")
def field_zones(field_id: str) -> dict:
    """Risk-grid overlay as a GeoJSON FeatureCollection (for the MapLibre fill layer)."""
    geojson = get_store().zones_geojson.get(field_id)
    if geojson is None:
        raise HTTPException(status_code=404, detail="field not found")
    return geojson


@router.get("/zones/{zone_id}", response_model=ZoneDetail)
def get_zone(zone_id: str):
    detail = zone_detail(zone_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="zone not found")
    return detail


@router.get("/flights", response_model=list[FlightRow])
def list_flights():
    return get_store().flights


@router.get("/batches", response_model=list[BatchRow])
def list_batches():
    return get_store().batches


@router.post("/lab-queue", response_model=SampleRequest)
def lab_queue(body: LabQueueBody):
    return make_sample_request(body.lot_ids)


@router.get("/regional", response_model=list[RegionalStat])
def list_regional():
    return regional_stats()


# --- drone-capture image dataset ---


@router.get("/dataset", response_model=list[DatasetSample])
def list_dataset():
    return get_dataset()


@router.get("/dataset/{capture_id}", response_model=DatasetSampleDetail)
def get_dataset_item(capture_id: str):
    detail = sample_detail(capture_id)
    if detail is None:
        raise HTTPException(status_code=404, detail="capture not found")
    return detail


@router.get("/dataset/{capture_id}/image/{kind}.png")
def dataset_image(capture_id: str, kind: str) -> Response:
    png = render_image(capture_id, kind)
    if png is None:
        raise HTTPException(status_code=404, detail="image not found")
    return Response(content=png, media_type="image/png", headers={"Cache-Control": "public, max-age=3600"})
