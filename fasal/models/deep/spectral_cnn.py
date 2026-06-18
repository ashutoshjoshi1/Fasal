"""1-D spectral CNN (docs/04 §3 Stage 1) wrapped as a :class:`RiskModel`.

No BatchNorm is used so that enabling ``train()`` toggles *only* dropout — giving clean
MC-dropout predictive-uncertainty sampling (docs/04 §5).
"""

from __future__ import annotations

import numpy as np
import torch
from torch import nn

from fasal.models.base import RiskModel
from fasal.models.deep.train import train_loop


class Spectral1DCNN(nn.Module):
    """Conv1D stack over a spectrum (N, 1, B) → single risk logit."""

    def __init__(self, n_bands: int, channels: tuple[int, ...] = (16, 32, 64), dropout: float = 0.3):
        super().__init__()
        layers: list[nn.Module] = []
        in_ch = 1
        for out_ch in channels:
            layers += [
                nn.Conv1d(in_ch, out_ch, kernel_size=5, padding=2),
                nn.ReLU(),
                nn.MaxPool1d(2),
                nn.Dropout(dropout),
            ]
            in_ch = out_ch
        self.features = nn.Sequential(*layers)
        self.pool = nn.AdaptiveAvgPool1d(1)
        self.head = nn.Sequential(nn.Linear(in_ch, in_ch), nn.ReLU(), nn.Dropout(dropout), nn.Linear(in_ch, 1))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.features(x)
        z = self.pool(z).squeeze(-1)
        return self.head(z)


class SpectralCNNRiskModel(RiskModel):
    """RiskModel adapter for :class:`Spectral1DCNN` (input X = spectra (N, B))."""

    name = "cnn1d"

    def __init__(
        self,
        *,
        epochs: int = 30,
        lr: float = 1e-3,
        batch_size: int = 64,
        dropout: float = 0.3,
        device: str | None = None,
        seed: int = 1337,
    ):
        self.epochs = epochs
        self.lr = lr
        self.batch_size = batch_size
        self.dropout = dropout
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.seed = seed
        self.module: Spectral1DCNN | None = None
        self.n_bands: int | None = None

    def fit(self, X: np.ndarray, y: np.ndarray) -> SpectralCNNRiskModel:
        torch.manual_seed(self.seed)
        X = np.asarray(X, dtype=np.float32)
        self.n_bands = X.shape[1]
        self.module = Spectral1DCNN(self.n_bands, dropout=self.dropout).to(self.device)
        xt = torch.as_tensor(X[:, None, :])
        yt = torch.as_tensor(np.asarray(y, dtype=np.float32)).view(-1, 1)
        loader = torch.utils.data.DataLoader(
            torch.utils.data.TensorDataset(xt, yt), batch_size=self.batch_size, shuffle=True
        )
        train_loop(self.module, loader, epochs=self.epochs, lr=self.lr, device=self.device)
        return self

    def _logits(self, X: np.ndarray) -> torch.Tensor:
        assert self.module is not None, "call fit() first"
        xt = torch.as_tensor(np.asarray(X, dtype=np.float32)[:, None, :]).to(self.device)
        return self.module(xt)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        self.module.eval()
        with torch.no_grad():
            return torch.sigmoid(self._logits(X)).cpu().numpy().ravel()

    def predict_proba_samples(self, X: np.ndarray, n_samples: int = 20) -> np.ndarray:
        """MC-dropout: (n_samples, N) probabilities with dropout active (docs/04 §5)."""
        self.module.train()  # only dropout is stochastic (no BatchNorm)
        out = []
        with torch.no_grad():
            for _ in range(n_samples):
                out.append(torch.sigmoid(self._logits(X)).cpu().numpy().ravel())
        return np.stack(out, axis=0)

    def save(self, path: str) -> None:
        torch.save(
            {"state": self.module.state_dict(), "n_bands": self.n_bands, "dropout": self.dropout}, path
        )

    @classmethod
    def load(cls, path: str, *, device: str | None = None) -> SpectralCNNRiskModel:
        blob = torch.load(path, map_location="cpu")
        model = cls(dropout=blob["dropout"], device=device)
        model.n_bands = blob["n_bands"]
        model.module = Spectral1DCNN(model.n_bands, dropout=model.dropout).to(model.device)
        model.module.load_state_dict(blob["state"])
        return model
