"""Confidence estimation and out-of-distribution (OOD) detection (docs/04 §5; science.md §10).

Confidence is reported as high / uncertain / OOD and is *model reliability, not chemical proof*.
OOD inputs are routed to manual sampling / lab rather than asserted.
"""

from __future__ import annotations

import numpy as np

from fasal.core import constants as C
from fasal.shared.enums import Confidence


def margin_confidence(prob: float, band: tuple[float, float] = C.CONFIDENCE_UNCERTAIN_BAND) -> Confidence:
    """Uncertain near the decision boundary, otherwise high."""
    lo, hi = band
    return Confidence.UNCERTAIN if lo <= float(prob) <= hi else Confidence.HIGH


def assign_confidence(
    prob: float, *, ood: bool = False, band: tuple[float, float] = C.CONFIDENCE_UNCERTAIN_BAND
) -> Confidence:
    """OOD dominates; else margin-based confidence."""
    if ood:
        return Confidence.OOD
    return margin_confidence(prob, band)


def confidence_from_samples(
    prob_samples: np.ndarray,
    *,
    std_threshold: float = 0.15,
    band: tuple[float, float] = C.CONFIDENCE_UNCERTAIN_BAND,
) -> tuple[Confidence, float, float]:
    """Confidence from a set of stochastic predictions (e.g. MC-dropout).

    Returns ``(confidence, mean_prob, std)``. High dispersion → uncertain.
    """
    arr = np.asarray(prob_samples, dtype=float)
    mean = float(arr.mean())
    std = float(arr.std())
    if std >= std_threshold:
        return Confidence.UNCERTAIN, mean, std
    return margin_confidence(mean, band), mean, std


class MahalanobisOODDetector:
    """Flags inputs far from the training feature distribution (regularized Mahalanobis distance)."""

    def __init__(self, quantile: float = C.OOD_TRAIN_QUANTILE, reg: float = 1e-6):
        self.quantile = quantile
        self.reg = reg

    def fit(self, X: np.ndarray) -> MahalanobisOODDetector:
        X = np.asarray(X, dtype=float)
        self.mean_ = X.mean(axis=0)
        cov = np.atleast_2d(np.cov(X, rowvar=False))
        self.inv_ = np.linalg.pinv(cov + self.reg * np.eye(cov.shape[0]))
        distances = self._distance(X)
        self.threshold_ = float(np.quantile(distances, self.quantile))
        return self

    def _distance(self, X: np.ndarray) -> np.ndarray:
        diff = np.asarray(X, dtype=float) - self.mean_
        quad = np.einsum("ij,jk,ik->i", diff, self.inv_, diff)
        return np.sqrt(np.maximum(quad, 0.0))

    def _check_fitted(self) -> None:
        if not hasattr(self, "threshold_"):
            raise RuntimeError("MahalanobisOODDetector must be fitted before use")

    def distance(self, X: np.ndarray) -> np.ndarray:
        self._check_fitted()
        return self._distance(X)

    def predict(self, X: np.ndarray) -> np.ndarray:
        """Boolean OOD flag per row."""
        self._check_fitted()
        return self._distance(X) > self.threshold_
