"""ML core: model interface, baselines, registry, uncertainty/OOD, calibration, explainability.

PyTorch deep models live in :mod:`fasal.models.deep` and are imported only on demand (the import
here does not require torch).
"""

from fasal.models import baseline, explain, registry, scoring, uncertainty
from fasal.models.base import RiskModel
from fasal.models.registry import available, create, register
from fasal.models.scoring import ScoreCalibrator
from fasal.models.uncertainty import (
    MahalanobisOODDetector,
    assign_confidence,
    confidence_from_samples,
)

__all__ = [
    "RiskModel",
    "baseline",
    "explain",
    "registry",
    "scoring",
    "uncertainty",
    "available",
    "create",
    "register",
    "ScoreCalibrator",
    "MahalanobisOODDetector",
    "assign_confidence",
    "confidence_from_samples",
]
