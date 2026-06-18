# 03 — Data Architecture & Governance

*Source: concept doc §8.1 (data schema), §8.4–8.5 (explainability, drift), §11.3 (dataset scale),
§12.3 (claims governance).*

## 1. Data schema — the 8 core objects

These objects are the single source of truth and are mirrored as `shared/` schemas in code
(see [`02`](02-system-architecture.md)). They connect **drone pixels → field context → lab truth**.

| Object | Example fields | Purpose |
|---|---|---|
| **Flight record** | flight ID, date/time, pilot, drone ID, sensor ID, altitude, speed, overlap | Traceability & repeatability |
| **Spectral cube** | orthomosaic path, wavelength list, reflectance bands, pixel masks | Core model input |
| **Calibration record** | panel reflectance, panel image, irradiance file, dark frame, white frame | Quality control & reproducibility |
| **Crop metadata** | crop, variety, field ID, growth stage, canopy condition, irrigation | Domain adaptation & interpretation |
| **Spray metadata** | active ingredient, formulation, dose, application date/time, equipment, **PHI** | Critical context for risk prediction |
| **Weather metadata** | temperature, humidity, wind, rain, cloud cover, solar radiation | Explains residue degradation & spectral variability |
| **Ground sample** | GPS point, sample type, sample mass, chain of custody, lab ID | Connects drone pixels to lab truth |
| **Lab result** | pesticide, concentration, LOQ, recovery, method, uncertainty | Reference label for training & evaluation |

### Relationships (logical)
```
Flight record 1───n Spectral cube
Flight record 1───1 Calibration record
Flight record n───1 Field (Crop metadata)   Field n───n Spray metadata (by date)
Flight record n───n Weather metadata (by time/place)
Spectral cube ──(GPS/zone)── Ground sample 1───1 Lab result
```
The **GPS/zone join** (PostGIS) between spectral pixels/zones and ground samples is the heart of
supervised training; lab results attach to the zones the samples came from.

## 2. Dataset strategy

### 2.1 Phased scale (source §11.3)
| Phase | Suggested scale | Goal |
|---|---|---|
| Bench / close-range proof | 300–500 samples | Do the chosen pesticides create measurable spectral differences? |
| Controlled field plots | 1,500–3,000 GPS-tagged samples | Train first drone risk model with known treatments |
| Farm pilot | 5,000–10,000 field-linked samples over seasons | Generalize across farms, varieties, weather, operators |
| Pre-commercial | 50,000+ linked spectra/sample records | Robust regional models + a multi-region dataset asset |

### 2.2 Public datasets first — and an honest limitation
Per the project decision, **public datasets bootstrap the build before first-party field
collection**. They are useful for the **pipeline, calibration sanity checks, vegetation/segmentation
models, and architecture validation** — e.g., open UAV/airborne hyperspectral crop and vegetation
datasets and public spectral libraries.

> **Limitation stated up front:** public HSI datasets essentially **never carry pesticide-residue
> labels**. So public data cannot, by itself, train the residue-risk model. Its role is to derisk
> engineering (reflectance, masking, segmentation, indices, model plumbing). **The gating asset is
> the first-party, lab-confirmed crop–pesticide–spectra dataset built in the controlled-plot and
> pilot phases, spanning multiple regions/climates.** This is also precisely what makes FASAL's
> dataset a valuable open contribution.

### 2.3 Experimental design (so the model learns *residue risk*, not artifacts)
The dataset **must** include blank/control zones, correctly sprayed zones, over-sprayed zones,
mixed-pesticide zones, varied pre-harvest intervals, varied weather histories, and multiple crop
varieties. Without this design the model can learn **location, soil, disease, or variety** instead
of residue risk. (Validation split discipline is in [`04`](04-ai-ml-modeling-plan.md); scientific
rationale in [`science.md`](science.md) §10.)

## 3. Storage, versioning, and lineage

