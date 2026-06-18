# 04 — AI / ML Modeling Plan

*Source: concept doc §4.5 (preprocessing), §5 (residue science & detection limits), §8.2–8.5
(model stages, outputs, explainability, drift), §9.1–9.3 (validation & metrics).*

## 1. The modeling problem (why this is hard)

A drone measures **radiance from a mixed surface**, and the pesticide-related signal is a *small*
component inside crop, soil, shadow, water, illumination, and noise effects. The underlying physics
and chemistry are detailed in [`science.md`](science.md). On real canopies the
residue layer is **thin, uneven, weathered, degraded, and mixed** with wax/water/dust. So the model
should not chase certified concentration; it should learn **risk** from a combination of weak direct
features and stronger indirect/contextual patterns.

### Detection modes the model exploits
| Mode | What it means | Drone suitability | Example output |
|---|---|---|---|
| **Direct chemical signal** | Spectral features linked to pesticide molecules/residue films | Possible in controlled conditions; harder from height | "Zone B resembles high-residue sprayed plots" |
| **Indirect crop response** | Crop stress, leaf-surface/wax/water change, spray pattern | More feasible for drone mapping | "Zone B has abnormal post-spray spectral behavior" |
| **Contextual risk** | Spray history + weather + PHI + crop + spectral anomaly together | Highly practical | "High-risk: spray timing + spectral pattern + rain history match prior high-residue cases" |

**Implication:** **metadata fusion is not optional** — spray/weather/PHI context often carries more
reliable signal than the spectrum alone, and proving the *uplift* of spectroscopy over metadata is a
core validation goal (§5).

### Why MRL-level measurement from the air is out of scope (v1)
MRLs are concentrations in the **homogenized edible matrix**, established by sampling → extraction →
cleanup → separation → MS detection. A drone sees the **outer canopy/fruit surface from a distance**,
not the edible sample. Therefore FASAL estimates **risk of residue presence / over-application**, not
certified mg/kg. Quantification can grow over time, but only with strong crop- and pesticide-specific
calibration against lab-confirmed samples. (See [`00`](00-executive-overview.md), [`06`](06-risk-compliance.md).)

### Where SERS/Raman fits (future)
Surface-enhanced Raman gives stronger molecular specificity but needs close sample interaction, a
substrate, and controlled geometry — strong for **handheld/bench confirmation**, weak as the primary
high-altitude sensor. A future **UAV→ground-rover hybrid** could use the drone for zone selection and
a ground robot/operator for close-range Raman/SERS. Not in v1.

## 2. Preprocessing recipe (version-locked before validation)

Preprocessing converts raw spectra into a stable model input. The recipe below is **locked and
versioned before validation** to avoid inflated performance, and is implemented in `pipeline/preprocess`
([`02`](02-system-architecture.md)).

1. Dark-current subtraction.
2. White/gray-reference normalization → **radiance-to-reflectance** conversion
   (`ρ_sample(λ) = [(DN_sample − DN_dark)/(DN_white − DN_dark)] · ρ_white`), plus irradiance/geometry
   correction and panel-based empirical-line calibration in field conditions (see [`05`](05-field-ops-hardware-plan.md)).
3. Spectral resampling to a common band grid.
4. **Savitzky-Golay** smoothing; first/second **derivative** spectra.
5. **Standard Normal Variate (SNV)** and/or **Multiplicative Scatter Correction (MSC)**.
6. **Bad-band removal** (noisy/water-absorption bands).
7. **Cloud/shadow masking** and saturation/blur removal → **coverage-quality** metric.
8. **Vegetation / fruit segmentation** before inference.

> Each preprocessing config is a versioned artifact (DVC); the exact recipe used is part of every
> prediction's provenance.

## 3. Modeling stages (start simple; earn complexity)

Begin simple and only advance after the dataset and validation are stable.

### Stage 0 — Feature baselines (first)
Vegetation indices, spectral derivatives, **PCA**, **PLS-R / PLS-DA**, **Random Forest**, **SVM**,
**gradient boosting**. Goal: establish honest, interpretable baselines and confirm whether the
chosen pesticides create *any* measurable, separable signal (bench → controlled plots).

### Stage 1 — Deep spectral / spatial models
- **1D CNN** over spectra (per-pixel/zone).
- **2D / 3D CNN** over spectral-spatial patches (texture + neighborhood).
- Segmentation backbone (U-Net-style) for canopy/fruit isolation feeding the above.

