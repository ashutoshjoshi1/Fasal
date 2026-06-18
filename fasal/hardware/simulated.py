"""Simulated drivers — let the whole stack run with no physical hardware (docs/05).

Backed by :mod:`fasal.synth`. Each class structurally satisfies a protocol in
:mod:`fasal.hardware.interfaces`. Deterministic given a seed (fixed capture timestamp).
"""

from __future__ import annotations

from datetime import datetime

import numpy as np

from fasal.core import constants as C
from fasal.hardware.interfaces import Capture
from fasal.pipeline.cube import HSICube
from fasal.pipeline.spectrum import RawSpectrum, WavelengthCalibration
from fasal.shared.schemas import CalibrationRecord, FlightRecord, GeoPoint
from fasal.synth import default_wavelengths, make_cube, make_dataset


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


class SimulatedAvantes:
    """Simulated Avantes (AvaSpec) point spectrometer — emits **counts vs detector pixel**.

    Emulates a wavelength-dependent lamp response, a dark level (offset + dark current that scales
    with integration time), and shot-like noise, so the raw-counts → reflectance chain
    (:func:`fasal.pipeline.calibrate_raw`) can be exercised end-to-end. Satisfies the
    :class:`~fasal.hardware.interfaces.Spectrometer` protocol. Deterministic per ``seed``.
    """

    def __init__(
        self,
        *,
        n_pixels: int = C.AVANTES_PIXELS,
        wavelength_range: tuple[float, float] = C.AVANTES_WAVELENGTH_RANGE,
        fov_deg: float = C.DEFAULT_FOV_DEG,
        dark_offset: float = 500.0,
        dark_current_per_ms: float = 2.0,
        lamp_peak: float = 50000.0,
        reference_it_ms: float = 50.0,
        seed: int = 1337,
    ):
        self._calibration = WavelengthCalibration.linear(n_pixels, *wavelength_range)
        self._n_pixels = n_pixels
        self.fov_deg = fov_deg
        self.dark_offset = dark_offset
        self.dark_current_per_ms = dark_current_per_ms
        self.reference_it_ms = reference_it_ms
        self._rng = np.random.default_rng(seed)
        wl = self._calibration.wavelengths(n_pixels)
        mid, span = 0.5 * (wl[0] + wl[-1]), (wl[-1] - wl[0])
        # Wavelength-dependent lamp/instrument response (removed by white referencing).
        self._lamp = lamp_peak * (0.3 + 0.7 * np.exp(-0.5 * ((wl - mid) / (0.35 * span)) ** 2))

    @property
    def n_pixels(self) -> int:
        return self._n_pixels

    @property
    def wavelength_calibration(self) -> WavelengthCalibration:
        return self._calibration

    @property
    def wavelengths(self) -> np.ndarray:
        return self._calibration.wavelengths(self._n_pixels)

    def _dark_level(self, integration_time_ms: float) -> float:
        return self.dark_offset + self.dark_current_per_ms * integration_time_ms

    def _counts(self, reflectance: np.ndarray, integration_time_ms: float) -> np.ndarray:
        reflectance = np.asarray(reflectance, dtype=float)
        signal = reflectance * self._lamp * (integration_time_ms / self.reference_it_ms)
        total = signal + self._dark_level(integration_time_ms)
        noise = self._rng.normal(0.0, np.sqrt(np.clip(total, 1.0, None)))
        return np.clip(total + noise, 0.0, None)

    def acquire_dark(self, integration_time_ms: float) -> RawSpectrum:
        level = self._dark_level(integration_time_ms)
        counts = np.clip(level + self._rng.normal(0.0, np.sqrt(level), self._n_pixels), 0.0, None)
        return RawSpectrum(counts, integration_time_ms)

    def acquire_white(self, integration_time_ms: float, white_reflectance: float = 0.99) -> RawSpectrum:
        counts = self._counts(np.full(self._n_pixels, white_reflectance), integration_time_ms)
        return RawSpectrum(counts, integration_time_ms)

    def acquire(self, integration_time_ms: float = 50.0, filter_name: str | None = None, *, reflectance: np.ndarray | None = None) -> RawSpectrum:
        if reflectance is None:
            from fasal.synth.generator import vegetation_template

            reflectance = vegetation_template(self.wavelengths) * self._rng.normal(1.0, 0.05)
        return RawSpectrum(self._counts(reflectance, integration_time_ms), integration_time_ms, filter_name=filter_name)

    def scan_dataset(
        self,
        n_scans: int = 300,
        integration_time_ms: float = 50.0,
        *,
        signal_strength: float = 0.04,
        seed: int = 0,
    ) -> tuple[RawSpectrum, np.ndarray, RawSpectrum, RawSpectrum]:
        """Emit a labelled batch plus white/dark references: ``(samples, labels, white, dark)``.

        ``samples.counts`` is ``(n_scans, n_pixels)``. Feed through :func:`calibrate_raw` then the
        preprocess → model stack.
        """
        reflectance, _wl, labels, _scores = make_dataset(
            n_scans, self.wavelengths, signal_strength=signal_strength, seed=seed
        )
        samples = RawSpectrum(self._counts(reflectance, integration_time_ms), integration_time_ms)
        return samples, labels, self.acquire_white(integration_time_ms), self.acquire_dark(integration_time_ms)
