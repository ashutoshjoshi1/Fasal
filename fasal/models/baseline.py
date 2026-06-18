"""Baseline risk models (docs/04 §3 Stage 0): PLS-DA, Random Forest, SVM, Gradient Boosting.

All wrap scikit-learn behind the :class:`~fasal.models.base.RiskModel` interface, with a
``StandardScaler`` front so feature magnitudes don't dominate. PLS-DA is a ``PLSRegression``
whose continuous output is clipped to [0, 1] as a pseudo-probability.
"""

from __future__ import annotations

import joblib
import numpy as np
from sklearn.cross_decomposition import PLSRegression
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

from fasal.models.base import RiskModel

_SEED = 1337


class SklearnRiskModel(RiskModel):
    """Adapter wrapping any scikit-learn estimator as a :class:`RiskModel`."""

    def __init__(self, estimator, name: str, version: str = "0.1.0", *, scale: bool = True, regression: bool = False):
        self.name = name
        self.version = version
        self.regression = regression
        self.estimator = make_pipeline(StandardScaler(), estimator) if scale else estimator

    def fit(self, X: np.ndarray, y: np.ndarray) -> SklearnRiskModel:
        self.estimator.fit(np.asarray(X, dtype=float), np.asarray(y))
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=float)
        if self.regression:  # PLS regression branch
            return np.clip(self.estimator.predict(X).ravel(), 0.0, 1.0)
        return self.estimator.predict_proba(X)[:, 1]

    def save(self, path: str) -> None:
        joblib.dump(
            {"estimator": self.estimator, "name": self.name, "version": self.version, "regression": self.regression},
            path,
        )

    @classmethod
    def load(cls, path: str) -> SklearnRiskModel:
        blob = joblib.load(path)
        model = cls.__new__(cls)
        model.estimator = blob["estimator"]
        model.name = blob["name"]
        model.version = blob["version"]
        model.regression = blob["regression"]
        return model


def random_forest(name: str = "rf", *, n_estimators: int = 300, random_state: int = _SEED, **kw) -> SklearnRiskModel:
    return SklearnRiskModel(
        RandomForestClassifier(n_estimators=n_estimators, random_state=random_state, **kw), name=name
    )


def gradient_boosting(name: str = "gbm", *, random_state: int = _SEED, **kw) -> SklearnRiskModel:
    return SklearnRiskModel(GradientBoostingClassifier(random_state=random_state, **kw), name=name)


def svm(name: str = "svm", *, random_state: int = _SEED, **kw) -> SklearnRiskModel:
    return SklearnRiskModel(SVC(probability=True, random_state=random_state, **kw), name=name)


def pls_da(name: str = "pls-da", *, n_components: int = 10, **kw) -> SklearnRiskModel:
    return SklearnRiskModel(PLSRegression(n_components=n_components, **kw), name=name, regression=True)
