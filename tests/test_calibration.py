"""Radiometric calibration tests (science.md §2)."""

import numpy as np

from fasal.pipeline import calibration
from fasal.pipeline.cube import HSICube


def test_two_point_reflectance_round_trip():
    # Arrange: DN = reflectance * gain, dark 0, white = gain
    reflectance = np.array([[0.1, 0.2, 0.3, 0.4]])
    dark = np.zeros(4)
    white = np.full(4, 1000.0)
    dn = reflectance * 1000.0
    # Act
    recovered = calibration.two_point_reflectance(dn, dark, white, white_reflectance=1.0)
    # Assert
    assert np.allclose(recovered, reflectance, atol=1e-9)


def test_two_point_reflectance_clips_negatives_and_flags_zero_denominator():
    dn = np.array([[10.0, 10.0]])
    out = calibration.two_point_reflectance(dn, dark=np.array([20.0, 0.0]), white=np.array([20.0, 100.0]))
    assert np.isnan(out[0, 0])  # white == dark → undefined
    assert out[0, 1] >= 0.0  # negatives clipped


def test_empirical_line_fit_recovers_linear_map():
    dn_panels = np.array([[0.0], [1000.0]])
    reflectance_panels = np.array([0.0, 1.0])
    gain, offset = calibration.empirical_line_fit(dn_panels, reflectance_panels)
    assert np.isclose(gain[0], 0.001, atol=1e-6)
    assert np.isclose(offset[0], 0.0, atol=1e-6)


def test_normalize_by_irradiance():
    dn = np.array([[2.0, 4.0]])
    out = calibration.normalize_by_irradiance(dn, irradiance=np.array([2.0, 2.0]))
    assert np.allclose(out, [[1.0, 2.0]])


def test_calibrate_cube_flags_reflectance():
    raw = HSICube(np.full((2, 2, 3), 500.0), np.array([500.0, 600.0, 700.0]))
    cube = calibration.calibrate_cube(raw, dark=np.zeros(3), white=np.full(3, 1000.0), white_reflectance=1.0)
    assert cube.is_reflectance
    assert np.allclose(cube.data, 0.5)
