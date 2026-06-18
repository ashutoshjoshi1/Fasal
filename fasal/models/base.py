"""The ``RiskModel`` interface — the contract every model (baseline or deep) implements.

Models consume a numeric feature matrix ``X`` (N, K) and produce a per-row risk probability in
[0, 1]. Feature construction lives in :mod:`fasal.features`; calibration of the probability into
the output contract's risk score lives in :mod:`fasal.models.scoring`.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import numpy as np


class RiskModel(ABC):
    """Abstract base for risk models."""

    name: str = "risk-model"
    version: str = "0.1.0"

    @abstractmethod
    def fit(self, X: np.ndarray, y: np.ndarray) -> RiskModel:
        """Fit on features ``X`` (N, K) and binary risk labels ``y`` (N,)."""

    @abstractmethod
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Return a risk probability in [0, 1] per row — shape (N,)."""

    def predict(self, X: np.ndarray, threshold: float = 0.5) -> np.ndarray:
        """Binary risk prediction at ``threshold``."""
        return (self.predict_proba(X) >= threshold).astype(int)

    def save(self, path: str) -> None:  # pragma: no cover - overridden by concrete models
        raise NotImplementedError

    @classmethod
    def load(cls, path: str) -> RiskModel:  # pragma: no cover
        raise NotImplementedError
