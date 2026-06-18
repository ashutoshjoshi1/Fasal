"""Drone-capture image dataset for the console (rendered from the synthetic captures).

Produces a gallery of imaging samples (RGB composite, NDVI, and risk raster) with metadata and
lab-label status. Field imagery is synthesized with coherent structure (vegetation rows + risk
blobs) and encoded to PNG using only the standard library (no image deps). Development scaffolding —
not real captures (docs/03).
"""

from __future__ import annotations

import struct
import zlib
from datetime import timedelta
from functools import lru_cache

import numpy as np
from pydantic import BaseModel
from scipy.ndimage import gaussian_filter, zoom

from fasal.api.demo_data import GeoLocation, SpectrumTrace, _spectrum_for, get_store
from fasal.shared.enums import RiskClass

_SIZE = 192  # rendered image side (px)


class DatasetSample(BaseModel):
    id: str
    field_id: str
    field_name: str
    crop: str
    captured_at: object  # datetime (serialized by FastAPI)
    sensor: str
    n_bands: int
    gsd_cm: float
    risk_class: RiskClass
    risk_score: float
    label_status: str  # "lab-confirmed" | "sample-queued" | "screened"
    location: GeoLocation


class DatasetSampleDetail(DatasetSample):
    spectrum: SpectrumTrace


# --------------------------------------------------------------------------- imagery
def _layers(seed: int, risk_level: float, size: int = _SIZE) -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    coarse = rng.random((6, 6))
    veg = zoom(coarse, (size / 6, size / 6), order=1)[:size, :size]
    veg = (veg - veg.min()) / (np.ptp(veg) + 1e-9)
    period = size / (12 + seed % 6)
    rows = 0.5 + 0.5 * np.sin(np.arange(size) / period * 2 * np.pi)  # crop rows
    veg = np.clip(0.55 * veg + 0.45 * veg * rows[None, :], 0, 1)

    yy, xx = np.mgrid[0:size, 0:size]
    risk = np.zeros((size, size))
    for _ in range(4):
        cy, cx = rng.random() * size, rng.random() * size
        risk += np.exp(-(((yy - cy) / (size * 0.16)) ** 2 + ((xx - cx) / (size * 0.16)) ** 2))
    risk = gaussian_filter(risk, 4)
    risk = (risk - risk.min()) / (np.ptp(risk) + 1e-9)
    risk = np.clip(risk * risk_level, 0, 1) * (veg > 0.3)
    return veg, risk


def _rgb(veg: np.ndarray, risk: np.ndarray) -> np.ndarray:
    soil = 1 - veg
    r = 60 + 95 * soil + 28 * risk
    g = 80 + 150 * veg - 18 * risk
    b = 52 + 30 * veg
    return np.clip(np.stack([r, g, b], axis=-1), 0, 255).astype(np.uint8)


def _hex(value: str) -> np.ndarray:
    value = value.lstrip("#")
    return np.array([int(value[i : i + 2], 16) for i in (0, 2, 4)], dtype=float)


def _ramp(t: np.ndarray, stops: list[tuple[float, str]]) -> np.ndarray:
    t = np.clip(t, 0, 1)
    out = np.zeros((*t.shape, 3))
    for (p0, c0), (p1, c1) in zip(stops, stops[1:], strict=False):
        mask = (t >= p0) & (t <= p1)
        f = ((t - p0) / (p1 - p0 + 1e-9))[..., None]
        out = np.where(mask[..., None], _hex(c0) * (1 - f) + _hex(c1) * f, out)
    return np.clip(out, 0, 255).astype(np.uint8)


def _ndvi_img(veg: np.ndarray) -> np.ndarray:
    return _ramp(veg, [(0.0, "#b8a06a"), (0.5, "#9fb84a"), (1.0, "#2f7d3a")])


def _risk_img(veg: np.ndarray, risk: np.ndarray) -> np.ndarray:
    img = _ramp(risk, [(0.0, "#5cbf8b"), (0.5, "#e3ab3e"), (1.0, "#d04a36")])
    img[veg <= 0.3] = _hex("#cfc9bf").astype(np.uint8)
    return img


def _encode_png(rgb: np.ndarray) -> bytes:
    arr = np.ascontiguousarray(rgb.astype(np.uint8))
    h, w, _ = arr.shape
    rows = np.zeros((h, 1 + w * 3), dtype=np.uint8)
    rows[:, 1:] = arr.reshape(h, w * 3)

    def chunk(typ: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + typ + data + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)  # 8-bit, color type 2 (RGB)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(rows.tobytes(), 6))
        + chunk(b"IEND", b"")
    )


# --------------------------------------------------------------------------- store
@lru_cache(maxsize=1)
def _build() -> tuple[list[DatasetSample], dict[str, tuple[int, float]]]:
    samples: list[DatasetSample] = []
    render: dict[str, tuple[int, float]] = {}
    for f in get_store().fields:
        for k in range(3):
            seed = (hash((f.id, k)) & 0xFFFF) + 1
            risk_level = float(np.clip(f.risk_score * (0.6 + 0.2 * k) + 0.12, 0, 1))
            rc = RiskClass.from_score(risk_level)
            label = (
                "lab-confirmed"
                if rc is RiskClass.HIGH and k == 0
                else "sample-queued" if rc is not RiskClass.LOW else "screened"
            )
            cid = f"cap-{f.id.split('-')[-1]}-{k + 1}"
            samples.append(
                DatasetSample(
                    id=cid,
                    field_id=f.id,
                    field_name=f.name,
                    crop=f.crop,
                    captured_at=f.last_flight - timedelta(days=k * 3),
                    sensor="VNIR hyperspectral + RGB",
                    n_bands=110,
                    gsd_cm=round(3.0 + k, 1),
                    risk_class=rc,
                    risk_score=round(risk_level, 3),
                    label_status=label,
                    location=f.location,
                )
            )
            render[cid] = (seed, risk_level)
    return samples, render


def get_dataset() -> list[DatasetSample]:
    return _build()[0]


def sample_detail(cid: str) -> DatasetSampleDetail | None:
    samples, render = _build()
    sample = next((s for s in samples if s.id == cid), None)
    if sample is None:
        return None
    seed, _risk = render[cid]
    return DatasetSampleDetail(**sample.model_dump(), spectrum=_spectrum_for(sample.risk_score, seed))


def render_image(cid: str, kind: str) -> bytes | None:
    params = _build()[1].get(cid)
    if params is None:
        return None
    seed, risk_level = params
    veg, risk = _layers(seed, risk_level)
    if kind == "rgb":
        return _encode_png(_rgb(veg, risk))
    if kind == "ndvi":
        return _encode_png(_ndvi_img(veg))
    if kind == "risk":
        return _encode_png(_risk_img(veg, risk))
    return None
