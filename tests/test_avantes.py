"""Simulated Avantes driver + point-screening integration tests."""

import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from fasal.hardware import SimulatedAvantes
from fasal.models import create
from fasal.pipeline import PipelineConfig, calibrate_raw, preprocess_spectra
from fasal.services import ScreeningConfig, ScreeningService, build_sample_plan_from_points
from fasal.shared import FieldOfView, SpectrometerSpec


def test_simulated_avantes_outputs_counts_vs_pixel():
    spec = SimulatedAvantes(n_pixels=256, seed=1)
    raw = spec.acquire(50.0)
    assert raw.counts.shape == (256,)
    assert raw.integration_time_ms == 50.0
    assert spec.n_pixels == 256


def test_white_reference_removes_lamp_response():
    spec = SimulatedAvantes(n_pixels=256, seed=1)
    true_reflectance = np.full(256, 0.5)
    sample = spec.acquire(50.0, reflectance=true_reflectance)
    point = calibrate_raw(sample, spec.acquire_white(50.0), spec.acquire_dark(50.0), spec.wavelength_calibration)
    assert np.nanmedian(np.abs(point.reflectance - 0.5)) < 0.05


def test_reflectance_invariant_to_integration_time():
    spec = SimulatedAvantes(n_pixels=128, seed=2)
    true_reflectance = np.clip(np.linspace(0.1, 0.6, 128), 0.0, 1.0)
    for it in (20.0, 50.0, 200.0):
        point = calibrate_raw(
            spec.acquire(it, reflectance=true_reflectance),
            spec.acquire_white(it),
            spec.acquire_dark(it),
            spec.wavelength_calibration,
        )
        assert np.nanmedian(np.abs(point.reflectance - true_reflectance)) < 0.05


def test_avantes_scan_dataset_trains_model():
    spec = SimulatedAvantes(n_pixels=256, seed=7)
    samples, labels, white, dark = spec.scan_dataset(300, 50.0, signal_strength=0.05, seed=0)
    assert samples.counts.shape == (300, 256)
    point = calibrate_raw(samples, white, dark, spec.wavelength_calibration)
    X, _ = preprocess_spectra(point.reflectance, point.wavelengths, PipelineConfig())
    Xtr, Xte, ytr, yte = train_test_split(X, labels, test_size=0.3, random_state=0, stratify=labels)
    model = create("rf").fit(Xtr, ytr)
    assert roc_auc_score(yte, model.predict_proba(Xte)) > 0.8


def test_screen_avantes_end_to_end():
    spec = SimulatedAvantes(n_pixels=256, seed=7)
    samples, labels, white, dark = spec.scan_dataset(300, 50.0, signal_strength=0.05, seed=0)
    config = PipelineConfig()
    point = calibrate_raw(samples, white, dark, spec.wavelength_calibration)
    prepared, _ = preprocess_spectra(point.reflectance, point.wavelengths, config)
    service = ScreeningService(create("rf").fit(prepared, labels), config=ScreeningConfig(pipeline_config=config))

    test, _, white2, dark2 = spec.scan_dataset(30, 50.0, signal_strength=0.05, seed=3)
    result = service.screen_avantes(test, white2, dark2, spec.wavelength_calibration, zone_id="f")
    assert 0.0 <= result.field_prediction.risk_score <= 1.0
    assert len(result.per_point) == 30
    assert result.coverage > 0.0
    assert len(build_sample_plan_from_points(result, per_class=2).points) > 0


def test_spectrometer_spec_schema():
    spec = SpectrometerSpec(
        model="AvaSpec-ULS2048",
        n_pixels=2048,
        wavelength_range_nm=(200, 1100),
        field_of_view=FieldOfView(full_angle_deg=25),
    )
    assert spec.manufacturer == "Avantes"
    assert spec.field_of_view.footprint_diameter_m(10) > 0
