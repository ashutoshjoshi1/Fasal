"""Spectral descriptors and feature-matrix assembly for the ML core (science.md §8.2-8.3).

Combines physically-meaningful indices with band statistics and derivative summaries into a
single feature matrix for baseline models. PCA is offered for dimensionality reduction.
"""

from __future__ import annotations

import numpy as np
from sklearn.decomposition import PCA

from fasal.features.indices import index_features

# numpy>=2.0 renamed trapz -> trapezoid; keep a portable alias.
_trapz = getattr(np, "trapezoid", np.trapz)


def band_statistics(spectra: np.ndarray) -> tuple[np.ndarray, list[str]]:
    """Summary statistics over the band axis. ``(N, B) -> (N, 6)``."""
    x = np.asarray(spectra, dtype=float)
    feats = np.stack(
        [
            x.mean(axis=-1),
            x.std(axis=-1),
            x.min(axis=-1),
            x.max(axis=-1),
            x.max(axis=-1) - x.min(axis=-1),
            _trapz(x, axis=-1),
        ],
        axis=-1,
    )
    return feats, ["mean", "std", "min", "max", "range", "area"]


def derivative_stats(spectra: np.ndarray) -> tuple[np.ndarray, list[str]]:
    """First-derivative summary stats — sensitivity to subtle/overlapping features."""
    x = np.asarray(spectra, dtype=float)
    d = np.gradient(x, axis=-1)
    feats = np.stack([d.mean(axis=-1), d.std(axis=-1), np.abs(d).max(axis=-1)], axis=-1)
    return feats, ["d1_mean", "d1_std", "d1_absmax"]


def build_feature_matrix(
    spectra: np.ndarray,
    wavelengths: np.ndarray,
    *,
    include_indices: bool = True,
    include_stats: bool = True,
    include_derivative: bool = True,
) -> tuple[np.ndarray, list[str]]:
    """Assemble an interpretable feature matrix ``(N, K)`` + names.

    Undefined descriptors (e.g. red-edge position when too few bands fall in the red-edge
    region) are replaced with 0 so downstream models receive finite inputs.
    """
    parts: list[np.ndarray] = []
    names: list[str] = []
    if include_indices:
        f, n = index_features(spectra, wavelengths)
        parts.append(f)
        names += n
    if include_stats:
        f, n = band_statistics(spectra)
        parts.append(f)
        names += n
    if include_derivative:
        f, n = derivative_stats(spectra)
        parts.append(f)
        names += n
    matrix = np.concatenate(parts, axis=-1)
    return np.nan_to_num(matrix, nan=0.0, posinf=0.0, neginf=0.0), names


def fit_pca(spectra: np.ndarray, n_components: int = 10) -> tuple[np.ndarray, PCA]:
    """Fit PCA on spectra and return ``(scores, fitted_pca)`` (science.md §8.3)."""
    pca = PCA(n_components=n_components)
    scores = pca.fit_transform(np.asarray(spectra, dtype=float))
    return scores, pca
