"""Contract tests: enums mappings, schema validation, and the output contract."""

import pytest
from pydantic import ValidationError

from fasal.shared import (
    Action,
    Confidence,
    LabMethod,
    LabResult,
    RiskClass,
    RiskPrediction,
    SpectralCube,
)


def test_risk_class_from_score_thresholds():
    assert RiskClass.from_score(0.1) is RiskClass.LOW
    assert RiskClass.from_score(0.5) is RiskClass.MEDIUM
    assert RiskClass.from_score(0.9) is RiskClass.HIGH


def test_risk_score_out_of_range_raises():
    with pytest.raises(ValueError):
        RiskClass.from_score(1.5)


def test_action_is_safety_first():
    # High risk always routes to the lab; OOD never resolves to "clear".
    assert Action.recommend(RiskClass.HIGH, Confidence.HIGH) is Action.SEND_TO_LAB
    assert Action.recommend(RiskClass.LOW, Confidence.OOD) is Action.COLLECT_SAMPLE
    assert Action.recommend(RiskClass.LOW, Confidence.HIGH) is Action.CLEAR
    assert Action.recommend(RiskClass.MEDIUM, Confidence.UNCERTAIN) is Action.COLLECT_SAMPLE


def test_risk_prediction_from_score_derives_class_and_action():
    pred = RiskPrediction.from_score("zoneB", 0.86, Confidence.HIGH)
    assert pred.risk_class is RiskClass.HIGH
    assert pred.action is Action.SEND_TO_LAB
    assert pred.risk_score == 0.86


def test_spectral_cube_band_count_validation():
    with pytest.raises(ValidationError):
        SpectralCube(cube_id="c", flight_id="f", wavelengths_nm=[500.0, 510.0], n_bands=3)


def test_spectral_cube_requires_increasing_wavelengths():
    with pytest.raises(ValidationError):
        SpectralCube(cube_id="c", flight_id="f", wavelengths_nm=[510.0, 500.0], n_bands=2)


def test_lab_result_rejects_negative_concentration():
    with pytest.raises(ValidationError):
        LabResult(sample_id="s", pesticide="x", concentration_mg_kg=-1.0, method=LabMethod.GC_MSMS)