- **Object storage (S3/MinIO):** spectral cubes & orthomosaics as **cloud-optimized GeoTIFF (COG)**.
- **Metadata DB (PostgreSQL + PostGIS):** the 8 objects, geospatial joins, provenance.
- **Dataset versioning (DVC):** every dataset snapshot is content-addressed and linked to the model
  trained on it and the code/recipe used — satisfies reproducibility (NFR1) and the source doc's
  rule to **lock preprocessing before validation**.
- **Experiment tracking (MLflow):** metrics by crop/pesticide/season; model registry holds the
  exact model version stamped onto each prediction (FR12).
- **No raw data in git:** the repo holds schema definitions, DVC pointers, and **dataset cards**
  (provenance, licensing, coverage, known gaps) — not bytes.

## 4. Ground truth & chain of custody

- Samples are **GPS-tagged** and drawn from **low, medium, and high** risk zones (not just suspected-high)
  to support both calibration and validation.
- Each sample carries a **chain-of-custody** record from field → transport → lab → result.
- Lab reference = **QuEChERS extraction → GC-MS/MS and/or LC-MS/MS** (internationally harmonized
  methods, e.g. EN 15662 / AOAC 2007.01), with LOQ, recovery, method, and uncertainty stored on the
  **Lab result** object (full method in [`05`](05-field-ops-hardware-plan.md)).

## 5. Responsible AI & claims governance

This is a safety-critical product; governance is a feature, not paperwork. (See also
[`06`](06-risk-compliance.md).)

### 5.1 Claims rules (must hold in UI, API, and every report)
- **Never** market FASAL output as an accredited-lab residue certificate.
- Use lab-confirmed terminology only: **screened · risk flagged · targeted sample recommended ·
  lab confirmation required**.
- Keep full **chain-of-custody** for any sample sent to a lab.
- Persist **model version, sensor serial, calibration record, and flight conditions** for every prediction.
- **Human review** is required for high-impact decisions (harvest holds, exporter rejection,
  regulatory escalation).

### 5.2 Confidence ≠ proof
**Model confidence means model reliability, not chemical proof.** The UI and API present confidence
as an operational reliability signal alongside the mandatory lab-confirmation path — never as a
substitute for it.

### 5.3 Out-of-distribution (OOD) routing
The model must detect when it operates outside its training experience — new variety, new
formulation, dusty field, unexpected disease, unusual lighting, new sensor, new region/jurisdiction.
Such cases are **flagged OOD and routed to manual sampling / lab confirmation** rather than asserted.
OOD rate is monitored as a drift signal ([`02`](02-system-architecture.md) §7).

### 5.4 Explainability (what every high-risk call must expose)
Wavelength importance, spatial attention maps, comparison to known controls, **reason codes**, and
uncertainty warnings — e.g. *"High-risk because the SWIR moisture/organic-feature pattern + recent
spray metadata + spatial residue-like patchiness resemble lab-confirmed high-risk training
examples."* (Method in [`04`](04-ai-ml-modeling-plan.md); science of the features in
[`science.md`](science.md).)

## 6. Privacy & data classification
- Datasets are **non-personal** (fields, spectra, agronomic metadata, lab chemistry).
- Regulatory/aggregate and any cross-farm views are **aggregated and anonymized**.
- Farm/operator identifiers are access-controlled by role ([`02`](02-system-architecture.md) §7).
- Data residency and consent follow the **applicable jurisdiction's** requirements.

## 7. Dataset publication plan (open / FAIR)
- Publish a **curated, documented, multi-region crop–pesticide–spectra–lab dataset** with dataset
  cards (coverage, licensing, known gaps, calibration provenance) as an open contribution to the
  agricultural-AI research community ([`08`](08-pitch.md)).
- Release **calibrated spectra + metadata + lab labels** to research partners under governed access.
- Versioned releases (DVC tags) so published benchmarks are reproducible (FAIR principles).
