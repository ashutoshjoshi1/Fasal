"""Hardware integration: sensor/drone protocols + a simulated driver."""

from fasal.hardware.interfaces import (
    GNSS,
    Capture,
    Drone,
    IrradianceSensor,
    RGBCamera,
    SpectralSensor,
    Spectrometer,
)
from fasal.hardware.simulated import (
    SimulatedAvantes,
    SimulatedDrone,
    SimulatedGNSS,
    SimulatedIrradianceSensor,
    SimulatedSpectralSensor,
)

__all__ = [
    "Capture",
    "Drone",
    "GNSS",
    "IrradianceSensor",
    "RGBCamera",
    "SpectralSensor",
    "Spectrometer",
    "SimulatedAvantes",
    "SimulatedDrone",
    "SimulatedGNSS",
    "SimulatedIrradianceSensor",
    "SimulatedSpectralSensor",
]
