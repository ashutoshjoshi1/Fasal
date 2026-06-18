"""Screening service + sampling + hardware integration tests (end-to-end on synthetic data)."""

from fasal.hardware import SimulatedDrone
from fasal.models import create
from fasal.pipeline import PipelineConfig, preprocess_spectra
from fasal.services import ScreeningConfig, ScreeningService, build_sample_plan
from fasal.shared.enums import Confidence, ReasonCodeType
from fasal.shared.outputs import RiskPrediction
from fasal.synth import default_wavelengths, make_cube, make_dataset


def _service() -> ScreeningService:
    config = PipelineConfig()
    wl = default_wavelengths()
    spectra, _, y, _ = make_dataset(400, wl, signal_strength=0.04, seed=0)
    prepared, _ = preprocess_spectra(spectra, wl, config)
    return ScreeningService(create("rf").fit(prepared, y), config=ScreeningConfig(pipeline_config=config))


def test_screen_cube_returns_valid_prediction():
    cube, _ = make_cube(20, 20, default_wavelengths(), seed=3)
    result = _service().screen_cube(cube, zone_id="z")
    assert isinstance(result.prediction, RiskPrediction)
    assert 0.0 <= result.prediction.risk_score <= 1.0
    assert result.pixel_probs.size > 0


def test_high_risk_field_routes_to_action():
    cube, _ = make_cube(20, 20, default_wavelengths(), high_risk_fraction=0.9, signal_strength=0.05, seed=4)
    result = _service().screen_cube(cube)
    assert result.prediction.risk_class.value in {"medium", "high"}


def test_no_vegetation_is_uncertain_low_coverage():
    cube, _ = make_cube(16, 16, default_wavelengths(), vegetation_fraction=0.0, seed=5)
    result = _service().screen_cube(cube)
    assert result.prediction.confidence is Confidence.UNCERTAIN
    assert any(c.type is ReasonCodeType.LOW_COVERAGE for c in result.prediction.reason_codes)


def test_sample_plan_has_points():
    cube, _ = make_cube(20, 20, default_wavelengths(), seed=6)
    result = _service().screen_cube(cube)
    plan = build_sample_plan(result, per_class=2)
    assert len(plan.points) > 0


def test_simulated_drone_capture():
    capture = SimulatedDrone().capture()
    assert capture.cube.n_bands > 0
    assert capture.flight is not None
    assert capture.location is not None
