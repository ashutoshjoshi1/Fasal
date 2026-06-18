"""Screening service — the orchestration that turns a cube into a :class:`RiskPrediction`.

Wires the spectroscopy pipeline → model → confidence/OOD → reason codes, producing both a
field-level prediction (high-recall: a high quantile of pixel probabilities) and a per-pixel risk
map for the dashboard and sampling plan. The model must have been trained on spectra prepared with
the *same* :class:`PipelineConfig` (use :func:`fasal.pipeline.preprocess_spectra`).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from fasal.models.base import RiskModel
from fasal.models.explain import reason_codes_from_bands
from fasal.models.uncertainty import assign_confidence
from fasal.pipeline import (
    PipelineConfig,
    ReflectancePipeline,
    calibrate_raw,
    preprocess_spectra,
)
from fasal.pipeline.cube import HSICube
from fasal.pipeline.spectrum import RawSpectrum, WavelengthCalibration
from fasal.shared.enums import Confidence, ReasonCodeType
from fasal.shared.outputs import Provenance, ReasonCode, RiskPrediction


@dataclass
class ScreeningConfig:
    pipeline_config: PipelineConfig = field(default_factory=PipelineConfig)
    field_quantile: float = 0.9  # high-recall field score = this quantile of pixel probabilities
    model_version: str = "baseline-0.1.0"


@dataclass
class ScreeningResult:
    prediction: RiskPrediction
    pixel_probs: np.ndarray  # (n_analysis,)
    pixel_indices: np.ndarray  # (n_analysis, 2)
    coverage: float
    risk_map: np.ndarray  # (H, W) float, NaN where not analyzed


@dataclass
class PointScreeningResult:
    """Result of screening point spectra (the Avantes path): a field-level prediction plus per-scan."""

    field_prediction: RiskPrediction
    per_point: list[RiskPrediction]
    probs: np.ndarray  # (n_usable,)
    locations: list | None  # aligned to usable scans, if provided
    coverage: float


class ScreeningService:
    def __init__(self, model: RiskModel, *, config: ScreeningConfig | None = None, calibrator=None, ood=None):
        self.model = model
        self.config = config or ScreeningConfig()
        self.calibrator = calibrator
        self.ood = ood
        self.pipeline = ReflectancePipeline(self.config.pipeline_config)

    def screen_cube(
        self,
        cube: HSICube,
        *,
        flight_id: str = "flight",
        zone_id: str = "field",
        dark: np.ndarray | None = None,
        white: np.ndarray | None = None,
        spray_recent: bool = False,
        short_phi: bool = False,
    ) -> ScreeningResult:
        result = self.pipeline.run(cube, dark=dark, white=white)
        risk_map = np.full((cube.height, cube.width), np.nan)
        provenance = Provenance(model_version=self.config.model_version, flight_id=flight_id)

        if result.spectra.shape[0] == 0:
            reason = [ReasonCode(type=ReasonCodeType.LOW_COVERAGE, detail="no vegetation/target pixels detected")]
            prediction = RiskPrediction.from_score(
                zone_id, 0.0, Confidence.UNCERTAIN, reason_codes=reason, provenance=provenance
            )
            return ScreeningResult(prediction, np.empty(0), result.pixel_indices, result.coverage, risk_map)

        probs = np.clip(np.asarray(self.model.predict_proba(result.spectra), dtype=float), 0.0, 1.0)
        if self.calibrator is not None:
            probs = np.clip(self.calibrator.transform(probs), 0.0, 1.0)
        rows, cols = result.pixel_indices[:, 0], result.pixel_indices[:, 1]
        risk_map[rows, cols] = probs

        field_score = float(np.quantile(probs, self.config.field_quantile))
        ood_flag = bool(np.mean(self.ood.predict(result.spectra)) > 0.5) if self.ood is not None else False
        confidence = assign_confidence(field_score, ood=ood_flag)
        reason = reason_codes_from_bands(
            self.model,
            result.wavelengths,
            coverage=result.coverage,
            ood=ood_flag,
            spray_recent=spray_recent,
            short_phi=short_phi,
        )
        prediction = RiskPrediction.from_score(
            zone_id, field_score, confidence, reason_codes=reason, provenance=provenance
        )
        return ScreeningResult(prediction, probs, result.pixel_indices, result.coverage, risk_map)

    def screen_spectra(
        self,
        reflectance: np.ndarray,
        wavelengths: np.ndarray,
        *,
        locations: list | None = None,
        zone_id: str = "field",
        flight_id: str = "flight",
        spray_recent: bool = False,
        short_phi: bool = False,
    ) -> PointScreeningResult:
        """Screen a set of point reflectance spectra ``(N, B)`` — the Avantes path.

        Produces a high-recall field-level prediction (a high quantile of per-scan probabilities)
        plus a per-scan prediction list (the sparse 'map' for a point sensor).
        """
        refl = np.atleast_2d(np.asarray(reflectance, dtype=float))
        spectra, wl = preprocess_spectra(refl, wavelengths, self.config.pipeline_config)
        provenance = Provenance(model_version=self.config.model_version, flight_id=flight_id)
        finite = np.isfinite(spectra).all(axis=1) if spectra.size else np.zeros(0, dtype=bool)
        coverage = float(finite.mean()) if finite.size else 0.0
        if not finite.any():
            reason = [ReasonCode(type=ReasonCodeType.LOW_COVERAGE, detail="no usable spectra")]
            field = RiskPrediction.from_score(
                zone_id, 0.0, Confidence.UNCERTAIN, reason_codes=reason, provenance=provenance
            )
            return PointScreeningResult(field, [], np.empty(0), None, coverage)

        usable = spectra[finite]
        locs = [locations[i] for i in np.where(finite)[0]] if locations is not None else None
        probs = np.clip(np.asarray(self.model.predict_proba(usable), dtype=float), 0.0, 1.0)
        if self.calibrator is not None:
            probs = np.clip(self.calibrator.transform(probs), 0.0, 1.0)
        ood_flag = bool(np.mean(self.ood.predict(usable)) > 0.5) if self.ood is not None else False
        field_score = float(np.quantile(probs, self.config.field_quantile))
        confidence = assign_confidence(field_score, ood=ood_flag)
        reason = reason_codes_from_bands(
            self.model, wl, coverage=coverage, ood=ood_flag, spray_recent=spray_recent, short_phi=short_phi
        )
        field = RiskPrediction.from_score(
            zone_id, field_score, confidence, reason_codes=reason, provenance=provenance
        )
        per_point = [
            RiskPrediction.from_score(
                f"{zone_id}-{i}", float(p), assign_confidence(float(p), ood=ood_flag), provenance=provenance
            )
            for i, p in enumerate(probs)
        ]
        return PointScreeningResult(field, per_point, probs, locs, coverage)

    def screen_avantes(
        self,
        samples: RawSpectrum,
        white: RawSpectrum,
        dark: RawSpectrum,
        calibration: WavelengthCalibration,
        *,
        white_reflectance: float = 0.99,
        passband: tuple[float, float] | None = None,
        locations: list | None = None,
        zone_id: str = "field",
        flight_id: str = "flight",
        spray_recent: bool = False,
        short_phi: bool = False,
    ) -> PointScreeningResult:
        """Calibrate raw Avantes counts (vs pixel) → reflectance, then screen the point spectra."""
        point = calibrate_raw(
            samples, white, dark, calibration, white_reflectance=white_reflectance, passband=passband
        )
        return self.screen_spectra(
            point.reflectance,
            point.wavelengths,
            locations=locations,
            zone_id=zone_id,
            flight_id=flight_id,
            spray_recent=spray_recent,
            short_phi=short_phi,
        )
