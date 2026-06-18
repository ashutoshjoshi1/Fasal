"""Synthetic data generation for development and testing (no real captures required)."""

from fasal.synth.generator import (
    default_wavelengths,
    make_cube,
    make_dataset,
    soil_template,
    vegetation_template,
)

__all__ = [
    "default_wavelengths",
    "make_cube",
    "make_dataset",
    "soil_template",
    "vegetation_template",
]
