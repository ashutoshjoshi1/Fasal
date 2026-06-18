"""Compose the raw-cube → AI-ready pipeline (docs/02 Fig 4; science.md §8).

``ReflectancePipeline`` runs: (optional) calibration → QC masking → segmentation → spectral
preprocessing of the analysis pixels, yielding model-ready spectra plus the masks and coverage
needed for the output's reason codes and confidence. ``preprocess_spectra`` is exposed separately
so training data can be prepared with the *exact same* recipe (no train/inference skew).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np

from fasal.core import constants as C
from fasal.core.logging import get_logger
from fasal.pipeline import calibration, preprocess, qc
from fasal.pipeline.cube import HSICube
from fasal.pipeline.segmentation import NDVISegmenter

_logger = get_logger(__name__)


@dataclass
class PipelineConfig:
    """Version-lockable preprocessing recipe (docs/04 §2)."""

    white_reflectance: float = 0.99
    sg_window: int = C.SG_WINDOW
    sg_polyorder: int = C.SG_POLYORDER
    derivative: int = 0  # 0 = smoothing only; >=1 = smoothed derivative
    scatter: Literal["snv", "msc", "none"] = "snv"
    target_wavelengths: np.ndarray | None = None
    bad_bands: tuple[tuple[float, float], ...] = ()
    ndvi_threshold: float = 0.3
    sat_value: float = 1.5
    min_brightness: float = 0.02
    max_brightness: float = 1.2
    # MSC reference spectrum fitted on TRAINING data; required for train/inference parity when
    # scatter="msc" (see fit_msc_reference). None falls back to a per-batch reference (skew risk).
    msc_reference: np.ndarray | None = None

    def __post_init__(self) -> None:
        if self.scatter not in ("snv", "msc", "none"):
            raise ValueError(f"scatter must be 'snv' | 'msc' | 'none'; got {self.scatter!r}")
        if self.derivative < 0:
            raise ValueError(f"derivative order must be >= 0; got {self.derivative}")


@dataclass
class PipelineResult:
    reflectance: HSICube
    valid_mask: np.ndarray  # (H, W) QC-valid
    vegetation_mask: np.ndarray  # (H, W) segmentation
    analysis_mask: np.ndarray  # (H, W) valid & vegetation
    coverage: float
    wavelengths: np.ndarray  # after resample / bad-band removal
    spectra: np.ndarray  # (n_analysis, B') preprocessed analysis spectra
    pixel_indices: np.ndarray  # (n_analysis, 2) row, col of each spectrum
    meta: dict = field(default_factory=dict)


def _pre_scatter(
    spectra: np.ndarray, wl: np.ndarray, config: PipelineConfig
) -> tuple[np.ndarray, np.ndarray]:
    """Recipe steps before scatter correction: bad-band removal, resample, smooth/derivative."""
    if config.bad_bands:
        spectra, wl = preprocess.remove_bad_bands(spectra, wl, config.bad_bands)
    if config.target_wavelengths is not None:
        spectra = preprocess.resample(spectra, wl, config.target_wavelengths)
        wl = np.asarray(config.target_wavelengths, dtype=float)
    if config.derivative and config.derivative > 0:
        spectra = preprocess.derivative(
            spectra, order=config.derivative, window=config.sg_window, polyorder=config.sg_polyorder
        )
    else:
        spectra = preprocess.savitzky_golay(
            spectra, window=config.sg_window, polyorder=config.sg_polyorder, deriv=0
        )
    return spectra, wl


def fit_msc_reference(spectra: np.ndarray, wavelengths: np.ndarray, config: PipelineConfig) -> np.ndarray:
    """Fit the MSC reference spectrum on TRAINING spectra.

    Store the result on ``config.msc_reference`` and reuse the same config at inference so MSC uses
    the same reference both times (avoids the train/serve skew flagged in review).
    """
    spectra = np.asarray(spectra, dtype=float)
    wl = np.asarray(wavelengths, dtype=float)
    if spectra.size == 0:
        return np.zeros(wl.shape, dtype=float)
    pre, _ = _pre_scatter(spectra, wl, config)
    return pre.reshape(-1, pre.shape[-1]).mean(axis=0)


def preprocess_spectra(
    spectra: np.ndarray, wavelengths: np.ndarray, config: PipelineConfig
) -> tuple[np.ndarray, np.ndarray]:
    """Apply the locked recipe to a ``(N, B)`` spectra array. Returns ``(spectra, wavelengths)``.

    Use this on training spectra so they match what the pipeline produces at inference time. For
    ``scatter="msc"`` set ``config.msc_reference`` (via :func:`fit_msc_reference`) so the same
    reference is used at train and inference time.
    """
    spectra = np.asarray(spectra, dtype=float)
    wl = np.asarray(wavelengths, dtype=float)
    if spectra.size == 0:
        return spectra, wl
    spectra, wl = _pre_scatter(spectra, wl, config)
    if config.scatter == "snv":
        spectra = preprocess.snv(spectra)
    elif config.scatter == "msc":
        if config.msc_reference is None:
            _logger.warning(
                "scatter='msc' without a fitted msc_reference; using a per-batch reference "
                "(train/inference skew risk). Set config.msc_reference via fit_msc_reference()."
            )
        spectra, _ = preprocess.msc(spectra, reference=config.msc_reference)
    return spectra, wl


class ReflectancePipeline:
    """Stateful pipeline configured by a :class:`PipelineConfig`."""

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()

    def calibrate(self, raw: HSICube, dark: np.ndarray, white: np.ndarray) -> HSICube:
        return calibration.calibrate_cube(raw, dark, white, self.config.white_reflectance)

    def run(
        self, cube: HSICube, *, dark: np.ndarray | None = None, white: np.ndarray | None = None
    ) -> PipelineResult:
        cfg = self.config
        refl = self.calibrate(cube, dark, white) if (dark is not None and white is not None) else cube

        qc_result = qc.compute_qc(
            refl,
            sat_value=cfg.sat_value,
            min_brightness=cfg.min_brightness,
            max_brightness=cfg.max_brightness,
        )
        veg = NDVISegmenter(cfg.ndvi_threshold).segment(refl)
        analysis = qc_result.valid_mask & veg

        rows, cols = np.where(analysis)
        selected = refl.data[rows, cols, :]
        spectra, wl = preprocess_spectra(selected, refl.wavelengths, cfg)

        return PipelineResult(
            reflectance=refl,
            valid_mask=qc_result.valid_mask,
            vegetation_mask=veg,
            analysis_mask=analysis,
            coverage=qc_result.coverage,
            wavelengths=wl,
            spectra=spectra,
            pixel_indices=np.stack([rows, cols], axis=1) if rows.size else np.empty((0, 2), int),
        )
