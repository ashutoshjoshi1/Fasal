"""Probability/score calibration (docs/04 §4): map raw model output to a calibrated risk score.

A calibrated score makes "0.86" mean the same thing across crops/seasons, which is what the
risk-class thresholds in the output contract assume.
"""

from __future__ import annotations

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression


class ScoreCalibrator:
    """Fit a monotone mapping from raw scores to calibrated probabilities."""

    def __init__(self, method: str = "isotonic"):
        if method not in {"isotonic", "sigmoid"}:
            raise ValueError("method must be 'isotonic' or 'sigmoid'")
        self.method = method
        self._isotonic: IsotonicRegression | None = None
        self._logistic: LogisticRegression | None = None

    def fit(self, scores: np.ndarray, y: np.ndarray) -> ScoreCalibrator:
        scores = np.asarray(scores, dtype=float).ravel()
        y = np.asarray(y).ravel()
        if self.method == "isotonic":
            self._isotonic = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0).fit(scores, y)
        else:
            self._logistic = LogisticRegression().fit(scores.reshape(-1, 1), y.astype(int))
        return self

    def transform(self, scores: np.ndarray) -> np.ndarray:
        scores = np.asarray(scores, dtype=float).ravel()
        if self.method == "isotonic":
            if self._isotonic is None:
                raise RuntimeError("ScoreCalibrator.transform() called before fit()")
            return np.clip(self._isotonic.predict(scores), 0.0, 1.0)
        if self._logistic is None:
            raise RuntimeError("ScoreCalibrator.transform() called before fit()")
        return self._logistic.predict_proba(scores.reshape(-1, 1))[:, 1]

    def fit_transform(self, scores: np.ndarray, y: np.ndarray) -> np.ndarray:
        return self.fit(scores, y).transform(scores)
