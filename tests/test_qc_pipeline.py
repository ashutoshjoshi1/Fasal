"""QC, segmentation, and end-to-end pipeline tests on synthetic cubes."""

import numpy as np

from fasal.pipeline import PipelineConfig, ReflectancePipeline, qc
from fasal.pipeline.segmentation import vegetation_mask
from fasal.synth import make_cube


def test_qc_coverage_and_mask_shape():
    cube, _ = make_cube(16, 16, seed=0)
    result = qc.compute_qc(cube)
    assert result.valid_mask.shape == (16, 16)
    assert 0.0 < result.coverage <= 1.0


def test_vegetation_mask_separates_soil():
    cube, info = make_cube(16, 16, seed=0, vegetation_fraction=0.7)
    veg = vegetation_mask(cube, threshold=0.3)
    agreement = float((veg == info["vegetation_mask"]).mean())
    assert agreement > 0.8


def test_pipeline_selects_analysis_pixels():
    cube, _ = make_cube(16, 16, seed=1)
    result = ReflectancePipeline(PipelineConfig()).run(cube)
    assert result.spectra.ndim == 2
    assert result.spectra.shape[0] == result.pixel_indices.shape[0] > 0
    assert 0.0 < result.coverage <= 1.0


def test_pipeline_is_deterministic():
    cube, _ = make_cube(12, 12, seed=2)
    config = PipelineConfig()
    r1 = ReflectancePipeline(config).run(cube)
    r2 = ReflectancePipeline(config).run(cube)
    assert np.allclose(r1.spectra, r2.spectra)
