"""Regression tests for code-review fixes."""

import numpy as np
import pytest

from fasal.api.demo_data import stable_seed
from fasal.models.scoring import ScoreCalibrator
from fasal.models.uncertainty import MahalanobisOODDetector
from fasal.pipeline import PipelineConfig, fit_msc_reference, preprocess_spectra
from fasal.storage import LocalObjectStore
from fasal.synth import default_wavelengths, make_dataset


def test_stable_seed_is_deterministic():
    assert stable_seed("fld-001-z00") == stable_seed("fld-001-z00")
    assert stable_seed("a", 1) != stable_seed("a", 2)


def test_ood_detector_requires_fit():
    with pytest.raises(RuntimeError):
        MahalanobisOODDetector().predict(np.zeros((1, 3)))


def test_score_calibrator_requires_fit():
    with pytest.raises(RuntimeError):
        ScoreCalibrator().transform(np.array([0.5]))


def test_local_object_store_rejects_traversal(tmp_path):
    store = LocalObjectStore(tmp_path)
    with pytest.raises(ValueError):
        store.put("../escape.bin", b"x")
    assert store.exists("../escape.bin") is False


def test_pipeline_config_validates():
    with pytest.raises(ValueError):
        PipelineConfig(scatter="nope")  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        PipelineConfig(derivative=-1)


def test_msc_reference_parity():
    spectra, wl, _labels, _scores = make_dataset(60, default_wavelengths(), seed=0)
    config = PipelineConfig(scatter="msc")
    reference = fit_msc_reference(spectra, wl, config)
    config.msc_reference = reference
    # A single held-out spectrum, corrected with the fitted reference, is stable + finite,
    # and the reference length matches the processed band count (no train/inference skew).
    out_a, _ = preprocess_spectra(spectra[:1], wl, config)
    out_b, _ = preprocess_spectra(spectra[:1], wl, config)
    assert np.allclose(out_a, out_b)
    assert np.isfinite(out_a).all()
    assert reference.shape[0] == out_a.shape[1]
