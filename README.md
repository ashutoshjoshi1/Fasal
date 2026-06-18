# FASAL — backend

**FASAL** is a drone-based hyperspectral + AI system that screens **pesticide-residue *risk*** in
crop fields before harvest and produces a geospatial **low / medium / high risk heatmap**.

> **Screening, not certification.** FASAL never certifies pesticide concentrations or MRL
> compliance. It identifies spatial risk patterns and routes high-risk zones to **targeted ground
> sampling and confirmatory GC-MS/MS / LC-MS/MS lab testing**. See [`docs/`](docs/README.md) and the
> scientific basis in [`docs/science.md`](docs/science.md).

This repository currently contains the **backend foundation** (Python). The frontend (React/Next.js)
will be built from [`design.md`](design.md) once design files arrive.

## What's here

| Layer | Status | Module |
|---|---|---|
| Spectroscopy pipeline (calibration → preprocess → QC → segmentation) | **Implemented + tested** | `fasal/pipeline` |
| **Avantes point spectrometer** path (counts→reflectance: pixel→wavelength, integration time, filters, FOV) | **Implemented + tested** | `fasal/pipeline/spectrum.py`, `fasal/hardware` |
| Feature extraction (indices, descriptors) | **Implemented + tested** | `fasal/features` |
| ML core — baselines (PLS-DA/RF/SVM/GBM), uncertainty/OOD, calibration, explainability | **Implemented + tested** | `fasal/models` |
| Deep models — 1D-CNN + spectral/spatial/metadata fusion (MC-dropout) | **Implemented** (extra `deep`) | `fasal/models/deep` |
| Contracts — 8 data objects + risk output contract | **Implemented + tested** | `fasal/shared` |
| Synthetic data (run/test without real captures) | **Implemented + tested** | `fasal/synth` |
| Hardware integration — sensor/drone protocols + simulated driver | **Implemented + tested** | `fasal/hardware` |
| Screening service + sample-plan generation | **Implemented + tested** | `fasal/services` |
| API / DB / object storage | **Light** (interfaces + local defaults) | `fasal/api`, `fasal/db`, `fasal/storage` |

The science and ML core are deep and fully tested; API/DB/infra are intentionally light this phase.
No real drone/sensor data or residue labels exist yet, so everything runs on **synthetic data**;
real data and Postgres/PostGIS + S3/MinIO are clean extension points (see
[`docs/02-system-architecture.md`](docs/02-system-architecture.md)).

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"            # core + test tooling (no torch)
# optional extras:
#   pip install -e ".[deep]"       # PyTorch deep models
#   pip install -e ".[api]"        # FastAPI/uvicorn

pytest                              # run the test suite
python -m fasal.cli demo            # end-to-end synthetic (imaging) screening
python -m fasal.cli demo-avantes    # end-to-end Avantes point-spectrometer screening
```

`fasal demo` runs a real screening: synthetic field → reflectance pipeline → baseline model →
risk class + score + confidence + reason codes + a targeted sampling plan.

### Run the API (needs the `api` extra)

```bash
uvicorn fasal.api.app:app --reload
# GET /health, GET /models, POST /screen/synthetic?seed=1
```

## Package layout

```
fasal/
├── core/        config, scientific constants, logging
├── shared/      the 8 data objects + risk output contract (pydantic)
├── pipeline/    calibration → preprocess → QC → segmentation → orchestrator (the science)
├── features/    vegetation/red-edge/water indices + descriptors
├── synth/       synthetic hyperspectral data
├── models/      baselines, uncertainty/OOD, score calibration, explainability
│   └── deep/    PyTorch 1D-CNN + fusion (extra: fasal[deep])
├── hardware/    sensor/drone protocols + simulated driver
├── services/    screening + sampling-plan
├── db/ storage/ api/   light data layer + thin HTTP surface
└── cli.py       `fasal version` / `fasal demo`
```

## Testing

```bash
pytest --cov=fasal --cov-report=term-missing
```

Deep-model tests `importorskip("torch")`, so they skip unless the `deep` extra is installed. With
torch present, total coverage exceeds 90%; the science/ML/services modules are 90–100% regardless.

## Design & planning docs

- [`docs/`](docs/README.md) — PRD, architecture, data governance, modeling plan, field ops, risk &
  compliance, roadmap, pitch, and **[`docs/science.md`](docs/science.md)** (how spectrometer data
  becomes a risk signal).
- [`docs/backend_design.md`](docs/backend_design.md) — in-depth backend design: data flow, every module/function, and many charts.
- [`design.md`](design.md) — production-grade UI/UX brief for the upcoming frontend.
