# 07 — Roadmap & Task Breakdown

*Source: concept doc §13 (12-month roadmap), re-expressed as parallel workstreams with epics, tasks,
dependencies, milestones, and exit criteria.*

## 1. Milestone map (the spine)

| Window | Deliverable | Exit criteria |
|---|---|---|
| **M1–M2** | Partner MoUs (agri university / grower cooperative / lab); crop & pesticide shortlist; **ethics & data-governance plan** | MoUs signed; shortlist locked; governance plan approved |
| **M1–M3** | Payload selection, sensor calibration, **field SOP**, **data schema**, lab chain-of-custody setup | Payload procured/calibrated; SOP + schema + custody approved |
| **M2–M5** | Controlled plots: **untreated, legal-dose, over-dose, mixed-spray** treatments | Plots planted & treated to design; first flights flown |
| **M3–M7** | Reflectance pipeline, segmentation, QC masks, **model baseline** | Pipeline reproducible; baseline metrics reported by crop/pesticide |
| **M5–M8** | **AI model v1** with uncertainty & explainability | v1 meets recall/precision targets on controlled plots (or documents the gap); XAI + OOD working |
| **M8–M11** | Independent **farm pilot** with targeted sampling & lab comparison | Pilot flights + lab loop closed; generalization measured |
| **M10–M12** | **Validation report**, **dashboard demo**, **funding/positioning docs**, **dataset publication** plan | Report by crop/pesticide/farm/season; demo runs; dataset cards published |

## 2. Workstreams (run in parallel)

### WS1 — Partnerships & Data Governance  *(M1–M2, ongoing)*
- **Epic 1.1 Partnerships:** MoUs with agri university, grower cooperative(s), accredited residue lab; pilot-farm access.
- **Epic 1.2 Shortlist:** finalize 3 crops × 5–8 pesticides (usage, export/import-rejection history, official residue-monitoring priorities, lab capability).
- **Epic 1.3 Governance:** ethics & data-governance plan; consent/anonymization; chain-of-custody policy; dataset licensing; per-jurisdiction data residency ([`03`](03-data-architecture-governance.md)).
- **Exit:** signed MoUs, locked shortlist, approved governance plan.

### WS2 — Hardware & Field Operations  *(M1–M3, then per-season)*
- **Epic 2.1 Payload:** select airframe + VNIR sensor + RGB + irradiance + GNSS/IMU + panels ([`05`](05-field-ops-hardware-plan.md)).
- **Epic 2.2 Calibration & SOP:** sensor calibration; flight/calibration/sampling SOP; airspace/regulatory compliance per jurisdiction ([`06`](06-risk-compliance.md)).
- **Epic 2.3 Plots:** establish controlled plots (untreated/legal/over/mixed); flight scheduling near solar noon.
- **Exit:** payload calibrated; SOP approved; plots flown to schedule.

### WS3 — Data Pipeline  *(M3–M7)*
- **Epic 3.1 Schema & ingestion:** implement the 8 data objects in `shared/`; schema-validated intake.
- **Epic 3.2 Calibration→reflectance:** dark/white/irradiance/empirical-line; geometry handling.
- **Epic 3.3 Preprocess + QC:** SG/derivative/SNV/MSC, bad-band removal, cloud/shadow masking, coverage-quality.
- **Epic 3.4 Segmentation:** canopy/fruit isolation.
- **Epic 3.5 MLOps backbone:** PostGIS, object store (COG), **DVC**, **MLflow** ([`02`](02-system-architecture.md)).
- **Exit:** end-to-end reproducible reflectance + masks + segmentation; preprocessing recipe **version-locked**.

### WS4 — AI / ML  *(M3–M11)*
- **Epic 4.1 Baselines (Stage 0):** indices/PCA/PLS/RF/SVM/GBM; feasibility of spectral separation.
- **Epic 4.2 Deep models (Stage 1):** 1D/2D/3D CNN; segmentation backbone.
- **Epic 4.3 Fusion (Stage 2):** spectral+spatial+metadata fusion; calibrated risk score.
- **Epic 4.4 Uncertainty/OOD + XAI:** confidence, abstention, wavelength importance, attention, reason codes ([`04`](04-ai-ml-modeling-plan.md)).
- **Epic 4.5 Generalization:** domain adaptation, active learning, region-wise validation.
- **Exit:** model v1 meeting pilot targets on controlled plots; XAI + OOD live.

### WS5 — Product / Dashboard (Web)  *(M5–M12)*
- **Epic 5.1 UI design handoff:** generate UI from [`../design.md`](../design.md) ("Claude design" step), then integrate.
- **Epic 5.2 API:** FastAPI services — prediction, data access, sample-plan, lab-loop.
- **Epic 5.3 Persona surfaces:** field risk map, zone inspector, flights/QC, batch & lab queue, sampling plan, regional trends, dataset/labeling, upload/status ([`../design.md`](../design.md) §5).
- **Epic 5.4 Trust UX:** screening disclaimer, confidence/OOD, provenance panel.
- **Exit:** dashboard demo runs end-to-end on pilot data with the full output contract.

### WS6 — Validation  *(M5–M12)*
- **Epic 6.1 Protocol:** split by field/date; independent farms; per-crop/pesticide/season tracking.
- **Epic 6.2 Ablations:** drone-only vs metadata-only vs fused (prove spectroscopy uplift).
- **Epic 6.3 Reporting:** confusion matrices by crop/pesticide/farm/season; calibration & repeatability; lab-uplift; abstention quality.
- **Exit:** validation report meeting [`01`](01-product-requirements.md) §8 targets (or documented gaps).

### WS7 — Funding & Go-to-Market Deliverables  *(M10–M12)*
- **Epic 7.1 Pitch package:** narrative, funding/market alignment, the ask ([`08`](08-pitch.md)).
- **Epic 7.2 Dataset publication:** dataset cards + governed open release (FAIR).
- **Epic 7.3 Demo:** dashboard + validation artifacts for the funder/partner demo.
- **Exit:** pitch docs + published dataset plan + working demo.

## 3. Critical dependencies
```
WS1 (partners, shortlist, governance) ─► WS2 (plots) ─► WS3 (pipeline needs flights)
WS3 (reflectance/segmentation) ─► WS4 (models need clean inputs)
WS4 (output contract) ─► WS5 (dashboard renders outputs)  ; WS5.1 design handoff can start early from design.md
WS4 + WS2 (pilot) ─► WS6 (validation needs lab loop closed)
WS5 + WS6 ─► WS7 (demo + report feed the pitch)
```
**Sequencing note:** the **classical baseline (Stage 0) ships before deep learning** so dataset and
validation discipline mature first; **VNIR precedes SWIR** (cost/benefit gate, [`05`](05-field-ops-hardware-plan.md)).

## 4. Cross-cutting tracks (continuous)
- **Reproducibility:** DVC + MLflow from day one; preprocessing locked before validation.
- **Compliance:** airspace checks per flight (per jurisdiction); chain-of-custody per sample; claims governance in every surface.
- **Risk burn-down:** track the [`06`](06-risk-compliance.md) register; revisit at each milestone.

## 5. Phase-1 "first 90 days" focus
WS1 fully; WS2 payload + SOP + first plots; WS3 schema + ingestion + calibration scaffolding; WS4
baseline feasibility on bench/controlled data; WS5.1 design handoff kicked off from
[`../design.md`](../design.md). Goal: prove **spectral separability + a reproducible pipeline** before
investing in deep models.
