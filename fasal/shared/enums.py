"""Controlled vocabularies and the operational mappings that define the output contract.

The score→class and (class, confidence)→action mappings live here so the *contract* has a
single source of truth (reused by models, services, and the API). See docs/01 §6 and
docs/science.md §5.
"""

from __future__ import annotations

from enum import Enum

from fasal.core import constants as C


class RiskClass(str, Enum):
    """Operational risk classification for a zone or batch."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @classmethod
    def from_score(cls, score: float) -> RiskClass:
        """Map a calibrated risk score in [0, 1] to a class (thresholds in core.constants)."""
        if not 0.0 <= score <= 1.0:
            raise ValueError(f"risk score must be in [0, 1], got {score!r}")
        if score <= C.RISK_LOW_MAX:
            return cls.LOW
        if score <= C.RISK_MEDIUM_MAX:
            return cls.MEDIUM
        return cls.HIGH


class Confidence(str, Enum):
    """Model reliability after uncertainty estimation. Never chemical proof."""

    HIGH = "high"
    UNCERTAIN = "uncertain"
    OOD = "ood"  # out-of-distribution: route to manual sampling / lab


class Action(str, Enum):
    """The single recommended next operational step."""

    CLEAR = "clear"
    COLLECT_SAMPLE = "collect_sample"
    CLOSE_RANGE_SCAN = "close_range_scan"
    SEND_TO_LAB = "send_to_lab"

    @classmethod
    def recommend(cls, risk: RiskClass, confidence: Confidence) -> Action:
        """Safety-first routing: never under-route uncertain/OOD or high-risk zones."""
        if confidence is Confidence.OOD:
            return cls.SEND_TO_LAB if risk is RiskClass.HIGH else cls.COLLECT_SAMPLE
        if risk is RiskClass.HIGH:
            return cls.SEND_TO_LAB
        if risk is RiskClass.MEDIUM:
            return cls.COLLECT_SAMPLE
        # LOW
        return cls.CLEAR if confidence is Confidence.HIGH else cls.CLOSE_RANGE_SCAN


class Modality(str, Enum):
    """Sensing modality of a capture (science.md §3.2)."""

    RGB = "rgb"
    MULTISPECTRAL = "multispectral"
    VNIR = "vnir"
    SWIR = "swir"
    THERMAL = "thermal"


class LabMethod(str, Enum):
    """Confirmatory laboratory reference method (science.md §7)."""

    GC_MSMS = "gc_msms"
    LC_MSMS = "lc_msms"


class ReasonCodeType(str, Enum):
    """Interpretable drivers attached to a prediction (docs/03 §5.4, docs/04 §6)."""

    SWIR_ANOMALY = "swir_anomaly"
    WATER_BAND_ANOMALY = "water_band_anomaly"
    RED_EDGE_SHIFT = "red_edge_shift"
    HIGH_STRESS_PATCH = "high_stress_patch"
    SPRAY_TIMING = "spray_timing"
    SHORT_PHI = "short_pre_harvest_interval"
    PRIOR_HIGH_RISK_PATTERN = "prior_high_risk_pattern"
    LOW_COVERAGE = "low_coverage"
    OOD_INPUT = "ood_input"
