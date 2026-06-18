"""HSICube container tests."""

import numpy as np
import pytest

from fasal.pipeline.cube import HSICube, nearest_band_index


def test_properties_and_band_access():
    wl = np.array([500.0, 600.0, 700.0])
    data = np.zeros((2, 3, 3))
    data[..., 1] = 0.5
    cube = HSICube(data, wl)
    assert (cube.height, cube.width, cube.n_bands, cube.n_pixels) == (2, 3, 3, 6)
    assert cube.band_index(605.0) == 1
    assert np.allclose(cube.band_at(600.0), 0.5)


def test_to_from_2d_roundtrip():
    wl = np.array([500.0, 600.0])
    data = np.arange(8.0).reshape(2, 2, 2)
    cube = HSICube(data, wl)
    assert cube.to_2d().shape == (4, 2)
    rebuilt = HSICube.from_2d(cube.to_2d(), (2, 2), wl)
    assert np.allclose(rebuilt.data, data)


def test_with_data_is_immutable_copy():
    wl = np.array([500.0, 600.0])
    cube = HSICube(np.zeros((1, 1, 2)), wl)
    updated = cube.with_data(np.ones((1, 1, 2)), is_reflectance=True)
    assert updated.is_reflectance and not cube.is_reflectance
    assert np.allclose(cube.data, 0.0)  # original untouched


def test_validation_errors():
    with pytest.raises(ValueError):
        HSICube(np.zeros((2, 2)), np.array([1.0, 2.0]))  # not 3-D
    with pytest.raises(ValueError):
        HSICube(np.zeros((1, 1, 2)), np.array([2.0, 1.0]))  # not increasing


def test_nearest_band_index():
    assert nearest_band_index([400.0, 500.0, 600.0], 510.0) == 1
