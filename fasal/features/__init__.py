"""Feature extraction (science → ML bridge): spectral indices and descriptors."""

from fasal.features.indices import (
    index_features,
    ndre,
    ndvi,
    red_edge_position,
    water_band_index,
)
from fasal.features.spectral import (
    band_statistics,
    build_feature_matrix,
    derivative_stats,
    fit_pca,
)

__all__ = [
    # indices
    "index_features",
    "ndre",
    "ndvi",
    "red_edge_position",
    "water_band_index",
    # descriptors
    "band_statistics",
    "build_feature_matrix",
    "derivative_stats",
    "fit_pca",
]
