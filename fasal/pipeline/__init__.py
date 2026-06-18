"""Spectroscopy science pipeline: calibration → preprocess → QC → segmentation → orchestrate.

See ``docs/science.md`` (§2 calibration, §6 confounds, §8 preprocessing) for the rationale
behind each stage.
"""

from fasal.pipeline import calibration, preprocess, qc
from fasal.pipeline.cube import HSICube, nearest_band_index
from fasal.pipeline.orchestrator import (
    PipelineConfig,
    PipelineResult,
    ReflectancePipeline,
    preprocess_spectra,
)
from fasal.pipeline.qc import QCResult
from fasal.pipeline.segmentation import NDVISegmenter, Segmenter, vegetation_mask
from fasal.pipeline.spectrum import (
    PointSpectrum,
    RawSpectrum,
    WavelengthCalibration,
    apply_filter,
    calibrate_raw,
    counts_to_reflectance,
    fov_footprint_diameter,
)

__all__ = [
    "HSICube",
    "nearest_band_index",
    "calibration",
    "preprocess",
    "qc",
    "QCResult",
    "Segmenter",
    "NDVISegmenter",
    "vegetation_mask",
    "ReflectancePipeline",
    "PipelineConfig",
    "PipelineResult",
    "preprocess_spectra",
    # point-spectrometer (Avantes) path
    "RawSpectrum",
    "PointSpectrum",
    "WavelengthCalibration",
    "calibrate_raw",
    "counts_to_reflectance",
    "apply_filter",
    "fov_footprint_diameter",
]
