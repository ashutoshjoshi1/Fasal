"""Targeted sampling-plan generation (FR9, docs/05 §4).

Selects representative low/medium/high points from a screening result so lab samples span the
risk range (not only suspected-high), supporting both calibration and validation.
"""

from __future__ import annotations

from fasal.services.screening import ScreeningResult
from fasal.shared.enums import RiskClass
from fasal.shared.outputs import SamplePlan, SamplePlanPoint
from fasal.shared.schemas import GeoPoint


def build_sample_plan(
    result: ScreeningResult,
    *,
    flight_id: str = "flight",
    origin: GeoPoint | None = None,
    deg_per_pixel: float = 1e-4,
    per_class: int = 2,
) -> SamplePlan:
    """Pick up to ``per_class`` points for each risk class from the per-pixel risk map.

    Pixel (row, col) is mapped to a GPS point as ``origin + (row, col) * deg_per_pixel`` — a
    placeholder geotransform until a real orthomosaic geotransform is wired in.
    """
    origin = origin or GeoPoint(lat=0.0, lon=0.0)
    probs = result.pixel_probs
    indices = result.pixel_indices
    if probs.size == 0:
        return SamplePlan(flight_id=flight_id, points=[])

    pixel_class = [RiskClass.from_score(float(p)) for p in probs]
    points: list[SamplePlanPoint] = []
    counter = 0
    for risk in (RiskClass.HIGH, RiskClass.MEDIUM, RiskClass.LOW):
        selected = [i for i, c in enumerate(pixel_class) if c == risk]
        if not selected:
            continue
        # Prefer the most extreme examples per class for representativeness.
        order = sorted(selected, key=lambda i: -probs[i] if risk is RiskClass.HIGH else probs[i])
        for i in order[:per_class]:
            row, col = int(indices[i, 0]), int(indices[i, 1])
            location = GeoPoint(
                lat=float(origin.lat + row * deg_per_pixel),
                lon=float(origin.lon + col * deg_per_pixel),
            )
            points.append(
                SamplePlanPoint(
                    point_id=f"sp-{counter}",
                    location=location,
                    target_risk=risk,
                    rationale=f"pixel ({row},{col}) risk score {probs[i]:.2f}",
                )
            )
            counter += 1
    return SamplePlan(flight_id=flight_id, points=points)
