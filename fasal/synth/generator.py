"""Synthetic hyperspectral data with a controllable, deliberately *weak* risk signal.

This lets the full pipeline + ML stack run and be tested without real captures or residue
labels (the data reality in docs/03). The "risk" signal is intentionally subtle — mirroring
science.md §4 (residue features are weak and mixed) — so models are non-trivial but imperfect.
Nothing here implies real residue chemistry; it is a stand-in for development only.
"""

from __future__ import annotations

import numpy as np

from fasal.pipeline.cube import HSICube

_WATER_BANDS = (970.0, 1200.0, 1450.0, 1940.0)


def vegetation_template(wavelengths: np.ndarray) -> np.ndarray:
    """A plausible vegetation reflectance curve: low VIS, red-edge rise, NIR plateau, water dips."""
    wl = np.asarray(wavelengths, dtype=float)
    nir_plateau = 0.5
    r = 0.05 + (nir_plateau - 0.05) / (1.0 + np.exp(-(wl - 715.0) / 12.0))  # red-edge logistic
    r += 0.06 * np.exp(-0.5 * ((wl - 550.0) / 25.0) ** 2)  # green bump
    r -= 0.03 * np.exp(-0.5 * ((wl - 430.0) / 20.0) ** 2)  # chlorophyll (blue)
    r -= 0.05 * np.exp(-0.5 * ((wl - 660.0) / 20.0) ** 2)  # chlorophyll (red)
    for center in _WATER_BANDS:
        r -= 0.12 * np.exp(-0.5 * ((wl - center) / 30.0) ** 2)  # water/O-H absorptions
    return np.clip(r, 0.01, 0.9)


def soil_template(wavelengths: np.ndarray) -> np.ndarray:
    """A bright, gently-rising soil curve with NDVI ≈ 0 (so segmentation removes it)."""
    wl = np.asarray(wavelengths, dtype=float)
    return np.clip(0.18 + 0.00015 * (wl - wl.min()), 0.05, 0.6)


def default_wavelengths() -> np.ndarray:
    """VNIR grid (450–995 nm @ 5 nm) — dense enough for red-edge and index features."""
    return np.arange(450.0, 1000.0, 5.0)


def make_dataset(
    n_samples: int = 400,
    wavelengths: np.ndarray | None = None,
    *,
    signal_strength: float = 0.03,
    positive_fraction: float = 0.5,
    noise: float = 0.01,
    seed: int = 1337,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Generate labelled spectra.

    Returns ``(spectra (N, B), wavelengths (B,), labels (N,) in {0,1}, scores (N,))``. High-risk
    spectra carry a weak residue-like absorption plus a subtle red-edge stress shift.
    """
    rng = np.random.default_rng(seed)
    wl = default_wavelengths() if wavelengths is None else np.asarray(wavelengths, dtype=float)
    n_bands = wl.size
    base = vegetation_template(wl)

    labels = (rng.random(n_samples) < positive_fraction).astype(int)
    # Residue-like weak feature near an accessible organic/water band within range.
    residue_center = wl[np.argmin(np.abs(wl - (920.0 if wl.max() < 1000.0 else 2100.0)))]
    residue_feature = np.exp(-0.5 * ((wl - residue_center) / 18.0) ** 2)
    stress_feature = np.exp(-0.5 * ((wl - 700.0) / 15.0) ** 2)

    spectra = np.empty((n_samples, n_bands))
    for i in range(n_samples):
        spec = base * rng.normal(1.0, 0.05)
        spec = spec + rng.normal(0.0, noise, n_bands)
        if labels[i] == 1:
            spec = spec - signal_strength * residue_feature
            spec = spec + 0.4 * signal_strength * stress_feature
        spectra[i] = spec
    spectra = np.clip(spectra, 0.0, None)

    scores = np.clip(labels * 0.7 + 0.15 + rng.normal(0.0, 0.1, n_samples), 0.0, 1.0)
    return spectra, wl, labels, scores


def make_cube(
    height: int = 16,
    width: int = 16,
    wavelengths: np.ndarray | None = None,
    *,
    vegetation_fraction: float = 0.7,
    high_risk_fraction: float = 0.3,
    signal_strength: float = 0.03,
    noise: float = 0.01,
    seed: int = 1337,
) -> tuple[HSICube, dict[str, np.ndarray]]:
    """Generate a synthetic reflectance cube with a mix of soil/vegetation and risk pixels.

    Returns ``(cube, info)`` where ``info`` has ``vegetation_mask`` and ``risk_map`` (1 = high
    risk among vegetation pixels, else 0). Soil pixels have low NDVI so QC/segmentation drop them.
    """
    rng = np.random.default_rng(seed)
    wl = default_wavelengths() if wavelengths is None else np.asarray(wavelengths, dtype=float)
    n_bands = wl.size
    veg_base = vegetation_template(wl)
    soil_base = soil_template(wl)
    residue_center = wl[np.argmin(np.abs(wl - (920.0 if wl.max() < 1000.0 else 2100.0)))]
    residue_feature = np.exp(-0.5 * ((wl - residue_center) / 18.0) ** 2)

    is_veg = rng.random((height, width)) < vegetation_fraction
    is_risk = is_veg & (rng.random((height, width)) < high_risk_fraction)

    data = np.empty((height, width, n_bands))
    for r in range(height):
        for c in range(width):
            if is_veg[r, c]:
                spec = veg_base * rng.normal(1.0, 0.05) + rng.normal(0.0, noise, n_bands)
                if is_risk[r, c]:
                    spec = spec - signal_strength * residue_feature
            else:
                spec = soil_base * rng.normal(1.0, 0.05) + rng.normal(0.0, noise, n_bands)
            data[r, c] = spec
    data = np.clip(data, 0.0, None)

    cube = HSICube(data, wl, is_reflectance=True, meta={"synthetic": True})
    return cube, {"vegetation_mask": is_veg, "risk_map": is_risk.astype(int)}