### Stage 2 — Multimodal fusion (target architecture)
Three branches → fusion → calibrated risk, with confidence and reason codes (source Figure 8):
```
spectral branch (1D/3D CNN on reflectance)  ┐
spatial  branch (2D CNN on patches/texture) ├─► fusion (attention/transformer) ─► risk score
metadata branch (spray/weather/PHI/crop)    ┘                                      │
                                            uncertainty/OOD ─► confidence          │
                                            explainability  ─► reason codes ───────┘
```

## 4. Output design (canonical contract)

Matches the output contract in [`01`](01-product-requirements.md) and the UI in [`../design.md`](../design.md):

| Output | Meaning | Example |
|---|---|---|
| **Risk class** | Operational classification for a zone/batch | low · medium · high |
| **Risk score** | Calibrated, probability-like score | 0.86 |
| **Confidence** | Reliability after uncertainty estimation | high · uncertain · OOD |
| **Reason codes** | Interpretable drivers | SWIR anomaly · spray timing · high-stress patch · prior high-risk pattern |
| **Action** | Next operational step | clear · collect sample · close-range scan · send to lab |

Scores are **calibrated** (e.g., isotonic/Platt) so a "0.86" is meaningful across crops/seasons.

## 5. Uncertainty & out-of-distribution (OOD)

The model must know when it is **outside its training experience** (new variety, new formulation,
dusty/dry field, unexpected disease, unusual lighting, new sensor, new region) and **abstain → route
to manual sampling / lab** rather than assert. Approaches: MC-dropout / deep ensembles for predictive
uncertainty; feature-space density / distance-to-training for OOD. **Abstention quality is a graded
success metric** (§7). OOD rate is monitored as a drift signal ([`02`](02-system-architecture.md) §7).

## 6. Explainability (every high-risk call must justify itself)

Farmers, exporters, and regulators will not trust a black box. Provide:
- **Wavelength importance** (which bands drove the call) — mapped to the spectral chart in the UI.
- **Spatial attention maps** (where the model looked).
- **Comparison to known controls** (how the zone differs from untreated/legal-dose plots).
- **Reason codes** (human-readable drivers) and **uncertainty warnings**.

Implemented with SHAP / attention / prototype-distance methods (`models/` in [`02`](02-system-architecture.md)).

## 7. Validation methodology & metrics

### 7.1 Discipline (prevents inflated accuracy)
- **Split by field and date, not random pixels** — pixel-level random splits leak field conditions.
- Use **independent validation farms** after the controlled-plot phase.
- Track **per-pesticide, per-crop, per-season** performance separately.
- **High-risk recall is the primary safety metric** (missing contaminated zones is worse than false alarms).
- **Report false positives** (too many needless lab samples reduces operational value).
- **Ablation:** compare **drone-only vs metadata-only vs fused** to prove spectroscopy's uplift.

### 7.2 Targets (pilot) — mirrors [`01`](01-product-requirements.md) §8
| Metric | Pilot target |
|---|---|
| High-risk zone recall | **≥ 90%** (controlled-plot) |
| High-risk precision | **≥ 65–75%** initial |
| AUC / PR-AUC | report by crop & pesticide family |
| Geospatial repeatability | stable class across repeat flights |
| Calibration stability | reflectance drift within tolerance |
| Lab-confirmation uplift | more high-risk samples found per lab test than blind sampling |
| Abstention quality | uncertain/OOD routed correctly |

### 7.3 Reporting artifacts
Confusion matrices **by crop, pesticide family, farm, and season**; PR/ROC curves under class
imbalance; calibration-reliability plots; ablation tables; per-flight repeatability summaries.

## 8. Generalization & continuous improvement
- **Region-wise validation**, **domain adaptation**, and **active learning** to combat "trained in
  one state, fails in another".
- The lab loop ([`02`](02-system-architecture.md) §M) continuously enlarges the labeled set; retrains
  are tracked in MLflow and tied to DVC dataset versions for reproducibility.

## 9. Modeling milestones (→ [`07`](07-roadmap-task-breakdown.md))
- **M3–M7:** reflectance pipeline, segmentation, QC masks, **baseline** (Stage 0).
- **M5–M8:** **AI model v1** with uncertainty + explainability (Stages 1–2).
- **M8–M11:** independent farm pilot, targeted sampling, lab comparison, ablations.
- **M10–M12:** validation report (by crop/pesticide/farm/season) + dataset publication plan.
