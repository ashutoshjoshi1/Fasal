"""PyTorch deep models (optional extra). Import requires ``pip install 'fasal[deep]'``.

The rest of the ML core does not import this package, so the spectroscopy pipeline and baseline
models work without PyTorch installed.
"""

from __future__ import annotations

try:
    import torch  # noqa: F401
except ImportError as exc:  # pragma: no cover - exercised only without torch
    raise ImportError(
        "PyTorch is required for fasal.models.deep. Install with: pip install 'fasal[deep]'"
    ) from exc

from fasal.models.base import RiskModel
from fasal.models.deep.fusion import FusionModel, FusionRiskModel
from fasal.models.deep.spectral_cnn import Spectral1DCNN, SpectralCNNRiskModel
from fasal.models.deep.train import train_loop


def build_model(kind: str, **kwargs) -> RiskModel:
    """Factory used by the model registry: ``cnn1d`` or ``fusion``."""
    if kind == "cnn1d":
        return SpectralCNNRiskModel(**kwargs)
    if kind == "fusion":
        return FusionRiskModel(**kwargs)
    raise ValueError(f"unknown deep model '{kind}' (expected 'cnn1d' or 'fusion')")


__all__ = [
    "build_model",
    "Spectral1DCNN",
    "SpectralCNNRiskModel",
    "FusionModel",
    "FusionRiskModel",
    "train_loop",
]
