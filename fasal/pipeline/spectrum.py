"""Point-spectrometer data path for the Avantes (AvaSpec) (science.md §2).

The Avantes is a fiber/point spectrometer: each acquisition is one spectrum of **counts vs
detector pixel** (not wavelength, not an image). Turning that into model-ready reflectance needs:

1. **Pixel → wavelength** via the device's calibration polynomial (Avantes ``AVS_GetLambda`` /
   device file): ``λ(p) = c0 + c1·p + c2·p² + …`` (ascending coefficients).
2. **Dark correction + integration-time normalization** — counts (and dark current) scale with
   integration time, so counts are dark-subtracted and divided by integration time before any
   cross-acquisition comparison.
3. **White-reference reflectance**: ``ρ = (sample − dark)/(white − dark)·ρ_white`` (the standard
   point-spectrometer reflectance; references taken with the same filter).
4. **Filter passband** masking — the active optical filter limits the valid wavelength range.
5. **Field of view (FOV)** — each scan covers a footprint ``≈ 2·d·tan(FOV/2)`` on the ground.

The calibrated reflectance spectra ``(N, B)`` then flow into the same preprocess → features →
models stack used by the imaging path.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
from numpy.polynomial import polynomial as _poly

from fasal.core import constants as C


@dataclass(frozen=True)
class WavelengthCalibration:
    """Pixel→wavelength mapping from ascending polynomial coefficients (Avantes convention)."""

    coefficients: tuple[float, ...]

    def pixel_to_wavelength(self, pixels: np.ndarray) -> np.ndarray:
        return _poly.polyval(np.asarray(pixels, dtype=float), self.coefficients)

    def wavelengths(self, n_pixels: int) -> np.ndarray:
        return self.pixel_to_wavelength(np.arange(n_pixels, dtype=float))

    @classmethod
    def linear(cls, n_pixels: int, lo: float, hi: float) -> WavelengthCalibration:
        """Linear placeholder mapping pixel 0→lo and pixel n-1→hi (until real coeffs are supplied)."""
        return cls((lo, (hi - lo) / (n_pixels - 1)))

    @classmethod
    def avantes_vnir_default(cls, n_pixels: int = C.AVANTES_PIXELS) -> WavelengthCalibration:
        return cls.linear(n_pixels, *C.AVANTES_WAVELENGTH_RANGE)


@dataclass(frozen=True)
class RawSpectrum:
    """Raw Avantes output: counts vs detector pixel, with its acquisition settings.

    ``counts`` is ``(P,)`` for one scan or ``(N, P)`` for a batch of scans.
    """

    counts: np.ndarray
    integration_time_ms: float
    filter_name: str | None = None
    dark_counts: np.ndarray | None = None
    meta: dict = field(default_factory=dict)

    @property
    def n_pixels(self) -> int:
        return int(np.asarray(self.counts).shape[-1])

    @property
    def pixels(self) -> np.ndarray:
        return np.arange(self.n_pixels)


@dataclass(frozen=True)
class PointSpectrum:
    """Calibrated reflectance spectrum/spectra on a wavelength grid."""

    reflectance: np.ndarray  # (B,) or (N, B)
    wavelengths: np.ndarray  # (B,)
    meta: dict = field(default_factory=dict)


def dark_correct(counts: np.ndarray, dark: np.ndarray) -> np.ndarray:
    return np.asarray(counts, dtype=float) - np.asarray(dark, dtype=float)


def per_millisecond(counts: np.ndarray, integration_time_ms: float) -> np.ndarray:
    """Normalize counts to counts/ms (makes acquisitions at different integration times comparable)."""
    if integration_time_ms <= 0:
        raise ValueError("integration_time_ms must be > 0")
    return np.asarray(counts, dtype=float) / float(integration_time_ms)


def counts_to_reflectance(
    sample: np.ndarray,
    white: np.ndarray,
    dark: np.ndarray,
    *,
    white_reflectance: float = 0.99,
    clip: bool = True,
) -> np.ndarray:
    """Same-integration-time reflectance: ``(sample−dark)/(white−dark)·ρ_white``.

    Use when sample, white, and dark share one integration time (the standard reference workflow).
    For acquisitions at different integration times use :func:`calibrate_raw`, which divides each by
    its integration time. Bands where ``white == dark`` become NaN.
    """
    s = dark_correct(sample, dark)
    w = dark_correct(white, dark)
    with np.errstate(divide="ignore", invalid="ignore"):
        refl = s / w * float(white_reflectance)
    refl = np.where(np.isclose(w, 0.0), np.nan, refl)
    if clip:
        refl = np.clip(refl, 0.0, None)
    return refl


def apply_filter(
    wavelengths: np.ndarray, values: np.ndarray, passband: tuple[float, float]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Mask to a filter passband ``(lo, hi)`` nm. Returns ``(values_in_band, wavelengths_in_band, mask)``."""
    wl = np.asarray(wavelengths, dtype=float)
    lo, hi = passband
    mask = (wl >= lo) & (wl <= hi)
    return np.asarray(values, dtype=float)[..., mask], wl[mask], mask


def fov_footprint_diameter(fov_deg: float, distance_m: float) -> float:
    """Ground footprint diameter of a circular FOV at a given distance: ``2·d·tan(FOV/2)``."""
    return 2.0 * float(distance_m) * math.tan(math.radians(float(fov_deg)) / 2.0)


def calibrate_raw(
    sample: RawSpectrum,
    white: RawSpectrum,
    dark: RawSpectrum,
    calibration: WavelengthCalibration,
    *,
    white_reflectance: float = 0.99,
    passband: tuple[float, float] | None = None,
) -> PointSpectrum:
    """Full chain: raw counts (vs pixel) → wavelength + dark/integration-time/white reflectance → filter.

    Each acquisition is dark-corrected and divided by its own integration time, so sample and white
    may use different integration times. A per-acquisition dark on the ``RawSpectrum`` is used when
    present, else the supplied ``dark``.
    """
    wavelengths = calibration.wavelengths(sample.n_pixels)
    sample_dark = sample.dark_counts if sample.dark_counts is not None else dark.counts
    white_dark = white.dark_counts if white.dark_counts is not None else dark.counts
    s = per_millisecond(dark_correct(sample.counts, sample_dark), sample.integration_time_ms)
    w = per_millisecond(dark_correct(white.counts, white_dark), white.integration_time_ms)
    with np.errstate(divide="ignore", invalid="ignore"):
        reflectance = s / w * float(white_reflectance)
    reflectance = np.clip(np.where(np.isclose(w, 0.0), np.nan, reflectance), 0.0, None)
    if passband is not None:
        reflectance, wavelengths, _ = apply_filter(wavelengths, reflectance, passband)
    return PointSpectrum(
        reflectance,
        wavelengths,
        meta={"integration_time_ms": sample.integration_time_ms, "filter": sample.filter_name},
    )
