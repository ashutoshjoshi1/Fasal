"""Spectral preprocessing (science.md §8.1). All ops act along the last (band) axis.

The recipe (smoothing → derivative → scatter correction → band selection) is composed by the
orchestrator and must be version-locked before validation (docs/04 §2).
"""

from __future__ import annotations

import numpy as np
from scipy.signal import savgol_filter

from fasal.core import constants as C


def _odd_window(window: int, n_bands: int) -> int:
    """Largest valid odd Savitzky-Golay window ≤ ``window`` and ≤ ``n_bands`` (min 3)."""
    w = min(window, n_bands if n_bands % 2 == 1 else n_bands - 1)
    if w % 2 == 0:
        w -= 1
    return max(w, 3)


def savitzky_golay(
    x: np.ndarray, window: int = C.SG_WINDOW, polyorder: int = C.SG_POLYORDER, deriv: int = 0
) -> np.ndarray:
    """Savitzky-Golay smoothing (``deriv=0``) or smoothed derivative (``deriv>=1``)."""
    x = np.asarray(x, dtype=float)
    n = x.shape[-1]
    if n < 3:
        return x.copy()
    w = _odd_window(window, n)
    p = min(polyorder, w - 1)
    return savgol_filter(x, w, p, deriv=deriv, axis=-1)


def derivative(
    x: np.ndarray, order: int = 1, window: int = C.SG_WINDOW, polyorder: int = C.SG_POLYORDER
) -> np.ndarray:
    """Smoothed spectral derivative — enhances subtle/overlapping features (science.md §8.1)."""
    if order < 1:
        raise ValueError("derivative order must be >= 1")
    return savitzky_golay(x, window=window, polyorder=polyorder, deriv=order)


def snv(x: np.ndarray) -> np.ndarray:
    """Standard Normal Variate — removes multiplicative scatter per spectrum."""
    x = np.asarray(x, dtype=float)
    mu = x.mean(axis=-1, keepdims=True)
    sd = x.std(axis=-1, keepdims=True)
    with np.errstate(divide="ignore", invalid="ignore"):
        out = (x - mu) / sd
    return np.where(np.isclose(sd, 0.0), 0.0, out)


def msc(x: np.ndarray, reference: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Multiplicative Scatter Correction against a reference (mean spectrum if None).

    For each spectrum fits ``x ≈ slope·ref + intercept`` and returns ``(x - intercept)/slope``.
    Returns ``(corrected, reference)``.
    """
    x = np.asarray(x, dtype=float)
    orig_shape = x.shape
    flat = x.reshape(-1, orig_shape[-1])
    ref = flat.mean(axis=0) if reference is None else np.asarray(reference, dtype=float)
    # Per-spectrum OLS of `flat[i] ≈ slope·ref + intercept`, vectorized (ref is shared across rows):
    #   slope = Σ(ref-ref̄)·flat / Σ(ref-ref̄)²,  intercept = flat̄ - slope·ref̄.
    ref_c = ref - ref.mean()
    denom = float(ref_c @ ref_c)
    slope = (flat @ ref_c) / denom if denom else np.zeros(flat.shape[0])
    slope = slope[:, None]
    intercept = flat.mean(axis=1, keepdims=True) - slope * ref.mean()
    with np.errstate(divide="ignore", invalid="ignore"):
        corrected = (flat - intercept) / slope
    out = np.where(np.isclose(slope, 0.0), flat - intercept, corrected)
    return out.reshape(orig_shape), ref


def resample(x: np.ndarray, wavelengths: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Linearly resample spectra onto a common ``target`` wavelength grid."""
    x = np.asarray(x, dtype=float)
    wl = np.asarray(wavelengths, dtype=float)
    tw = np.asarray(target, dtype=float)
    flat = x.reshape(-1, x.shape[-1])
    # Shared source/target grids → resolve bracketing indices + weights once, apply to all rows.
    # Matches np.interp: linear between neighbours, clamped to edge values outside [wl[0], wl[-1]].
    lo = np.clip(np.searchsorted(wl, tw, side="right") - 1, 0, wl.size - 2)
    hi = lo + 1
    frac = np.clip((tw - wl[lo]) / (wl[hi] - wl[lo]), 0.0, 1.0)
    out = flat[:, lo] * (1.0 - frac) + flat[:, hi] * frac
    return out.reshape(*x.shape[:-1], tw.size)


def good_band_mask(wavelengths: np.ndarray, bad_ranges) -> np.ndarray:
    """Boolean mask of bands NOT inside any ``(lo, hi)`` range (nm) — e.g. water-saturated bands."""
    wl = np.asarray(wavelengths, dtype=float)
    good = np.ones(wl.shape, dtype=bool)
    for lo, hi in bad_ranges:
        good &= ~((wl >= lo) & (wl <= hi))
    return good


def remove_bad_bands(
    x: np.ndarray, wavelengths: np.ndarray, bad_ranges
) -> tuple[np.ndarray, np.ndarray]:
    """Drop bands inside ``bad_ranges``; returns ``(filtered_spectra, filtered_wavelengths)``."""
    good = good_band_mask(wavelengths, bad_ranges)
    return np.asarray(x, dtype=float)[..., good], np.asarray(wavelengths, dtype=float)[good]
