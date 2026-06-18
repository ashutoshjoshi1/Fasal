"""Deterministic demo dataset for the console API (built from synth + ScreeningService).

Produces a coherent, region-neutral (global) set of fields, flights, zones (a GeoJSON risk grid),
batches, and a lab queue so the frontend runs against live endpoints without real captures. Built
once and cached. Nothing here is real residue data — it is development scaffolding (docs/03).
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from dataclasses import field as dc_field
from datetime import datetime, timedelta
from functools import lru_cache

import numpy as np
from pydantic import BaseModel

from fasal.models import create
from fasal.models.explain import reason_codes_from_bands
from fasal.models.uncertainty import assign_confidence
from fasal.pipeline import PipelineConfig, preprocess_spectra
from fasal.services import ScreeningConfig, ScreeningService
from fasal.shared.enums import Confidence, RiskClass
from fasal.shared.outputs import Provenance, RiskPrediction
from fasal.synth import default_wavelengths, make_cube, make_dataset, vegetation_template

_BASE = datetime(2024, 6, 1, 12, 0, 0)  # fixed reference (deterministic, no wall clock)
_MODEL_VERSION = "rf-demo-0.1.0"
_GRID = 8  # zone grid per field (NxN)

# Region-neutral demo fields (varied global coordinates).
_FIELDS_SEED = [
    ("fld-001", "Riverbend Vineyard — Block 7", "grapes", 38.29, -122.46),
    ("fld-002", "Sunridge Chilli — Plot 3", "chilli", 36.75, -119.77),
    ("fld-003", "Greenrows Tomato — North", "tomato", 41.88, -87.63),
    ("fld-004", "Eastmere Okra — Field 12", "okra", 30.27, -97.74),
    ("fld-005", "Highland Tea Estate — Slope 4", "tea", -0.52, 37.45),
]
_INGREDIENTS = ["chlorpyrifos", "imidacloprid", "mancozeb", "lambda-cyhalothrin", "azoxystrobin"]


def stable_seed(*parts: object) -> int:
    """Deterministic 32-bit seed from arbitrary parts (independent of PYTHONHASHSEED).

    Builtin ``hash()`` is salted per process, so it must not be used where reproducibility is
    claimed (review finding). This gives the same value across runs.
    """
    digest = hashlib.md5("|".join(str(p) for p in parts).encode()).hexdigest()
    return int(digest[:8], 16)


# --------------------------------------------------------------------------- DTOs
class GeoLocation(BaseModel):
    lat: float
    lon: float


class FieldSummary(BaseModel):
    id: str
    name: str
    crop: str
    location: GeoLocation
    area_ha: float
    risk_class: RiskClass
    risk_score: float
    confidence: Confidence
    coverage: float
    last_flight: datetime


class FieldDetail(FieldSummary):
    bbox: list[float]  # [west, south, east, north]
    prediction: RiskPrediction
    n_zones: int


class FlightRow(BaseModel):
    flight_id: str
    field_id: str
    field_name: str
    captured_at: datetime
    calibration: str  # ok | degraded | failed
    coverage_quality: float
    conditions: str


class BatchRow(BaseModel):
    lot_id: str
    field_id: str
    crop: str
    risk_class: RiskClass
    risk_score: float
    confidence: Confidence
    phi_days: int


class SpectrumTrace(BaseModel):
    wavelengths: list[float]
    sample: list[float]
    control: list[float]


class ZoneMetadata(BaseModel):
    crop: str
    variety: str
    active_ingredient: str
    days_since_spray: int
    pre_harvest_interval_days: int
    temperature_c: float
    humidity_pct: float


class ZoneDetail(BaseModel):
    zone_id: str
    field_id: str
    prediction: RiskPrediction
    spectrum: SpectrumTrace
    metadata: ZoneMetadata


class SampleRequestItem(BaseModel):
    point_id: str
    lot_id: str
    target_risk: RiskClass


class SampleRequest(BaseModel):
    request_id: str
    lot_ids: list[str]
    points: list[SampleRequestItem]
    created_label: str


class RegionalStat(BaseModel):
    region: str
    crop: str
    high_risk_pct: float
    flights: int
    trend: list[float]


# --------------------------------------------------------------------------- store
@dataclass
class _Zone:
    zone_id: str
    field_id: str
    score: float
    confidence: Confidence
    days_since_spray: int
    phi_days: int


@dataclass
class DemoStore:
    fields: list[FieldDetail]
    zones_geojson: dict[str, dict]  # field_id -> GeoJSON FeatureCollection
    zones: dict[str, _Zone]  # zone_id -> zone
    flights: list[FlightRow]
    batches: list[BatchRow]
    crop_by_field: dict[str, str] = dc_field(default_factory=dict)


@lru_cache(maxsize=1)
def build_service() -> ScreeningService:
    config = PipelineConfig()
    wl = default_wavelengths()
    spectra, _, labels, _ = make_dataset(400, wl, signal_strength=0.04, seed=0)
    prepared, _ = preprocess_spectra(spectra, wl, config)
    model = create("rf").fit(prepared, labels)
    return ScreeningService(model, config=ScreeningConfig(pipeline_config=config, model_version=_MODEL_VERSION))


def _grid_ring(bbox: list[float], gi: int, gj: int, n: int) -> list[list[float]]:
    west, south, east, north = bbox
    cw, ch = (east - west) / n, (north - south) / n
    lon0, lon1 = west + gj * cw, west + (gj + 1) * cw
    lat_top, lat_bot = north - gi * ch, north - (gi + 1) * ch
    return [[lon0, lat_top], [lon1, lat_top], [lon1, lat_bot], [lon0, lat_bot], [lon0, lat_top]]


def _block_mean(risk_map: np.ndarray, gi: int, gj: int, n: int) -> float | None:
    h, w = risk_map.shape
    bh, bw = h // n, w // n
    block = risk_map[gi * bh : (gi + 1) * bh, gj * bw : (gj + 1) * bw]
    if not np.isfinite(block).any():
        return None
    return float(np.nanmean(block))


def spectrum_for(score: float, seed: int) -> SpectrumTrace:
    rng = np.random.default_rng(seed)
    wl = default_wavelengths()
    control = vegetation_template(wl)
    residue = np.exp(-0.5 * ((wl - 920.0) / 18.0) ** 2)
    sample = control * rng.normal(1.0, 0.02, wl.size) - 0.05 * score * residue
    return SpectrumTrace(
        wavelengths=[float(x) for x in wl],
        sample=[float(x) for x in np.clip(sample, 0.0, None)],
        control=[float(x) for x in control],
    )


@lru_cache(maxsize=1)
def get_store() -> DemoStore:
    """Build (once) and return the cached demo dataset."""
    service = build_service()
    wl = default_wavelengths()
    fields: list[FieldDetail] = []
    zones_geojson: dict[str, dict] = {}
    zones: dict[str, _Zone] = {}
    flights: list[FlightRow] = []
    batches: list[BatchRow] = []
    crop_by_field: dict[str, str] = {}

    for idx, (fid, name, crop, lat, lon) in enumerate(_FIELDS_SEED):
        crop_by_field[fid] = crop
        rng = np.random.default_rng(1000 + idx)
        cube, _ = make_cube(24, 24, wl, high_risk_fraction=0.2 + 0.12 * idx, signal_strength=0.045, seed=200 + idx)
        result = service.screen_cube(cube, flight_id=f"{fid}-f1", zone_id=fid)
        risk_map = result.risk_map

        half = 0.012
        bbox = [lon - half, lat - half, lon + half, lat + half]
        features: list[dict] = []
        for gi in range(_GRID):
            for gj in range(_GRID):
                score = _block_mean(risk_map, gi, gj, _GRID)
                if score is None:
                    continue
                zid = f"{fid}-z{gi}{gj}"
                conf = assign_confidence(score)
                features.append(
                    {
                        "type": "Feature",
                        "geometry": {"type": "Polygon", "coordinates": [_grid_ring(bbox, gi, gj, _GRID)]},
                        "properties": {
                            "zone_id": zid,
                            "risk_score": round(score, 3),
                            "risk_class": RiskClass.from_score(score).value,
                            "confidence": conf.value,
                        },
                    }
                )
                zones[zid] = _Zone(zid, fid, score, conf, int(rng.integers(1, 21)), int(rng.integers(2, 14)))
        zones_geojson[fid] = {"type": "FeatureCollection", "features": features}

        fields.append(
            FieldDetail(
                id=fid,
                name=name,
                crop=crop,
                location=GeoLocation(lat=lat, lon=lon),
                area_ha=round(float(2.0 + idx * 1.4), 1),
                risk_class=result.prediction.risk_class,
                risk_score=round(float(result.prediction.risk_score), 3),
                confidence=result.prediction.confidence,
                coverage=round(float(result.coverage), 3),
                last_flight=_BASE - timedelta(days=idx),
                bbox=bbox,
                prediction=result.prediction,
                n_zones=len(features),
            )
        )

        # flights (2 per field)
        for k in range(2):
            cal = "ok" if (idx + k) % 4 != 3 else "degraded"
            flights.append(
                FlightRow(
                    flight_id=f"{fid}-f{k+1}",
                    field_id=fid,
                    field_name=name,
                    captured_at=_BASE - timedelta(days=idx, hours=6 * k),
                    calibration=cal,
                    coverage_quality=round(float(np.clip(result.coverage - 0.03 * k, 0, 1)), 3),
                    conditions=["clear · 27°C · wind 2 m/s", "hazy · 31°C · wind 4 m/s"][k % 2],
                )
            )

        # batches (2 lots per field, sampled from zone scores)
        zone_scores = sorted((z.score for z in zones.values() if z.field_id == fid), reverse=True)
        for k in range(2):
            s = float(zone_scores[k * max(1, len(zone_scores) // 3)]) if zone_scores else 0.2
            conf = assign_confidence(s)
            batches.append(
                BatchRow(
                    lot_id=f"{fid}-L{k+1}",
                    field_id=fid,
                    crop=crop,
                    risk_class=RiskClass.from_score(s),
                    risk_score=round(s, 3),
                    confidence=conf,
                    phi_days=int(rng.integers(2, 12)),
                )
            )

    return DemoStore(fields, zones_geojson, zones, flights, batches, crop_by_field)


def zone_detail(zone_id: str) -> ZoneDetail | None:
    store = get_store()
    zone = store.zones.get(zone_id)
    if zone is None:
        return None
    wl = default_wavelengths()
    reasons = reason_codes_from_bands(
        build_service().model,
        wl,
        coverage=0.9,
        spray_recent=zone.days_since_spray < 7,
        short_phi=zone.phi_days < 5,
    )
    prediction = RiskPrediction.from_score(
        zone.zone_id,
        zone.score,
        zone.confidence,
        reason_codes=reasons,
        provenance=Provenance(
            model_version=_MODEL_VERSION, sensor_id="sim-vnir", flight_id=f"{zone.field_id}-f1"
        ),
    )
    seed = stable_seed(zone_id)
    crop = store.crop_by_field.get(zone.field_id, "crop")
    return ZoneDetail(
        zone_id=zone.zone_id,
        field_id=zone.field_id,
        prediction=prediction,
        spectrum=spectrum_for(zone.score, seed),
        metadata=ZoneMetadata(
            crop=crop,
            variety="cv. demo",
            active_ingredient=_INGREDIENTS[seed % len(_INGREDIENTS)],
            days_since_spray=zone.days_since_spray,
            pre_harvest_interval_days=zone.phi_days,
            temperature_c=round(24.0 + (seed % 80) / 10.0, 1),
            humidity_pct=round(40.0 + (seed % 400) / 10.0, 1),
        ),
    )


def make_sample_request(lot_ids: list[str]) -> SampleRequest:
    store = get_store()
    by_lot = {b.lot_id: b for b in store.batches}
    points = [
        SampleRequestItem(point_id=f"sp-{i}", lot_id=lot, target_risk=by_lot[lot].risk_class)
        for i, lot in enumerate(lot_ids)
        if lot in by_lot
    ]
    return SampleRequest(
        request_id=f"req-{stable_seed(*lot_ids) % 10000:04d}",
        lot_ids=list(lot_ids),
        points=points,
        created_label="just now",
    )


def regional_stats() -> list[RegionalStat]:
    store = get_store()
    out: list[RegionalStat] = []
    for f in store.fields:
        field_zone_scores = [z.score for z in store.zones.values() if z.field_id == f.id]
        high = 100.0 * (sum(s > 0.66 for s in field_zone_scores) / max(len(field_zone_scores), 1))
        trend = [round(float(np.clip(high / 100.0 + 0.05 * np.sin(t), 0, 1)), 3) for t in range(6)]
        out.append(
            RegionalStat(region=f.name.split(" — ")[0], crop=f.crop, high_risk_pct=round(high, 1), flights=2, trend=trend)
        )
    return out
