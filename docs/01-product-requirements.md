# 01 — Product Requirements Document (PRD)

*Source: concept doc §1, §2, §3, §8.3, §9.3, §10, §11.*

## 1. Problem statement

Agricultural supply chains worldwide move produce from farms through wholesale markets, grower
cooperatives, warehouses, exporters, processors, and retailers to consumers. Pesticide-residue
testing matters for food safety, export/import compliance, grower reputation, and consumer trust —
but lab testing today is **costly, centralized, sample-limited, and applied after produce has
already entered the chain**. Sampling is largely blind, so contaminated lots can be missed while
clean lots are tested unnecessarily.

**The opportunity:** move screening *upstream*. Scan the field **before harvest**, map suspicious
zones, and route scarce lab capacity to the samples most likely to matter. This converts the
workflow from *reactive testing* to *proactive risk mapping* — and it generalizes across regions,
crops, and regulatory regimes.

## 2. Goals and non-goals

### Goals
- **G1.** Produce a field-scale, geospatial **low/medium/high pesticide-risk heatmap** before harvest.
- **G2.** **Maximize high-risk recall** (don't miss contaminated zones), accepting some false alarms.
- **G3.** **Guide targeted sampling** — output GPS-tagged sample plans that improve lab representativeness.
- **G4.** Provide **confidence, reason codes, and out-of-distribution (OOD) warnings** with every output.
- **G5.** Build a reproducible, **multi-region** crop–pesticide–spectra–lab dataset as a durable asset.
- **G6.** Keep certified lab methods as the **reference truth** and route high-impact decisions to humans.

### Non-goals (v1) — see also [`00`](00-executive-overview.md) and [`06`](06-risk-compliance.md)
- **N1.** No certified concentration (mg/kg, ppm) from flight data.
- **N2.** No MRL compliance/non-compliance determination without lab confirmation.
- **N3.** No claim of universal coverage across all crops/pesticides/weather.
- **N4.** AI confidence is **not** treated as chemical or regulatory proof.

## 3. Users / personas and their needs

| Persona | Main need | Key dashboard surface |
|---|---|---|
| **Farmer / grower cooperative** | Know if a crop is safe to harvest or should be sampled | Simple low/med/high field map + plain-language advisory |
| **Exporter** | Avoid shipment rejection; select batches for lab confirmation | Batch-level risk report + lab queue |
| **Food-testing lab** | Receive more representative samples | GPS-tagged sample plan + chain-of-custody record |
| **Agriculture / regulatory agency** | Monitor spray practice & risk hotspots | Aggregated, anonymized maps + trend dashboard |
| **Research partner** | Improve model & dataset | Access to calibrated spectra, metadata, lab labels |

Detailed UI treatment of each surface is in [`../design.md`](../design.md).

## 4. Representative user stories

- *As a grower-cooperative manager*, I want a one-glance field map so I can decide whether a block is
  clear to harvest or needs sampling — **with a visible reminder that this is screening, not a lab result.**
- *As an exporter*, I want batches ranked by risk and a one-click lab queue so I send the right
  lots for GC-MS/MS confirmation before shipping.
- *As a lab coordinator*, I want a GPS-tagged sampling plan and a chain-of-custody record so field
  samples are traceable end-to-end.
- *As a regulatory officer*, I want anonymized hotspot trends across regions so I can target advisories.
- *As a researcher*, I want versioned, calibrated spectra joined to lab labels so I can retrain and
  benchmark models reproducibly.

## 5. Scope

**In scope (planning phase → eventual build):** ingestion of flights and metadata; radiometric
calibration → reflectance; QC/cloud-shadow masking; canopy/fruit segmentation; risk inference with
confidence/OOD; reason codes & explainability; GPS-tagged sample-plan generation; role-based
dashboards; dataset capture joined to lab results; auditability/provenance.

**Out of scope (v1):** quantitative concentration estimation; autonomous harvest-hold decisions;
real-time on-board inference (post-flight processing acceptable initially); pesticide-by-name
identification claims; non-pilot crops.

## 6. Functional requirements

The system is a **workflow**, not just a model. End-to-end path (scientific basis: [`science.md`](science.md)):

1. **FR1 — Flight & metadata intake.** Capture flight record + crop/spray/weather metadata + calibration record (schema in [`03`](03-data-architecture-governance.md)).
2. **FR2 — Radiometric calibration → reflectance.** Dark-current, white/gray panel, irradiance, empirical-line correction; produce calibrated reflectance products.
3. **FR3 — Quality control & masking.** Remove saturated/blurred/cloud/shadow-dominated pixels; emit a **coverage-quality** measure.
4. **FR4 — Segmentation.** Identify crop canopy and visible fruit/leaf regions before inference.
5. **FR5 — Risk inference.** Produce per-zone **risk class** + calibrated **risk score**.
6. **FR6 — Confidence & OOD.** Emit **confidence** (high / uncertain / OOD) and route OOD cases to manual sampling / lab.
7. **FR7 — Explainability.** Emit **reason codes** (e.g., SWIR anomaly, spray timing, high-stress patch, prior high-risk pattern) + wavelength importance + spatial attention.
8. **FR8 — Action recommendation.** Map outputs to an operational next step: *clear / collect sample / close-range scan / send to lab*.
9. **FR9 — Sampling plan.** Generate GPS-tagged sample points spanning low/medium/high zones; produce chain-of-custody records.
10. **FR10 — Lab loop.** Ingest lab results, join to pixels/zones, and update the training dataset.
11. **FR11 — Role-based dashboards.** Serve the five persona surfaces (§3) with appropriate aggregation/anonymization.
12. **FR12 — Provenance.** Persist model version, sensor serial, calibration record, and flight conditions for every prediction.

### Output contract (canonical — reused in UI and API)
| Field | Meaning | Example |
|---|---|---|
| Risk class | Operational classification for a zone/batch | low · medium · high |
| Risk score | Calibrated probability-like score | 0.86 |
| Confidence | Model reliability after uncertainty estimation | high · uncertain · OOD |
| Reason codes | Interpretable drivers | "SWIR anomaly; spray 2 d ago; high-stress patch" |
| Action | Next operational step | clear · collect sample · close-range scan · send to lab |

## 7. Non-functional requirements

- **NFR1 — Reproducibility.** Preprocessing recipe is **locked before validation**; runs are
  versioned (data + model + code) so any prediction is re-derivable. See [`04`](04-ai-ml-modeling-plan.md).
- **NFR2 — Geospatial repeatability.** The same zone classifies stably across repeat flights
  (within tolerance) — required for grower trust.
- **NFR3 — Calibration stability.** Reflectance drift stays within a predefined tolerance across days.
- **NFR4 — Auditability.** Every output carries provenance (FR12) and a chain-of-custody link for any sampled point.
- **NFR5 — Safety-by-default UX.** Outputs are always labeled screening; lab-confirmation is the
  prescribed path for compliance decisions; OOD/uncertain states are surfaced, not hidden.
- **NFR6 — Privacy / non-personal data.** Datasets are non-personal; aggregated views are anonymized. See [`03`](03-data-architecture-governance.md).
- **NFR7 — Extensibility.** New crops, pesticides, sensors (VNIR→+SWIR), regions, and jurisdictions can be added without re-architecting (domain adaptation, active learning).
- **NFR8 — Performance posture.** Post-flight processing acceptable in v1; architecture leaves room for edge inference later.

## 8. Success metrics (pilot targets)

*Source: §9.3. These are the acceptance bar for the controlled-plot and pilot phases.*

| Metric | Pilot target | Why it matters |
|---|---|---|
| **High-risk zone recall** | **≥ 90%** (controlled-plot validation) | Avoid missing suspicious zones (primary safety metric) |
| **High-risk precision** | **≥ 65–75%** initial | Keep lab workload manageable |
| AUC / PR-AUC | Report **by crop and pesticide family** | Informative under class imbalance |
| Geospatial repeatability | Stable zone class across repeat flights | Grower trust |
| Calibration stability | Reflectance drift within tolerance | Multi-day comparison |
| Lab-confirmation uplift | More high-risk samples found per lab test than blind sampling | Demonstrates business value |
| Model-abstention quality | Uncertain/OOD cases routed correctly | Safe & trusted AI behavior |

**Validation discipline (summary; full method in [`04`](04-ai-ml-modeling-plan.md)):** split by
**field and date, not random pixels**; use **independent validation farms**; track
**per-pesticide / per-crop / per-season** separately; compare **drone-only vs metadata-only vs
fused** to prove the value of spectroscopy.

## 9. Pilot scope (crops, pesticides, scale)

- **Crops (5):** grapes, chilli, tomato, okra, tea — globally traded, high residue/export relevance,
  plot-trial feasible. The crop set is **configurable per deployment region**.
- **Pesticides:** crop-specific, based on real local usage, export/import-rejection history, official
  residue-monitoring priorities (per jurisdiction), and lab-partner capability. **First phase: 3 crops
  × 5–8 active ingredients**, plus untreated controls and legal-dose vs over-dose plots. Include
  insecticides, fungicides, and mixed sprays.
- **Dataset scale (phased):** bench proof 300–500 → controlled plots 1,500–3,000 → farm pilot
  5,000–10,000 → pre-commercial 50,000+ (detail in [`03`](03-data-architecture-governance.md)).

## 10. Assumptions & dependencies

- Partnerships with an agricultural university / grower cooperative / accredited lab are secured
  (M1–M2; see [`07`](07-roadmap-task-breakdown.md)).
- Public hyperspectral/agriculture datasets bootstrap the pipeline and vegetation/segmentation
  models; **public data lacks pesticide-residue labels**, so the multi-region lab-linked dataset is
  the gating asset (see [`03`](03-data-architecture-governance.md)).
- Drone operations comply with the **applicable national/regional drone regulations** of each
  operating jurisdiction (see [`06`](06-risk-compliance.md)).

## 11. Open questions

- Final pilot crop/pesticide shortlist per launch region (depends on lab-partner capability and
  export/import-rejection data).
- Zone granularity for "risk class" (per-pixel patch vs management zone vs batch) — to be fixed in `04`.
- Whether SWIR is added in the controlled-plot phase or deferred (cost/benefit test).
