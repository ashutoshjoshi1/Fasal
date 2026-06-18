"""PyTorch deep-model tests. Skipped automatically when torch is not installed."""

import pytest

torch = pytest.importorskip("torch")  # noqa: F841 — skip whole module without the deep extra

import numpy as np  # noqa: E402
from sklearn.metrics import roc_auc_score  # noqa: E402
from sklearn.model_selection import train_test_split  # noqa: E402

from fasal.models import create  # noqa: E402
from fasal.synth import make_dataset  # noqa: E402


def _split():
    spectra, _wl, y, _ = make_dataset(300, signal_strength=0.05, noise=0.01, seed=0)
    return train_test_split(spectra, y, test_size=0.3, random_state=0, stratify=y)


def test_spectral_cnn_trains_and_mc_dropout_samples():
    Xtr, Xte, ytr, yte = _split()
    model = create("cnn1d", epochs=15, batch_size=32)
    model.fit(Xtr, ytr)
    assert roc_auc_score(yte, model.predict_proba(Xte)) > 0.7
    samples = model.predict_proba_samples(Xte, n_samples=5)
    assert samples.shape == (5, len(yte))


def test_fusion_model_spectral_only_predicts_probabilities():
    Xtr, Xte, ytr, yte = _split()
    model = create("fusion", epochs=10, batch_size=32)
    model.fit(Xtr, ytr)
    probs = model.predict_proba(Xte)
    assert probs.shape == (len(yte),)
    assert ((probs >= 0.0) & (probs <= 1.0)).all()


def test_deep_models_save_load_roundtrip(tmp_path):
    Xtr, Xte, ytr, _yte = _split()
    for kind in ("cnn1d", "fusion"):
        model = create(kind, epochs=5, batch_size=32).fit(Xtr, ytr)
        path = str(tmp_path / f"{kind}.pt")
        model.save(path)
        reloaded = type(model).load(path)
        assert np.allclose(model.predict_proba(Xte), reloaded.predict_proba(Xte), atol=1e-5)
