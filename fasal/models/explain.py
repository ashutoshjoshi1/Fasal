"""Explainability (docs/03 §5.4, docs/04 §6): feature/band importance → reason codes.

Models train on preprocessed *spectra* (the chemometric standard — the trace signal lives in
specific bands, not in aggregate indices; science.md §8.3). So the primary explanation maps the
most influential **wavelength bands** to science-grounded reason-code types (science.md §3.3/§4):
red-edge → stress, water/O-H bands → moisture/organic anomaly, SWIR → molecular anomaly.

A name-based path (:func:`build_reason_codes`) is also provided for models trained on the named
engineered feature matrix (:func:`fasal.features.build_feature_matrix`).
"""

from __future__ import annotations

import numpy as np

from fasal.core import constants as C
from fasal.shared.enums import ReasonCodeType
from fasal.shared.outputs import ReasonCode

# Named engineered feature → reason-code type.
_FEATURE_REASON: dict[str, ReasonCodeType] = {
    "ndre": ReasonCodeType.RED_EDGE_SHIFT,
    "red_edge_position": ReasonCodeType.RED_EDGE_SHIFT,
    "water_band_index": ReasonCodeType.WATER_BAND_ANOMALY,
    "ndvi": ReasonCodeType.HIGH_STRESS_PATCH,
    "d1_absmax": ReasonCodeType.SWIR_ANOMALY,
    "d1_std": ReasonCodeType.SWIR_ANOMALY,
}


def feature_importance(model) -> np.ndarray | None:
    """Best-effort per-input importance from a fitted sklearn-backed model."""
    estimator = getattr(model, "estimator", model)
    final = estimator.steps[-1][1] if hasattr(estimator, "steps") else estimator
    imp = getattr(final, "feature_importances_", None)
    if imp is None:
        coef = getattr(final, "coef_", None)
        if coef is not None:
            imp = np.abs(np.ravel(coef))
    return None if imp is None else np.asarray(imp, dtype=float)


def region_for_wavelength(nm: float) -> ReasonCodeType:
    """Map a wavelength (nm) to the reason-code type for its spectral region (science.md §3.3)."""
    if C.RED_EDGE_RANGE[0] <= nm <= C.RED_EDGE_RANGE[1]:
        return ReasonCodeType.RED_EDGE_SHIFT
    if any(abs(nm - w) <= 40.0 for w in C.WATER_ABSORPTION):
        return ReasonCodeType.WATER_BAND_ANOMALY
    if nm >= C.SWIR_RANGE[0]:
        return ReasonCodeType.SWIR_ANOMALY
    return ReasonCodeType.HIGH_STRESS_PATCH


def band_importance(model, wavelengths: np.ndarray) -> dict[float, float]:
    """Importance per wavelength for a model trained on spectra (empty if unavailable)."""
    imp = feature_importance(model)
    wl = np.asarray(wavelengths, dtype=float)
    if imp is None or len(imp) != len(wl):
        return {}
    return {float(w): float(v) for w, v in zip(wl, imp, strict=False)}


def wavelength_importance(model, names: list[str]) -> dict[str, float]:
    """Importance per named engineered feature (empty if unavailable / mismatched)."""
    imp = feature_importance(model)
    if imp is None or len(imp) != len(names):
        return {}
    return {n: float(v) for n, v in zip(names, imp, strict=False)}


def top_features(model, names: list[str], k: int = 3) -> list[str]:
    ranked = sorted(wavelength_importance(model, names).items(), key=lambda kv: -kv[1])
    return [name for name, _ in ranked[:k]]


def _context_codes(
    *, coverage: float | None, ood: bool, spray_recent: bool, short_phi: bool, prior_high_risk: bool
) -> list[ReasonCode]:
    codes: list[ReasonCode] = []
    if spray_recent:
        codes.append(ReasonCode(type=ReasonCodeType.SPRAY_TIMING, detail="recent spray application"))
    if short_phi:
        codes.append(ReasonCode(type=ReasonCodeType.SHORT_PHI, detail="short pre-harvest interval"))
    if prior_high_risk:
        codes.append(ReasonCode(type=ReasonCodeType.PRIOR_HIGH_RISK_PATTERN, detail="matches prior high-risk pattern"))
    if coverage is not None and coverage < 0.5:
        codes.append(ReasonCode(type=ReasonCodeType.LOW_COVERAGE, detail=f"low usable coverage ({coverage:.0%})"))
    if ood:
        codes.append(ReasonCode(type=ReasonCodeType.OOD_INPUT, detail="input outside model experience"))
    return codes


def reason_codes_from_bands(
    model,
    wavelengths: np.ndarray,
    *,
    k: int = 3,
    coverage: float | None = None,
    ood: bool = False,
    spray_recent: bool = False,
    short_phi: bool = False,
    prior_high_risk: bool = False,
) -> list[ReasonCode]:
    """Reason codes from the most influential wavelength bands (model trained on spectra)."""
    importance = band_importance(model, wavelengths)
    top_wl = [w for w, _ in sorted(importance.items(), key=lambda kv: -kv[1])[:k]]
    codes: list[ReasonCode] = []
    seen: set[ReasonCodeType] = set()
    for w in top_wl:
        rc = region_for_wavelength(w)
        if rc not in seen:
            codes.append(ReasonCode(type=rc, detail=f"band ~{w:.0f} nm strongly influenced this zone"))
            seen.add(rc)
    codes += _context_codes(
        coverage=coverage, ood=ood, spray_recent=spray_recent, short_phi=short_phi, prior_high_risk=prior_high_risk
    )
    return codes


def build_reason_codes(
    top_feature_names: list[str],
    *,
    coverage: float | None = None,
    ood: bool = False,
    spray_recent: bool = False,
    short_phi: bool = False,
    prior_high_risk: bool = False,
) -> list[ReasonCode]:
    """Reason codes from named engineered features (model trained on the feature matrix)."""
    codes: list[ReasonCode] = []
    seen: set[ReasonCodeType] = set()
    for name in top_feature_names:
        rc = _FEATURE_REASON.get(name)
        if rc is not None and rc not in seen:
            codes.append(ReasonCode(type=rc, detail=f"feature '{name}' strongly influenced this zone"))
            seen.add(rc)
    codes += _context_codes(
        coverage=coverage, ood=ood, spray_recent=spray_recent, short_phi=short_phi, prior_high_risk=prior_high_risk
    )
    return codes
