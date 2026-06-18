# 02 — System Architecture

*Source: concept doc §4 (remote-sensing science), §6 (payload), §8.2 (model stages), Figures 4 & 8.
This doc records the **chosen architecture and tech stack** for the eventual build — no code is
written in this phase.*

## 1. Architecture at a glance

FASAL is a pipeline from **raw hyperspectral cube → calibrated reflectance → AI-ready map → risk
product**, fronted by an API and a role-based web dashboard, with a closed **lab-feedback loop**
that grows the dataset.

```
                         ┌─────────────────────── FASAL platform ───────────────────────┐
 Drone flight            │                                                               │
 (HSI cube, RGB,         │   INGESTION ─► CALIBRATION ─► PREPROCESS ─► SEGMENTATION       │
  irradiance, GNSS/IMU)──┼─►  + metadata    radiance→     SG/deriv/      canopy/fruit     │
 + field metadata        │   validation     reflectance   SNV/MSC/mask   regions          │
 (crop/spray/weather)    │        │              │            │             │              │
                         │        ▼              ▼            ▼             ▼              │
                         │   ┌──────────────── AI INFERENCE (fusion) ─────────────────┐   │
                         │   │ spectral branch + spatial branch + metadata branch      │   │
                         │   │      └────────────► fusion ► risk score                 │   │
                         │   │      uncertainty/OOD ─► confidence    XAI ─► reason codes│   │
                         │   └─────────────────────────┬───────────────────────────────┘  │
                         │                              ▼                                   │
                         │      RISK PRODUCT: heatmap · class · score · confidence ·        │
                         │      reason codes · action · GPS sample plan                     │
                         │              │                         │                         │
                         │              ▼                         ▼                         │
                         │         API (FastAPI)  ◄──────►  Web dashboard (Next.js)         │
                         │              │                                                   │
                         │   ┌──────────┴───────────┐                                       │
                         │   │ Metadata DB (PostGIS) │   Object store (COG cubes/orthos)    │
                         │   │ Dataset registry / DVC│   Experiment tracking (MLflow)       │
                         │   └───────────────────────┘                                      │
                         └──────────────────────────────┬───────────────────────────────────┘
                                                         ▼
                                  LAB LOOP: GPS samples → QuEChERS + GC-MS/MS / LC-MS/MS
                                  → results joined to zones → dataset & model update
```

*(Mirrors source Figure 4 — raw cube → reflectance — and Figure 8 — spectral/spatial/metadata
branches → fusion → confidence → action.)*

## 2. Why the signal is hard (drives the design)

A drone measures **radiance**, not molecules:
`L_sensor(λ) = E_sun(λ)·ρ_surface(λ)·G(θ_sun,θ_view,φ) + L_path(λ) + N_sensor(λ)`.
Each pixel is a **mixture** (leaf, fruit, stem, soil, shadow, water, dust, mulch, residue), and
reflectance shifts with illumination, leaf angle, growth stage, moisture, and BRDF/view geometry.
Consequences enforced by the architecture:

- Calibration to **reflectance** is mandatory before AI (Component B).
- **Metadata fusion** is first-class — spray history/weather/PHI carry much of the signal.
- Outputs are **risk + uncertainty**, never concentration (see [`00`](00-executive-overview.md); full physics/chemistry in [`science.md`](science.md)).

## 3. Components

