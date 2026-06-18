"""Radiometric calibration: digital numbers (DN) → surface reflectance (science.md §2).

Two paths are provided: the two-point dark/white normalization and a multi-panel
empirical-line fit (the standard UAV field method), plus downwelling-irradiance
normalization. Reflectance is (approximately) an intrinsic surface property and is the
required input to the AI stages.
"""

from __future__ import annotations

import numpy as np

from fasal.pipeline.cube import HSICube


def two_point_reflectance(
    dn: np.ndarray,
    dark: np.ndarray,
    white: np.ndarray,
    white_reflectance: float | np.ndarray = 0.99,
    *,
    clip: bool = True,
    max_reflectance: float | None = None,
) -> np.ndarray:
    """ρ = (DN - dark) / (white - dark) · ρ_white, elementwise along bands.

    ``dn`` has shape ``(..., B)``; ``dark``/``white`` broadcast against it (e.g. ``(B,)``).
    Bands where ``white == dark`` become NaN. Negative reflectance is clipped to 0 by default.
    """
    dn = np.asarray(dn, dtype=float)
    dark = np.asarray(dark, dtype=float)
    white = np.asarray(white, dtype=float)
    denom = white - dark
    with np.errstate(divide="ignore", invalid="ignore"):
        refl = (dn - dark) / denom * np.asarray(white_reflectance, dtype=float)
    refl = np.where(np.isclose(denom, 0.0), np.nan, refl)
    if clip:
        refl = np.clip(refl, 0.0, max_reflectance)
    return refl


def empirical_line_fit(
    dn_panels: np.ndarray, reflectance_panels: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """Per-band least-squares fit of ``reflectance = gain·DN + offset`` over ≥2 panels.

    ``dn_panels`` is ``(n_panels, B)``; ``reflectance_panels`` is ``(n_panels,)`` (same
    reflectance per band) or ``(n_panels, B)``. Returns ``(gain, offset)`` each ``(B,)``.
    """
    dn = np.asarray(dn_panels, dtype=float)
    ref = np.asarray(reflectance_panels, dtype=float)
    if dn.ndim != 2:
        raise ValueError("dn_panels must be 2-D (n_panels, n_bands)")
    n_panels, n_bands = dn.shape
    if n_panels < 2:
        raise ValueError("empirical line needs >= 2 reference panels")
    if ref.ndim == 1:
        ref = np.repeat(ref[:, None], n_bands, axis=1)
    gain = np.empty(n_bands)
    offset = np.empty(n_bands)
    for b in range(n_bands):
        design = np.vstack([dn[:, b], np.ones(n_panels)]).T
        (g, o), *_ = np.linalg.lstsq(design, ref[:, b], rcond=None)
        gain[b], offset[b] = g, o
    return gain, offset


def apply_empirical_line(
    dn: np.ndarray, gain: np.ndarray, offset: np.ndarray, *, clip: bool = True
) -> np.ndarray:
    """Apply a fitted empirical line: ``reflectance = gain·DN + offset``."""
    out = np.asarray(dn, dtype=float) * np.asarray(gain, dtype=float) + np.asarray(offset, dtype=float)
    return np.clip(out, 0.0, None) if clip else out


def normalize_by_irradiance(dn: np.ndarray, irradiance: np.ndarray) -> np.ndarray:
    """Divide DN by downwelling irradiance per band (corrects changing sunlight)."""
    irr = np.asarray(irradiance, dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.asarray(dn, dtype=float) / np.where(np.isclose(irr, 0.0), np.nan, irr)


def calibrate_cube(
    cube: HSICube,
    dark: np.ndarray,
    white: np.ndarray,
    white_reflectance: float | np.ndarray = 0.99,
) -> HSICube:
    """Two-point calibrate a whole cube and flag it as reflectance."""
    refl = two_point_reflectance(cube.data, dark, white, white_reflectance)
    return cube.with_data(refl, is_reflectance=True)
