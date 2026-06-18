"""The 8 core data objects (docs/03 §1), as validated pydantic models.

These connect drone pixels → field context → lab truth. The *numerical* hyperspectral
array is held separately by :class:`fasal.pipeline.cube.HSICube`; :class:`SpectralCube`
here is the metadata/record for that cube.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, field_validator, model_validator

from fasal.shared.enums import LabMethod, Modality


class GeoPoint(BaseModel):
    """WGS84 location."""

    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    alt_m: float | None = None


class FlightRecord(BaseModel):
    """Traceability & repeatability for one flight (docs/03)."""

    flight_id: str
    captured_at: datetime
    drone_id: str
    sensor_id: str
    altitude_m: float = Field(gt=0)
    speed_ms: float = Field(ge=0, default=0.0)
    overlap_front_pct: float = Field(ge=0, le=100, default=80.0)
    overlap_side_pct: float = Field(ge=0, le=100, default=70.0)
    pilot: str | None = None
    field_id: str | None = None


class SpectralCube(BaseModel):
    """Metadata for a hyperspectral cube (core model input)."""

    cube_id: str
    flight_id: str
    modality: Modality = Modality.VNIR
    wavelengths_nm: list[float]
    n_bands: int
    is_reflectance: bool = False  # True only after radiometric calibration
    orthomosaic_path: str | None = None
    pixel_mask_path: str | None = None
    height: int | None = None
    width: int | None = None

    @model_validator(mode="after")
    def _check_bands(self) -> "SpectralCube":
        if self.n_bands != len(self.wavelengths_nm):
            raise ValueError(
                f"n_bands ({self.n_bands}) != len(wavelengths_nm) ({len(self.wavelengths_nm)})"
            )
        if any(b <= a for a, b in zip(self.wavelengths_nm, self.wavelengths_nm[1:])):
            raise ValueError("wavelengths_nm must be strictly increasing")
        return self


class CalibrationRecord(BaseModel):
    """Reference panels / frames for radiometric calibration (QC & reproducibility)."""

    calibration_id: str
    flight_id: str
    white_reflectance: float = Field(gt=0, le=1, default=0.99)
    panel_reflectance: list[float] | None = None  # optional per-band panel reflectance
    panel_image_path: str | None = None
    irradiance_path: str | None = None
    dark_frame_path: str | None = None
    white_frame_path: str | None = None


class CropMetadata(BaseModel):
    """Domain context for adaptation & interpretation."""

    field_id: str
    crop: str
    variety: str | None = None
    growth_stage: str | None = None
    canopy_condition: str | None = None
    irrigation: str | None = None


class SprayMetadata(BaseModel):
    """Spray-history context — critical for risk prediction."""

    field_id: str
    active_ingredient: str
    application_datetime: datetime
    dose: float | None = Field(default=None, ge=0)
    dose_unit: str | None = None
    formulation: str | None = None
    equipment: str | None = None
    pre_harvest_interval_days: int | None = Field(default=None, ge=0)


class WeatherMetadata(BaseModel):
    """Weather context — explains residue degradation & spectral variability."""

    field_id: str
    observed_at: datetime
    temperature_c: float | None = None
    humidity_pct: float | None = Field(default=None, ge=0, le=100)
    wind_ms: float | None = Field(default=None, ge=0)
    rain_mm: float | None = Field(default=None, ge=0)
    cloud_cover_pct: float | None = Field(default=None, ge=0, le=100)
    solar_radiation: float | None = Field(default=None, ge=0)


class GroundSample(BaseModel):
    """A physical sample connecting drone pixels/zones to lab truth."""

    sample_id: str
    flight_id: str
    location: GeoPoint
    sample_type: str | None = None
    sample_mass_g: float | None = Field(default=None, gt=0)
    chain_of_custody: list[str] = Field(default_factory=list)
    lab_id: str | None = None
    zone_id: str | None = None


class LabResult(BaseModel):
    """Reference label — the chemical ground truth (science.md §7)."""

    sample_id: str
    pesticide: str
    concentration_mg_kg: float = Field(ge=0)
    method: LabMethod
    loq_mg_kg: float | None = Field(default=None, ge=0)
    recovery_pct: float | None = Field(default=None, ge=0)
    uncertainty: float | None = Field(default=None, ge=0)

    @field_validator("concentration_mg_kg")
    @classmethod
    def _finite(cls, v: float) -> float:
        import math

        if not math.isfinite(v):
            raise ValueError("concentration must be finite")
        return v