| # | Component | Responsibility | Key tech |
|---|---|---|---|
| A | **Ingestion & validation** | Accept flight cube, RGB, irradiance, GNSS/IMU, calibration frames, and crop/spray/weather metadata; validate against schema at the boundary | FastAPI + pydantic; object upload |
| B | **Radiometric calibration → reflectance** | Dark-current subtraction, white/gray panel + irradiance + empirical-line correction, geometry handling | NumPy/SciPy, rasterio/GDAL, `spectral` |
| C | **Preprocessing** | Spectral resampling, Savitzky-Golay smoothing, derivatives, SNV, MSC, bad-band removal | SciPy/scikit-learn; **recipe version-locked** |
| D | **QC & masking** | Drop saturated/blurred/cloud/shadow pixels; compute coverage-quality metric | rasterio, OpenCV |
| E | **Segmentation** | Isolate canopy and visible fruit/leaf regions before inference | CNN/U-Net (PyTorch); RGB+spectral |
| F | **AI inference (fusion)** | Spectral + spatial + metadata branches → fusion → risk score | PyTorch (DL), scikit-learn (baselines) |
| G | **Uncertainty / OOD** | Confidence estimate; flag out-of-distribution inputs → route to manual/lab | MC-dropout / ensembles / density estimates |
| H | **Explainability** | Wavelength importance, spatial attention, reason codes, control comparison | SHAP / attention maps / prototype distances |
| I | **Risk-product assembly** | Compose heatmap, class, score, confidence, reason codes, action, sample plan | GeoTIFF/COG outputs; GeoJSON sample plan |
| J | **API** | Serve predictions and data access; enforce roles | FastAPI, pydantic, OAuth2/JWT |
| K | **Web dashboard** | Role-based persona surfaces; map-first UI | Next.js/React (see [`../design.md`](../design.md)) |
| L | **Data & MLOps backbone** | Metadata DB, object storage, dataset versioning, experiment tracking | PostgreSQL+PostGIS, S3/MinIO, DVC, MLflow |
| M | **Lab loop** | Ingest lab results, join to zones, trigger dataset/model update | DB + DVC + retraining job |

Modeling detail for F/G/H is in [`04`](04-ai-ml-modeling-plan.md); the data schema for A/L/M is in
[`03`](03-data-architecture-governance.md).

## 4. Recommended technology stack (with rationale)

Chosen for the **"solid long-term foundation"** priority: a Python ML core + a Next.js front end,
with reproducibility and geospatial correctness built in.

| Layer | Choice | Rationale |
|---|---|---|
| **Language (core)** | Python 3.11+ | Ecosystem for HSI, remote sensing, and ML |
| **HSI / geospatial** | NumPy, SciPy, xarray, rasterio/GDAL, `spectral` (SPy) | Cube math, reflectance, cloud-optimized GeoTIFF (COG) handling |
| **Classical ML** | scikit-learn (PLS, RF, SVM, GBM), `numpy` indices | Baselines first per §8.2 |
| **Deep learning** | PyTorch (1D/2D/3D CNN, attention/fusion) | Spectral-spatial-metadata fusion, segmentation |
| **Uncertainty/XAI** | MC-dropout/ensembles, SHAP, captum | Confidence + reason codes (NFR5, FR6–FR8) |
| **API** | FastAPI + pydantic | Boundary validation, typed contracts (NFR4) |
| **Metadata DB** | PostgreSQL + **PostGIS** | Geospatial joins of zones, samples, lab results |
| **Object storage** | S3-compatible (MinIO local / cloud) | Large spectral cubes & orthomosaics as COG |
| **Orthomosaic** | OpenDroneMap / structure-from-motion | Stitch flights into georeferenced mosaics (ops, planned) |
| **Dataset versioning** | **DVC** | Reproducibility (NFR1); links data ↔ model ↔ code |
| **Experiment tracking** | **MLflow** | Runs, metrics-by-crop/pesticide, model registry |
| **Frontend** | **Next.js / React** + TanStack Query | Production dashboard; server-state caching |
| **Map / geo-viz** | WebGL map (MapLibre GL or deck.gl) | Risk-heatmap overlays on basemap/orthomosaic |
| **AuthN/Z** | OAuth2/JWT + role-based access | Five personas with different aggregation/anonymization |
| **Packaging/CI** | Docker, GitHub Actions | Reproducible envs; lint/type/test gates |
| **Compute** | Edge GPU (field) + cloud GPU (training) | §6.1 "ideal" path; scalable training compute |

## 5. Repository structure (as built — backend)

The backend foundation now exists at the repo root as the importable `fasal/` package; `web/` is
deferred until the frontend design files arrive.

