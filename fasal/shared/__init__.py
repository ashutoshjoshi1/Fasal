"""Shared contracts: the 8 data objects, controlled vocabularies, and the output contract."""

from fasal.shared.enums import (
    Action,
    Confidence,
    LabMethod,
    Modality,
    ReasonCodeType,
    RiskClass,
)
from fasal.shared.outputs import (
    Provenance,
    ReasonCode,
    RiskPrediction,
    SamplePlan,
    SamplePlanPoint,
)
from fasal.shared.schemas import (
    AcquisitionSettings,
    CalibrationRecord,
    CropMetadata,
    FieldOfView,
    Filter,
    FlightRecord,
    GeoPoint,
    GroundSample,
    LabResult,
    SpectralCube,
    SpectrometerSpec,
    SprayMetadata,
    WavelengthCalibrationSpec,
    WeatherMetadata,
)

__all__ = [
    # enums
    "Action",
    "Confidence",
    "LabMethod",
    "Modality",
    "ReasonCodeType",
    "RiskClass",
    # data objects
    "CalibrationRecord",
    "CropMetadata",
    "FlightRecord",
    "GeoPoint",
    "GroundSample",
    "LabResult",
    "SpectralCube",
    "SprayMetadata",
    "WeatherMetadata",
    # instrument / acquisition
    "Filter",
    "FieldOfView",
    "WavelengthCalibrationSpec",
    "SpectrometerSpec",
    "AcquisitionSettings",
    # outputs
    "Provenance",
    "ReasonCode",
    "RiskPrediction",
    "SamplePlan",
    "SamplePlanPoint",
]
