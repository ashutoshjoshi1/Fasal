"""Simulated drivers — let the whole stack run with no physical hardware (docs/05).

Backed by :mod:`fasal.synth`. Each class structurally satisfies a protocol in
:mod:`fasal.hardware.interfaces`. Deterministic given a seed (fixed capture timestamp).
"""

from __future__ import annotations

from datetime import datetime

import numpy as np

from fasal.hardware.interfaces import Capture
from fasal.pipeline.cube import HSICube
from fasal.shared.schemas import CalibrationRecord, FlightRecord, GeoPoint
from fasal.synth import default_wavelengths, make_cube


class SimulatedSpectralSensor:
    def __init__(self, height: int = 32, width: int = 32, wavelengths: np.ndarray | None = None, seed: int = 1337, **cube_kwargs):
        self._wavelengths = default_wavelengths() if wavelengths is None else np.asarray(wavelengths, dtype=float)
        self.height = height
        self.width = width
        self.seed = seed
        self.cube_kwargs = cube_kwargs

    @property
    def wavelengths(self) -> np.ndarray:
        return self._wavelengths

    def capture_cube(self) -> HSICube:
        cube, _ = make_cube(self.height, self.width, self._wavelengths, seed=self.seed, **self.cube_kwargs)
        return cube


class SimulatedGNSS:
    def __init__(self, lat: float = 0.0, lon: float = 0.0):
        self.lat = lat
        self.lon = lon

    def fix(self) -> GeoPoint:
        return GeoPoint(lat=self.lat, lon=self.lon)


class SimulatedIrradianceSensor:
    def __init__(self, wavelengths: np.ndarray):
        self._wavelengths = np.asarray(wavelengths, dtype=float)

    def read(self) -> np.ndarray:
        return np.ones_like(self._wavelengths)


class SimulatedDrone:
    """Composes simulated sensors into a :class:`Capture` (satisfies the ``Drone`` protocol)."""

    def __init__(
        self,
        sensor: SimulatedSpectralSensor | None = None,
        gnss: SimulatedGNSS | None = None,
        irradiance: SimulatedIrradianceSensor | None = None,
        *,
        flight_id: str = "sim-flight",
        captured_at: datetime | None = None,
    ):
        self.sensor = sensor or SimulatedSpectralSensor()
        self.gnss = gnss or SimulatedGNSS()
        self.irradiance = irradiance or SimulatedIrradianceSensor(self.sensor.wavelengths)
        self.flight_id = flight_id
        self.captured_at = captured_at or datetime(2024, 1, 1, 12, 0, 0)

    def capture(self) -> Capture:
        cube = self.sensor.capture_cube()
        flight = FlightRecord(
            flight_id=self.flight_id,
            captured_at=self.captured_at,
            drone_id="sim-uav",
            sensor_id="sim-vnir",
            altitude_m=30.0,
            field_id="sim-field",
        )
        calibration = CalibrationRecord(
            calibration_id="sim-cal", flight_id=self.flight_id, white_reflectance=0.99
        )
        return Capture(
            cube=cube,
            rgb=None,
            location=self.gnss.fix(),
            irradiance=self.irradiance.read(),
            calibration=calibration,
            flight=flight,
        )
