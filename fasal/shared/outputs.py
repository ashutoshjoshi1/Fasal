"""The risk **output contract** (docs/01 §6, docs/04 §4) — what every prediction carries.

A :class:`RiskPrediction` is never a certification. It pairs a calibrated risk score with a
class, a confidence (incl. OOD), interpretable reason codes, a safety-first action, and
provenance for auditability (docs/03 §5, docs/06 §3).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from fasal.shared.enums import Action, Confidence, ReasonCodeType, RiskClass
from fasal.shared.schemas import GeoPoint


class ReasonCode(BaseModel):
    """One interpretable driver behind a prediction."""

    type: ReasonCodeType
    detail: str
    weight: float = Field(default=1.0, ge=0, le=1)


class Provenance(BaseModel):
    """Per-prediction provenance — required for auditability (docs/06 §3, FR12)."""

    model_version: str
    sensor_id: str | None = None
    calibration_id: str | None = None
    flight_id: str | None = None
    flight_conditions: dict[str, float] | None = None


class RiskPrediction(BaseModel):
    """The canonical screening output for a zone or batch."""

    zone_id: str
    risk_class: RiskClass
    risk_score: float = Field(ge=0, le=1)
    confidence: Confidence
    action: Action
    reason_codes: list[ReasonCode] = Field(default_factory=list)
    provenance: Provenance | None = None

    @classmethod
    def from_score(
        cls,
        zone_id: str,
        risk_score: float,
        confidence: Confidence,
        *,
        reason_codes: list[ReasonCode] | None = None,
        provenance: Provenance | None = None,
    ) -> RiskPrediction:
        """Build a prediction, deriving class and action from the contract mappings."""
        risk_class = RiskClass.from_score(risk_score)
        return cls(
            zone_id=zone_id,
            risk_class=risk_class,
            risk_score=risk_score,
            confidence=confidence,
            action=Action.recommend(risk_class, confidence),
            reason_codes=reason_codes or [],
            provenance=provenance,
        )


class SamplePlanPoint(BaseModel):
    """A single GPS-tagged sampling location."""

    point_id: str
    location: GeoPoint
    target_risk: RiskClass
    rationale: str | None = None


class SamplePlan(BaseModel):
    """A targeted sampling plan spanning low/medium/high zones (docs/05 §4)."""

    flight_id: str
    points: list[SamplePlanPoint] = Field(default_factory=list)

    @property
    def covered_classes(self) -> set[RiskClass]:
        return {p.target_risk for p in self.points}
