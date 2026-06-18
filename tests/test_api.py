"""Thin API tests (call route handlers directly — no HTTP client dependency)."""

from fasal.api.routes import health, models, screen_synthetic
from fasal.shared.outputs import RiskPrediction


def test_health_ok():
    assert health()["status"] == "ok"


def test_models_lists_rf():
    assert "rf" in models()["available"]


def test_screen_synthetic_returns_prediction():
    pred = screen_synthetic(seed=1)
    assert isinstance(pred, RiskPrediction)
    assert 0.0 <= pred.risk_score <= 1.0
