"""Quality control: per-pixel validity masks and a coverage-quality metric (FR3).

Heuristics operate on reflectance cubes: drop saturated, shadow-dominated, and
cloud/specular-bright pixels. ``coverage`` is the fraction of usable pixels — a key
operational signal surfaced in the UI (docs/03, ../design.md).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from fasal.pipeline.cube import HSICube


@dataclass(frozen=True)
class QCResult:
    valid_mask: np.ndarray  # (H, W) bool, True = usable
    coverage: float  # fraction of usable pixels in [0, 1]
    components: dict[str, np.ndarray]  # per-test masks


def brightness(data: np.ndarray) -> np.ndarray:
    """Mean reflectance across bands per pixel — a simple brightness proxy."""
    return np.nanmean(data, axis=-1)


def saturation_valid(data: np.ndarray, sat_value: float) -> np.ndarray:
    """Valid where no band is at/above ``sat_value`` (detector saturation)."""
    return ~(np.asarray(data, dtype=float) >= sat_value).any(axis=-1)


def shadow_valid(data: np.ndarray, min_brightness: float) -> np.ndarray:
    """Valid where brightness is above ``min_brightness`` (rejects deep shadow)."""
    return brightness(data) >= min_brightness


def highlight_valid(data: np.ndarray, max_brightness: float) -> np.ndarray:
    """Valid where brightness is below ``max_brightness`` (rejects cloud/specular)."""
    return brightness(data) <= max_brightness


def compute_qc(
    cube: HSICube,
    *,
    sat_value: float = 1.5,
    min_brightness: float = 0.02,
    max_brightness: float = 1.2,
) -> QCResult:
    """Combine QC tests into a single validity mask and coverage fraction."""
    data = cube.data
    sat = saturation_valid(data, sat_value)
    shadow = shadow_valid(data, min_brightness)
    cloud = highlight_valid(data, max_brightness)
    finite = np.isfinite(data).all(axis=-1)
    valid = sat & shadow & cloud & finite
    if cube.mask is not None:
        valid = valid & cube.mask
    return QCResult(
        valid_mask=valid,
        coverage=float(valid.mean()),
        components={"saturation": sat, "shadow": shadow, "cloud": cloud, "finite": finite},
    )
