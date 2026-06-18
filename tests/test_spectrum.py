"""Point-spectrometer (Avantes) calibration tests: counts vs pixel → reflectance."""

import numpy as np

from fasal.pipeline import (
    RawSpectrum,
    WavelengthCalibration,
    apply_filter,
    calibrate_raw,
    counts_to_reflectance,
    fov_footprint_diameter,
)
from fasal.pipeline.spectrum import per_millisecond


def test_wavelength_calibration_linear_endpoints():
    cal = WavelengthCalibration.linear(2048, 200.0, 1100.0)
    wl = cal.wavelengths(2048)
    assert wl.size == 2048
    assert np.isclose(wl[0], 200.0) and np.isclose(wl[-1], 1100.0)


def test_wavelength_calibration_polynomial():
    cal = WavelengthCalibration((100.0, 1.0, 0.001))  # 100 + p + 0.001*p^2
    assert np.isclose(cal.pixel_to_wavelength(np.array([0.0]))[0], 100.0)
    assert np.isclose(cal.pixel_to_wavelength(np.array([10.0]))[0], 100.0 + 10.0 + 0.001 * 100)


def test_counts_to_reflectance_same_it_round_trip():
    r = np.array([0.1, 0.3, 0.5])
    lamp = np.array([1000.0, 2000.0, 1500.0])
    it, dark = 50.0, 600.0
    refl = counts_to_reflectance(r * lamp * it + dark, 0.99 * lamp * it + dark, np.full(3, dark), white_reflectance=0.99)
    assert np.allclose(refl, r, atol=1e-9)


def test_per_millisecond_normalizes_counts():
    assert np.allclose(per_millisecond(np.array([100.0, 200.0]), 50.0), [2.0, 4.0])


def test_calibrate_raw_handles_different_integration_times():
    r = np.array([0.1, 0.2, 0.3, 0.4])
    lamp = np.array([1000.0, 2000.0, 1500.0, 1200.0])
    offset, dc = 500.0, 2.0
    it_s, it_w = 50.0, 100.0
    dark_s, dark_w = offset + dc * it_s, offset + dc * it_w
    sample = RawSpectrum(r * lamp * it_s + dark_s, it_s, dark_counts=np.full(4, dark_s))
    white = RawSpectrum(0.99 * lamp * it_w + dark_w, it_w, dark_counts=np.full(4, dark_w))
    point = calibrate_raw(sample, white, RawSpectrum(np.full(4, dark_s), it_s), WavelengthCalibration.linear(4, 500, 800))
    assert np.allclose(point.reflectance, r, atol=1e-9)
    assert point.wavelengths.size == 4


def test_apply_filter_masks_passband():
    wl = np.array([300.0, 500.0, 700.0, 1200.0])
    values = np.array([[1.0, 2.0, 3.0, 4.0]])
    filtered, fwl, _ = apply_filter(wl, values, (400.0, 1000.0))
    assert fwl.tolist() == [500.0, 700.0]
    assert filtered.tolist() == [[2.0, 3.0]]


def test_fov_footprint_grows_with_distance():
    near = fov_footprint_diameter(25.0, 10.0)
    far = fov_footprint_diameter(25.0, 30.0)
    assert 0 < near < far


def test_raw_spectrum_properties():
    raw = RawSpectrum(np.zeros((5, 512)), 50.0)
    assert raw.n_pixels == 512
    assert raw.pixels.tolist() == list(range(512))
