"""Regression guards for the vectorized preprocessing/calibration ops.

Each vectorized routine must match its original per-row/per-band loop (closed-form OLS /
linear interpolation) to floating-point tolerance. The loops are reproduced here as the oracle.
"""

from __future__ import annotations

import numpy as np

from fasal.pipeline.calibration import empirical_line_fit
from fasal.pipeline.preprocess import msc, resample


def _msc_loop(flat: np.ndarray, ref: np.ndarray) -> np.ndarray:
    out = np.empty_like(flat)
    for i in range(flat.shape[0]):
        slope, intercept = np.polyfit(ref, flat[i], 1)
        out[i] = flat[i] - intercept if np.isclose(slope, 0.0) else (flat[i] - intercept) / slope
    return out


def _resample_loop(x: np.ndarray, wl: np.ndarray, tw: np.ndarray) -> np.ndarray:
    flat = x.reshape(-1, x.shape[-1])
    out = np.empty((flat.shape[0], tw.size))
    for i in range(flat.shape[0]):
        out[i] = np.interp(tw, wl, flat[i])
    return out.reshape(*x.shape[:-1], tw.size)


def _eline_loop(dn: np.ndarray, ref: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    n_panels, n_bands = dn.shape
    if ref.ndim == 1:
        ref = np.repeat(ref[:, None], n_bands, axis=1)
    gain, offset = np.empty(n_bands), np.empty(n_bands)
    for b in range(n_bands):
        design = np.vstack([dn[:, b], np.ones(n_panels)]).T
        (g, o), *_ = np.linalg.lstsq(design, ref[:, b], rcond=None)
        gain[b], offset[b] = g, o
    return gain, offset


def test_msc_matches_polyfit_loop():
    rng = np.random.default_rng(0)
    x = rng.normal(0.4, 0.1, (50, 60)) * rng.uniform(0.8, 1.2, (50, 1)) + rng.uniform(-0.05, 0.05, (50, 1))
    ref = x.mean(0)
    got, got_ref = msc(x, ref)
    assert np.allclose(got, _msc_loop(x, ref))
    assert np.allclose(got_ref, ref)


def test_msc_default_reference_3d():
    rng = np.random.default_rng(1)
    cube = rng.normal(0.5, 0.08, (8, 8, 40))
    got, _ = msc(cube)
    flat = cube.reshape(-1, 40)
    expected = _msc_loop(flat, flat.mean(0)).reshape(8, 8, 40)
    assert np.allclose(got, expected)


def test_resample_matches_interp_loop_with_edge_clamping():
    rng = np.random.default_rng(2)
    wl = np.linspace(400, 1000, 80)
    tw = np.linspace(380, 1020, 120)  # extends past both edges → exercises clamping
    spectra = rng.normal(0.3, 0.05, (30, 80))
    assert np.allclose(resample(spectra, wl, tw), _resample_loop(spectra, wl, tw))


def test_empirical_line_matches_lstsq_loop():
    rng = np.random.default_rng(3)
    dn = rng.normal(2000, 400, (5, 70))
    refl_1d = np.array([0.03, 0.12, 0.25, 0.45, 0.6])
    gain, offset = empirical_line_fit(dn, refl_1d)
    e_gain, e_offset = _eline_loop(dn, refl_1d)
    assert np.allclose(gain, e_gain) and np.allclose(offset, e_offset)

    refl_2d = rng.uniform(0.02, 0.6, (5, 70))
    gain2, offset2 = empirical_line_fit(dn, refl_2d)
    e_gain2, e_offset2 = _eline_loop(dn, refl_2d)
    assert np.allclose(gain2, e_gain2) and np.allclose(offset2, e_offset2)
