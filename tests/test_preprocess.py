"""Spectral preprocessing tests (science.md §8.1)."""

import numpy as np

from fasal.pipeline import preprocess


def test_snv_gives_zero_mean_unit_std():
    x = np.array([[1.0, 2.0, 3.0, 4.0, 5.0]])
    out = preprocess.snv(x)
    assert np.isclose(out.mean(), 0.0, atol=1e-9)
    assert np.isclose(out.std(), 1.0, atol=1e-9)


def test_snv_constant_spectrum_is_zero():
    out = preprocess.snv(np.full((1, 6), 3.0))
    assert np.allclose(out, 0.0)


def test_savitzky_golay_derivative_of_linear_is_slope():
    x = np.arange(20.0)[None, :]  # slope 1 per sample
    d1 = preprocess.derivative(x, order=1, window=11, polyorder=2)
    assert np.allclose(d1[0, 5:15], 1.0, atol=1e-6)


def test_msc_returns_same_shape_and_reference():
    x = np.random.default_rng(0).uniform(0.1, 0.5, (8, 12))
    out, ref = preprocess.msc(x)
    assert out.shape == x.shape
    assert ref.shape == (12,)


def test_good_band_mask_and_removal():
    wl = np.array([400.0, 1000.0, 1450.0, 2000.0])
    mask = preprocess.good_band_mask(wl, [(1400.0, 1500.0)])
    assert mask.tolist() == [True, True, False, True]
    spectra = np.ones((2, 4))
    filtered, fwl = preprocess.remove_bad_bands(spectra, wl, [(1400.0, 1500.0)])
    assert filtered.shape == (2, 3)
    assert 1450.0 not in fwl.tolist()


def test_resample_interpolates_onto_new_grid():
    wl = np.array([500.0, 600.0, 700.0])
    x = np.array([[0.0, 1.0, 2.0]])
    out = preprocess.resample(x, wl, np.array([550.0, 650.0]))
    assert np.allclose(out, [[0.5, 1.5]])
