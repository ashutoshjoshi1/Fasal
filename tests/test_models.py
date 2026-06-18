"""ML core tests: registry, baselines, calibration, uncertainty/OOD, explainability."""

import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

from fasal.models import (
    MahalanobisOODDetector,
    ScoreCalibrator,
    assign_confidence,
    available,
    confidence_from_samples,
    create,
)
from fasal.models.baseline import SklearnRiskModel
from fasal.models.explain import reason_codes_from_bands, region_for_wavelength
from fasal.shared.enums import Confidence, ReasonCodeType
from fasal.synth import make_dataset


def _split():
    spectra, wl, y, _ = make_dataset(400, signal_strength=0.04, noise=0.015, seed=0)
    return (wl, *train_test_split(spectra, y, test_size=0.3, random_state=0, stratify=y))


def test_registry_lists_baselines_and_deep():
    for name in ("rf", "pls-da", "svm", "gbm", "cnn1d", "fusion"):
        assert name in available()


def test_baseline_learns_signal_on_spectra():
    _, Xtr, Xte, ytr, yte = _split()
    model = create("rf").fit(Xtr, ytr)
    assert roc_auc_score(yte, model.predict_proba(Xte)) > 0.8


def test_baseline_save_load_roundtrip(tmp_path):
    _, Xtr, Xte, ytr, yte = _split()
    model = create("rf").fit(Xtr, ytr)
    path = tmp_path / "model.joblib"
    model.save(str(path))
    reloaded = SklearnRiskModel.load(str(path))
    assert np.allclose(model.predict_proba(Xte), reloaded.predict_proba(Xte))


def test_score_calibrator_outputs_probabilities():
    rng = np.random.default_rng(0)
    scores = rng.random(200)
    y = (scores > 0.5).astype(int)
    out = ScoreCalibrator("isotonic").fit_transform(scores, y)
    assert out.min() >= 0.0 and out.max() <= 1.0


def test_ood_detector_flags_distribution_shift():
    _, Xtr, Xte, ytr, yte = _split()
    detector = MahalanobisOODDetector().fit(Xtr)
    assert detector.predict(Xtr).mean() < 0.2
    assert detector.predict(Xte + 50.0).mean() > 0.8


def test_assign_confidence():
    assert assign_confidence(0.5) is Confidence.UNCERTAIN
    assert assign_confidence(0.95) is Confidence.HIGH
    assert assign_confidence(0.95, ood=True) is Confidence.OOD


def test_confidence_from_samples_flags_dispersion():
    conf, _mean, _std = confidence_from_samples([0.1, 0.9, 0.5, 0.2, 0.8])
    assert conf is Confidence.UNCERTAIN


def test_region_for_wavelength_maps_science_regions():
    assert region_for_wavelength(700.0) is ReasonCodeType.RED_EDGE_SHIFT
    assert region_for_wavelength(1450.0) is ReasonCodeType.WATER_BAND_ANOMALY
    assert region_for_wavelength(2100.0) is ReasonCodeType.SWIR_ANOMALY


def test_reason_codes_include_context_and_bands():
    wl, Xtr, Xte, ytr, yte = _split()
    model = create("rf").fit(Xtr, ytr)
    codes = reason_codes_from_bands(model, wl, coverage=0.4, spray_recent=True)
    types = {c.type for c in codes}
    assert ReasonCodeType.LOW_COVERAGE in types
    assert ReasonCodeType.SPRAY_TIMING in types
