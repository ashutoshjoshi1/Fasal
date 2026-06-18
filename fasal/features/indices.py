"""Vegetation, red-edge, and water spectral indices (science.md §3.3, §8.2).

Each function takes an array with the band axis last — ``(..., B)`` — plus matching
``wavelengths`` (nm), and reduces the band axis: a cube ``(H, W, B) -> (H, W)`` or a set of
spectra ``(N, B) -> (N,)``. Bands are matched to the nearest available wavelength. This module
is intentionally free of any ``fasal.pipeline`` import to keep the dependency graph acyclic.
"""

from __future__ import annotations

import numpy as np

from fasal.core import constants as C


def _nearest(wavelengths: np.ndarray, target_nm: float) -> int:
    wl = np.asarray(wavelengths, dtype=float)
    return int(np.argmin(np.abs(wl - float(target_nm))))


def _band(arr: np.ndarray, wavelengths: np.ndarray, target_nm: float) -> np.ndarray:
    return np.asarray(arr, dtype=float)[..., _nearest(wavelengths, target_nm)]


def _normalized_difference(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    denom = a + b
    with np.errstate(divide="ignore", invalid="ignore"):
        out = (a - b) / denom
    return np.where(denom == 0, 0.0, out)


def ndvi(arr: np.ndarray, wavelengths: np.ndarray, red_nm: float = C.BAND_RED, nir_nm: float = C.BAND_NIR) -> np.ndarray:
    """Normalized Difference Vegetation Index — greenness/biomass proxy."""
    return _normalized_difference(_band(arr, wavelengths, nir_nm), _band(arr, wavelengths, red_nm))


def ndre(arr: np.ndarray, wavelengths: np.ndarray, red_edge_nm: float = C.BAND_RED_EDGE, nir_nm: float = C.BAND_NIR) -> np.ndarray:
    """Normalized Difference Red-Edge — sensitive to canopy stress."""
    return _normalized_difference(_band(arr, wavelengths, nir_nm), _band(arr, wavelengths, red_edge_nm))


def water_band_index(arr: np.ndarray, wavelengths: np.ndarray, nir_nm: float = C.BAND_NIR, water_nm: float = C.BAND_WATER) -> np.ndarray:
    """Moisture proxy using the ~970 nm O-H water feature vs an NIR reference."""
    return _normalized_difference(_band(arr, wavelengths, nir_nm), _band(arr, wavelengths, water_nm))


def red_edge_position(
    arr: np.ndarray,
    wavelengths: np.ndarray,
    lo: float = C.RED_EDGE_RANGE[0],
    hi: float = C.RED_EDGE_RANGE[1],
) -> np.ndarray:
    """Wavelength (nm) of maximum first-derivative within the red-edge region.

    Returns NaN (broadcast over leading dims) when fewer than 3 bands fall in the region.
    """
    wl = np.asarray(wavelengths, dtype=float)
    sel = (wl >= lo) & (wl <= hi)
    arr = np.asarray(arr, dtype=float)
    if int(sel.sum()) < 3:
        return np.full(arr.shape[:-1], np.nan)
    region = arr[..., sel]
    wls = wl[sel]
    grad = np.gradient(region, wls, axis=-1)
    idx = np.argmax(grad, axis=-1)
    return wls[idx]


def index_features(arr: np.ndarray, wavelengths: np.ndarray) -> tuple[np.ndarray, list[str]]:
    """Stack the physically-meaningful indices into a feature array ``(..., K)`` + names."""
    names = ["ndvi", "ndre", "water_band_index", "red_edge_position"]
    feats = np.stack(
        [
            ndvi(arr, wavelengths),
            ndre(arr, wavelengths),
            water_band_index(arr, wavelengths),
            red_edge_position(arr, wavelengths),
        ],
        axis=-1,
    )
    return feats, names
