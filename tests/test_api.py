"""Thin API tests (call route handlers directly — no HTTP client dependency)."""

from fasal.api.routes import (
    LabQueueBody,
    field_zones,
    get_zone,
    health,
    lab_queue,
    list_batches,
    list_fields,
    models,
    screen_synthetic,
)
from fasal.shared.outputs import RiskPrediction


def test_health_ok():
    assert health()["status"] == "ok"


def test_models_lists_rf():
    assert "rf" in models()["available"]


def test_screen_synthetic_returns_prediction():
    pred = screen_synthetic(seed=1)
    assert isinstance(pred, RiskPrediction)
    assert 0.0 <= pred.risk_score <= 1.0


def test_fields_and_zones_endpoints():
    fields = list_fields()
    assert len(fields) >= 1 and fields[0].id
    geojson = field_zones(fields[0].id)
    assert geojson["type"] == "FeatureCollection"
    assert len(geojson["features"]) > 0
    props = geojson["features"][0]["properties"]
    assert {"zone_id", "risk_class", "risk_score", "confidence"} <= props.keys()


def test_zone_detail_and_lab_queue():
    zone_id = field_zones(list_fields()[0].id)["features"][0]["properties"]["zone_id"]
    detail = get_zone(zone_id)
    assert 0.0 <= detail.prediction.risk_score <= 1.0
    assert len(detail.spectrum.wavelengths) == len(detail.spectrum.sample) > 0
    request = lab_queue(LabQueueBody(lot_ids=[list_batches()[0].lot_id]))
    assert len(request.points) == 1
