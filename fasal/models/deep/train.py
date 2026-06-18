"""Generic training loop for torch ``RiskModel`` adapters (binary risk via BCEWithLogits).

Handles three batch-input shapes so it serves both the spectral CNN (single tensor) and the
fusion model (a dict of branch tensors): a plain tensor, a tuple/list, or a dict (``module(**inputs)``).
"""

from __future__ import annotations

from collections.abc import Mapping

import torch
from torch import nn


def train_loop(module, loader, *, epochs: int = 30, lr: float = 1e-3, device: str = "cpu", weight_decay: float = 0.0) -> list[float]:
    """Train ``module`` over ``loader`` and return the per-epoch mean loss history."""
    module.to(device)
    module.train()
    optimizer = torch.optim.Adam(module.parameters(), lr=lr, weight_decay=weight_decay)
    loss_fn = nn.BCEWithLogitsLoss()
    history: list[float] = []
    for _ in range(epochs):
        total, count = 0.0, 0
        for inputs, yb in loader:
            yb = yb.to(device)
            if isinstance(inputs, Mapping):
                out = module(**{k: v.to(device) for k, v in inputs.items()})
            elif isinstance(inputs, list | tuple):
                out = module(*[t.to(device) for t in inputs])
            else:
                out = module(inputs.to(device))
            loss = loss_fn(out, yb)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            total += float(loss) * yb.size(0)
            count += yb.size(0)
        history.append(total / max(count, 1))
    return history
