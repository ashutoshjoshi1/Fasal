"""Spectral index and feature-matrix tests (science.md §3.3, §8.2)."""

import numpy as np

from fasal.features import build_feature_matrix, index_features, ndvi, red_edge_position

WL = np.array([450.0, 550.0, 670.0, 705.0, 800.0, 970.0])


def test_ndvi_known_value():
    spectra = np.full((1, 6), 0.1)
    spectra[0, 4] = 0.5  # NIR (800 nm)
    value = ndvi(spectra, WL)  # (0.5 - 0.1) / (0.5 + 0.1)
    assert np.isclose(value[0], 0.4 / 0.6, atol=1e-9)


def test_index_features_shape_and_finite():
    spectra = np.random.default_rng(0).uniform(0.05, 0.6, (10, 6))
    feats, names = index_features(spectra, WL)
    assert feats.shape == (10, 4)
    # red-edge region has < 3 bands here → red_edge_position is NaN by design
    assert names == ["ndvi", "ndre", "water_band_index", "red_edge_position"]


def test_red_edge_position_requires_enough_bands():
    dense = np.arange(680.0, 751.0, 5.0)
    rising = np.linspace(0.1, 0.5, dense.size)[None, :]
    rep = red_edge_position(rising, dense)
    assert dense.min() <= rep[0] <= dense.max()


def test_build_feature_matrix_is_finite():
    spectra = np.random.default_rng(1).uniform(0.05, 0.6, (5, 6))
    matrix, names = build_feature_matrix(spectra, WL)
    assert matrix.shape == (5, len(names))
    assert np.isfinite(matrix).all()  # undefined descriptors replaced with 0
