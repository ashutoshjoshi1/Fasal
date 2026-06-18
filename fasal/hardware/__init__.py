"""Hardware integration: sensor/drone protocols + a simulated driver."""

from fasal.hardware.interfaces import (
    GNSS,
    Capture,
    Drone,
    IrradianceSensor,
    RGBCamera,
    SpectralSensor,
)
from fasal.hardware.simulated import (
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
    "SimulatedDrone",
    "SimulatedGNSS",
    "SimulatedIrradianceSensor",
    "SimulatedSpectralSensor",
]
