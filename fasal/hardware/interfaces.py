"""Hardware integration interfaces (docs/05, docs/02 Component A).

Structural ``Protocol`` types decouple the platform from any specific drone/sensor. A concrete
driver only needs to match these shapes (see :mod:`fasal.hardware.simulated`); real RTK/PPK,
VNIR/SWIR, and irradiance drivers slot in later without touching the pipeline.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

import numpy as np

from fasal.pipeline.cube import HSICube
from fasal.pipeline.spectrum import RawSpectrum, WavelengthCalibration
from fasal.shared.schemas import CalibrationRecord, FlightRecord, GeoPoint


@dataclass
class Capture:
    """One acquisition: the cube plus synchronized RGB, position, irradiance, and records."""

    cube: HSICube
    rgb: np.ndarray | None = None
    location: GeoPoint | None = None
    irradiance: np.ndarray | None = None
    calibration: CalibrationRecord | None = None
    flight: FlightRecord | None = None


@runtime_checkable
class SpectralSensor(Protocol):
    @property
    def wavelengths(self) -> np.ndarray: ...

    def capture_cube(self) -> HSICube: ...


@runtime_checkable
class RGBCamera(Protocol):
    def capture_rgb(self) -> np.ndarray: ...


@runtime_checkable
class GNSS(Protocol):
    def fix(self) -> GeoPoint: ...


@runtime_checkable
class IrradianceSensor(Protocol):
    def read(self) -> np.ndarray: ...


@runtime_checkable
class Spectrometer(Protocol):
    """A point spectrometer producing counts vs detector pixel (e.g. Avantes AvaSpec)."""

    @property
    def n_pixels(self) -> int: ...

    @property
    def wavelength_calibration(self) -> WavelengthCalibration: ...

    def acquire(self, integration_time_ms: float, filter_name: str | None = None) -> RawSpectrum: ...

    def acquire_white(self, integration_time_ms: float) -> RawSpectrum: ...

    def acquire_dark(self, integration_time_ms: float) -> RawSpectrum: ...


@runtime_checkable
class Drone(Protocol):
    """Orchestrates the sensors into a single :class:`Capture`."""

    def capture(self) -> Capture: ...
