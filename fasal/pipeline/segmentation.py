"""Canopy/fruit segmentation (FR4). Baseline NDVI-threshold segmenter + a Protocol so
learned segmenters can be dropped in later without changing callers.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import numpy as np

from fasal.features.indices import ndvi
from fasal.pipeline.cube import HSICube


@runtime_checkable
class Segmenter(Protocol):
    """Anything that maps a cube to a boolean ``(H, W)`` vegetation/target mask."""

    def segment(self, cube: HSICube) -> np.ndarray: ...


@dataclass
class NDVISegmenter:
    """Threshold NDVI to isolate vegetation (canopy/fruit) before inference."""

    threshold: float = 0.3

    def segment(self, cube: HSICube) -> np.ndarray:
        return ndvi(cube.data, cube.wavelengths) >= self.threshold


def vegetation_mask(cube: HSICube, threshold: float = 0.3) -> np.ndarray:
    """Convenience wrapper for the NDVI baseline segmenter."""
    return NDVISegmenter(threshold).segment(cube)