```
fasal/                 # importable Python package (backend)
├── core/          # config, scientific constants, logging
├── shared/        # the 8 data objects + risk output contract (pydantic)
├── pipeline/      # calibration → preprocess → QC → segmentation → orchestrator (the science)
├── features/      # vegetation/red-edge/water indices + descriptors
├── synth/         # synthetic hyperspectral data (run/test without real captures)
├── models/        # baselines (PLS/RF/SVM/GBM), uncertainty/OOD, calibration, explainability
│   └── deep/      # PyTorch 1D-CNN + spectral/spatial/metadata fusion (extra: fasal[deep])
├── hardware/      # sensor/drone protocols + simulated driver
├── services/      # screening (cube → prediction) + sample-plan generation
├── db/            # repository pattern (in-memory default; Postgres/PostGIS later) — light
├── storage/       # object store (local default; S3/MinIO later) — light
├── api/           # thin FastAPI surface (extra: fasal[api]) — light
└── cli.py         # `fasal version` / `fasal demo`
tests/             # pytest suite (science + ML + integration)
infra/             # docker-compose (Postgres/PostGIS + MinIO); CI under .github/workflows/
docs/              # planning suite + science.md     (web/ deferred until design files arrive)
```

The **output contract** and **8 data objects** live in `shared/` so the pipeline, API, and web app
cannot drift apart (single source of truth; supports NFR7 extensibility).

## 6. Data flow & contracts

1. **Intake (A):** every object validated against `shared/` schemas; reject/flag malformed inputs (input-validation at boundary).
2. **Calibration (B) → Preprocess (C) → QC (D) → Segmentation (E):** deterministic, version-pinned; each stage records provenance.
3. **Inference (F–I):** emits the canonical **output contract** (class, score, confidence, reason codes, action) + heatmap (COG) + sample plan (GeoJSON).
4. **Serving (J/K):** API returns risk products + provenance; dashboard renders map-first with persona scoping.
5. **Lab loop (M):** lab results joined by GPS to zones in PostGIS; dataset registry (DVC) updated; retraining tracked in MLflow.

> **Point-sensor (Avantes) ingestion — primary path.** The current spectral sensor is an Avantes
> point spectrometer emitting **counts vs detector pixel**. `fasal/pipeline/spectrum.py` maps
> pixel→wavelength (device polynomial), applies dark / integration-time / white-reference calibration
> and the filter passband, and yields reflectance spectra that enter the same preprocess→model path.
> Each scan covers a FOV footprint, so the field map is a set of **geo-tagged point scans** (sparse),
> not a dense raster (see [`science.md`](science.md) and [`05`](05-field-ops-hardware-plan.md) §1.4).

## 7. Cross-cutting concerns

- **Reproducibility (NFR1):** preprocessing recipe + model + data are versioned together; a
  prediction can be reproduced from its provenance record. *Preprocessing is locked before
  validation to avoid inflated performance.*
- **Provenance (FR12/NFR4):** model version, sensor serial, calibration record, and flight
  conditions persist with each prediction.
- **Security/roles:** OAuth2/JWT; per-persona scoping; aggregated views anonymized for regulatory/aggregate
  consumers; full security posture and claims governance in
  [`06`](06-risk-compliance.md) and [`03`](03-data-architecture-governance.md).
- **Observability:** structured logs, pipeline-stage metrics, model-performance dashboards by
  crop/pesticide/season; OOD-rate monitoring as a drift signal.
- **Compute/deployment:** post-flight cloud/GPU processing in v1 (laptop acceptable for earliest
  trials per §6.1); architecture leaves room for edge-GPU field inference later.

## 8. Phasing note

v1 favors **post-flight batch processing** and **VNIR** sensing; **SWIR** and **edge inference**
are additive (NFR7). The classical-ML baseline ships before deep learning so the dataset and
validation discipline mature first ([`04`](04-ai-ml-modeling-plan.md), [`07`](07-roadmap-task-breakdown.md)).
