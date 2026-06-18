"""Model registry — create models by name (docs/02 ``models/``).

Baselines are registered eagerly. Deep models are registered with *lazy* factories so importing
the registry (and the rest of the ML core) never requires PyTorch; torch is only imported when a
deep model is actually created.
"""

from __future__ import annotations

from collections.abc import Callable

from fasal.models import baseline
from fasal.models.base import RiskModel

_REGISTRY: dict[str, Callable[..., RiskModel]] = {}


def register(name: str) -> Callable[[Callable[..., RiskModel]], Callable[..., RiskModel]]:
    """Decorator/registrar for a model factory."""

    def _register(factory: Callable[..., RiskModel]) -> Callable[..., RiskModel]:
        _REGISTRY[name] = factory
        return factory

    return _register


def create(name: str, **kwargs) -> RiskModel:
    """Instantiate a registered model by name."""
    if name not in _REGISTRY:
        raise KeyError(f"unknown model '{name}'; available: {available()}")
    return _REGISTRY[name](**kwargs)


def available() -> list[str]:
    return sorted(_REGISTRY)


# --- baselines (eager) ---
register("rf")(baseline.random_forest)
register("gbm")(baseline.gradient_boosting)
register("svm")(baseline.svm)
register("pls-da")(baseline.pls_da)


# --- deep models (lazy: torch only needed at creation) ---
def _deep_factory(kind: str) -> Callable[..., RiskModel]:
    def factory(**kwargs) -> RiskModel:
        from fasal.models.deep import build_model

        return build_model(kind, **kwargs)

    return factory


register("cnn1d")(_deep_factory("cnn1d"))
register("fusion")(_deep_factory("fusion"))
