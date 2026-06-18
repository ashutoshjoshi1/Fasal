"""torch Datasets for the deep models.

``SpectraDataset`` yields ``((1, B) spectrum, (1,) label)``. ``FusionDataset`` yields
``(dict-of-branch-tensors, (1,) label)`` so the fusion model can bind branches by keyword
regardless of which are present.
"""

from __future__ import annotations

import numpy as np
import torch
from torch.utils.data import Dataset


class SpectraDataset(Dataset):
    def __init__(self, X: np.ndarray, y: np.ndarray):
        self.X = torch.as_tensor(np.asarray(X, dtype=np.float32)[:, None, :])
        self.y = torch.as_tensor(np.asarray(y, dtype=np.float32)).view(-1, 1)

    def __len__(self) -> int:
        return self.X.shape[0]

    def __getitem__(self, i: int):
        return self.X[i], self.y[i]


class FusionDataset(Dataset):
    def __init__(self, spectral: np.ndarray, spatial=None, metadata=None, y=None):
        self.spectral = torch.as_tensor(np.asarray(spectral, dtype=np.float32)[:, None, :])
        self.spatial = None if spatial is None else torch.as_tensor(np.asarray(spatial, dtype=np.float32))
        self.metadata = None if metadata is None else torch.as_tensor(np.asarray(metadata, dtype=np.float32))
        self.y = None if y is None else torch.as_tensor(np.asarray(y, dtype=np.float32)).view(-1, 1)

    def __len__(self) -> int:
        return self.spectral.shape[0]

    def __getitem__(self, i: int):
        inputs = {"spectral": self.spectral[i]}
        if self.spatial is not None:
            inputs["spatial"] = self.spatial[i]
        if self.metadata is not None:
            inputs["metadata"] = self.metadata[i]
        y = self.y[i] if self.y is not None else torch.zeros(1)
        return inputs, y
