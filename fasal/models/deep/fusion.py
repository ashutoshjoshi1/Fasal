"""Spectral + spatial + metadata fusion model (docs/04 §3 Stage 2; source Figure 8).

Three branches produce embeddings that are concatenated and passed to a risk head. Spatial and
metadata branches are optional — enabled only when those inputs are supplied at ``fit`` — so the
same class serves spectral-only and full-fusion configurations. Branches use dropout (no
BatchNorm) for clean MC-dropout uncertainty.
"""

from __future__ import annotations

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader

from fasal.models.base import RiskModel
from fasal.models.deep.datasets import FusionDataset
from fasal.models.deep.train import train_loop


class SpectralBranch(nn.Module):
    def __init__(self, n_bands: int, embed: int = 32, dropout: float = 0.3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(1, 16, 5, padding=2), nn.ReLU(), nn.MaxPool1d(2), nn.Dropout(dropout),
            nn.Conv1d(16, 32, 5, padding=2), nn.ReLU(), nn.AdaptiveAvgPool1d(1),
        )
        self.fc = nn.Linear(32, embed)

    def forward(self, x):
        return torch.relu(self.fc(self.net(x).squeeze(-1)))


class SpatialBranch(nn.Module):
    def __init__(self, in_channels: int, embed: int = 32, dropout: float = 0.3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(in_channels, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2), nn.Dropout(dropout),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.AdaptiveAvgPool2d(1),
        )
        self.fc = nn.Linear(32, embed)

    def forward(self, x):
        return torch.relu(self.fc(self.net(x).flatten(1)))


class MetadataBranch(nn.Module):
    def __init__(self, in_dim: int, embed: int = 32, dropout: float = 0.3):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, 64), nn.ReLU(), nn.Dropout(dropout), nn.Linear(64, embed), nn.ReLU()
        )

    def forward(self, x):
        return self.net(x)


class FusionModel(nn.Module):
    """Concatenate enabled branch embeddings → risk logit."""

    def __init__(self, n_bands: int, spatial_channels: int | None = None, metadata_dim: int = 0, embed: int = 32, dropout: float = 0.3):
        super().__init__()
        self.use_spatial = spatial_channels is not None
        self.use_metadata = bool(metadata_dim)
        self.spectral = SpectralBranch(n_bands, embed, dropout)
        self.spatial = SpatialBranch(spatial_channels, embed, dropout) if self.use_spatial else None
        self.metadata = MetadataBranch(metadata_dim, embed, dropout) if self.use_metadata else None
        fused = embed * (1 + int(self.use_spatial) + int(self.use_metadata))
        self.head = nn.Sequential(nn.Linear(fused, embed), nn.ReLU(), nn.Dropout(dropout), nn.Linear(embed, 1))

    def forward(self, spectral, spatial=None, metadata=None):
        embeds = [self.spectral(spectral)]
        if self.use_spatial:
            embeds.append(self.spatial(spatial))
        if self.use_metadata:
            embeds.append(self.metadata(metadata))
        return self.head(torch.cat(embeds, dim=1))


class FusionRiskModel(RiskModel):
    """RiskModel adapter. ``X`` is either spectra (N, B) or a dict with keys
    ``spectral`` (N, B), optional ``spatial`` (N, C, P, P), optional ``metadata`` (N, D)."""

    name = "fusion"

    def __init__(self, *, epochs: int = 30, lr: float = 1e-3, batch_size: int = 64, dropout: float = 0.3, embed: int = 32, device: str | None = None, seed: int = 1337):
        self.epochs = epochs
        self.lr = lr
        self.batch_size = batch_size
        self.dropout = dropout
        self.embed = embed
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.seed = seed
        self.module: FusionModel | None = None

    @staticmethod
    def _unpack(X):
        if isinstance(X, dict):
            spectral = np.asarray(X["spectral"], dtype=np.float32)
            spatial = None if X.get("spatial") is None else np.asarray(X["spatial"], dtype=np.float32)
            metadata = None if X.get("metadata") is None else np.asarray(X["metadata"], dtype=np.float32)
            return spectral, spatial, metadata
        return np.asarray(X, dtype=np.float32), None, None

    def fit(self, X, y) -> FusionRiskModel:
        torch.manual_seed(self.seed)
        spectral, spatial, metadata = self._unpack(X)
        spatial_channels = spatial.shape[1] if spatial is not None else None
        metadata_dim = metadata.shape[1] if metadata is not None else 0
        self.n_bands = spectral.shape[1]
        self.spatial_channels = spatial_channels
        self.metadata_dim = metadata_dim
        self.module = FusionModel(
            self.n_bands, spatial_channels, metadata_dim, embed=self.embed, dropout=self.dropout
        ).to(self.device)
        loader = DataLoader(
            FusionDataset(spectral, spatial, metadata, y), batch_size=self.batch_size, shuffle=True
        )
        train_loop(self.module, loader, epochs=self.epochs, lr=self.lr, device=self.device)
        return self

    def predict_proba(self, X) -> np.ndarray:
        if self.module is None:
            raise RuntimeError("call fit() or load() first")
        spectral, spatial, metadata = self._unpack(X)
        inputs = {"spectral": torch.as_tensor(spectral[:, None, :]).to(self.device)}
        if spatial is not None:
            inputs["spatial"] = torch.as_tensor(spatial).to(self.device)
        if metadata is not None:
            inputs["metadata"] = torch.as_tensor(metadata).to(self.device)
        self.module.eval()
        with torch.no_grad():
            return torch.sigmoid(self.module(**inputs)).cpu().numpy().ravel()

    def save(self, path: str) -> None:
        if self.module is None:
            raise RuntimeError("call fit() first")
        torch.save(
            {
                "state": self.module.state_dict(),
                "n_bands": self.n_bands,
                "spatial_channels": self.spatial_channels,
                "metadata_dim": self.metadata_dim,
                "embed": self.embed,
                "dropout": self.dropout,
            },
            path,
        )

    @classmethod
    def load(cls, path: str, *, device: str | None = None) -> FusionRiskModel:
        blob = torch.load(path, map_location="cpu", weights_only=True)
        model = cls(embed=blob["embed"], dropout=blob["dropout"], device=device)
        model.n_bands = blob["n_bands"]
        model.spatial_channels = blob["spatial_channels"]
        model.metadata_dim = blob["metadata_dim"]
        model.module = FusionModel(
            blob["n_bands"],
            blob["spatial_channels"],
            blob["metadata_dim"],
            embed=blob["embed"],
            dropout=blob["dropout"],
        ).to(model.device)
        model.module.load_state_dict(blob["state"])
        return model
