# Science — How FASAL Uses Spectrometer Data

*Standing scientific reference. Unlike the proposal docs, this file is meant to **persist into the
build** — the pipeline, feature engineering, and model code should be traceable back to the physics
and chemistry here. Companion to [`02-system-architecture.md`](02-system-architecture.md) (where the
pipeline lives), [`04-ai-ml-modeling-plan.md`](04-ai-ml-modeling-plan.md) (how features become a
model), and [`05-field-ops-hardware-plan.md`](05-field-ops-hardware-plan.md) (how data is captured).*

> **Bottom line the science forces:** a spectrometer on a drone measures **light**, not molecules.
> The pesticide-related signal is a *small* part of a much larger optical signal. The defensible
> scientific product is therefore a **risk map**, validated against **lab chemistry** — not a
> certified concentration. Every section below explains *why*.

---

## 1. The measurement chain — from photons to a number

A hyperspectral imager is an array of tiny spectrometers: for every pixel it records **reflected
radiance at many narrow, contiguous wavelengths**. It does **not** measure chemical concentration;
it measures how much light of each wavelength arrives at the sensor.

### 1.1 What reaches the sensor (the measurement model)
The radiance recorded at wavelength λ for a surface point is approximately:

```
L_sensor(λ) = E_sun(λ) · ρ_surface(λ) · G(θ_sun, θ_view, φ) + L_path(λ) + N_sensor(λ)
```

| Term | Meaning | Why it matters |
|---|---|---|
| `L_sensor(λ)` | Radiance measured at the sensor | The raw observable |
| `E_sun(λ)` | Incoming solar irradiance | Changes with sun angle, cloud, haze, time of day |
| `ρ_surface(λ)` | **Surface reflectance** | The quantity we actually want — closer to an intrinsic property |
| `G(θ_sun,θ_view,φ)` | Sun–view geometry & canopy structure | Same leaf looks different at different angles (BRDF, §6) |
| `L_path(λ)` | Atmospheric/path radiance | Scattering/absorption between surface and sensor |
| `N_sensor(λ)` | Sensor noise | Dark current, gain, detector temperature |

**Key consequence:** the chemically meaningful term is `ρ_surface(λ)`. Everything else is nuisance
that must be removed or modelled before any AI is applied.

### 1.2 Digital numbers vs radiance vs reflectance
Raw images are stored as **digital numbers (DN)** that depend on exposure, gain, detector
temperature, lens response, solar angle, cloud cover, and illumination. DN is **not comparable**
across flights, times, or sensors. For science we must convert DN → **calibrated reflectance**, an
(approximately) intrinsic surface property that *is* comparable. This conversion is non-negotiable
and is the first scientific gate in the pipeline.

## 2. Calibration — turning brightness into reflectance

Reflectance calibration removes illumination and sensor effects so that two flights of the same
field are comparable. The core normalization (controlled imaging) is:

```
ρ_sample(λ) = [ (DN_sample(λ) − DN_dark(λ)) / (DN_white(λ) − DN_dark(λ)) ] · ρ_white(λ)
```

where `DN_dark` is the dark-current frame and `DN_white` is a calibrated reference panel of known
reflectance `ρ_white`. In the field this must be augmented with:

- **Downwelling irradiance** measurement (to track changing sunlight, `E_sun`).
- **Empirical-line calibration** using multiple ground reference panels (white/gray/black).
- **Geometry handling** for sun–view effects (`G`, §6).
- **Quality filtering** (saturation, blur, cloud, shadow).

Without correct calibration, the model learns *lighting and sensor artifacts*, not the surface.
Calibration **stability across days** is a tracked success metric. (Procedures: [`05`](05-field-ops-hardware-plan.md) §3.)

## 3. Hyperspectral imaging fundamentals

### 3.1 The data cube
A hyperspectral capture is a **3-D cube** `(x, y, λ)`: two spatial dimensions and one spectral
dimension. Each pixel carries a full **spectral signature** — reflectance as a function of
wavelength — instead of just 3 RGB values. That continuous spectrum is what lets us look for narrow
chemical absorption features.

### 3.2 Why narrow, contiguous bands matter
| Modality | Typical bands | Strength | Limit for pesticide risk |
|---|---|---|---|
| RGB | 3 broad | Cheap; crop/fruit detection; visible symptoms | Cannot resolve narrow chemical features |
| Multispectral | 4–12 broader | Vegetation indices; crop stress | May miss subtle pesticide-related features |
| **VNIR hyperspectral** | 100s narrow, ~400–1000 nm | Red-edge, chlorophyll, canopy stress, leaf structure | Mostly *indirect* residue signal; limited chemical specificity |
| **SWIR hyperspectral** | ~900–1700 nm (to ~2500 nm) | Stronger water, C–H, O–H, N–H, organic-molecule features | Costlier, heavier, harder to calibrate |
| Thermal | Long-wave IR | Water-stress / transpiration anomalies | Not pesticide-specific; auxiliary context only |

FASAL starts with **VNIR** (accessible, light) and evaluates **SWIR** in controlled plots, because
SWIR is where molecular C–H/O–H/N–H overtone information is strongest (§4).

### 3.3 Wavelength regions and what lives there
- **Visible (≈400–700 nm):** pigment electronic transitions (chlorophyll absorbs ~430 & ~660 nm) →
  greenness, pigment stress.
- **Red-edge (≈680–750 nm):** the steep reflectance rise; its position/shape is a sensitive **stress**
  indicator (chlorophyll, canopy condition).
- **NIR (≈750–1000 nm):** canopy structure, leaf internal scattering, biomass.
- **SWIR (≈1000–2500 nm):** **water absorption** (≈970, 1200, 1450, 1940 nm) and **overtone/combination
  bands** of organic bonds — the most promising window for molecular/residue-related information.

## 4. Why pesticide residues have spectral signatures (the chemistry)

Pesticide molecules contain bonds and groups — **C–H, O–H, N–H, C=O, P=O, S=O, aromatic rings,
halogenated structures** — that interact with light. The relevant interactions for a reflectance
imager are:

- **Electronic transitions** (UV–visible): strong but mostly from pigments, not trace residue.
- **Vibrational fundamentals** (mid-IR, ≈2500–25000 nm): the sharpest molecular fingerprints — but
  **outside** the VNIR/SWIR range typical drone sensors see.
- **Overtones & combination bands** (NIR/SWIR, ≈700–2500 nm): *weaker, broader* echoes of those
  fundamentals — **this is what a VNIR/SWIR imager can actually access** for organic chemistry.
- **Scattering changes** from surface films/wax alteration; occasionally **fluorescence**.
- **Raman scattering** (inelastic): a true molecular fingerprint, but practically a *close-range*
  technique (§9), not a high-altitude one.

### Why the field signal is weak
On a real canopy the residue layer is **thin, uneven, weathered, chemically degraded, and mixed**
with leaf wax, water, dust, and natural plant chemistry. So from drone height the accessible signal
is mostly **weak direct features + indirect field patterns** (spray coverage, crop stress, abnormal
spectral texture) rather than a clean molecular fingerprint. This is the single most important
scientific fact shaping the product.

## 5. Three detection regimes (why "risk," not "concentration")

| Regime | What the model keys on | Drone feasibility | Example statement |
|---|---|---|---|
| **Direct chemical signal** | Spectral features tied to residue molecules/films | Possible in controlled conditions; hard from height | "Zone B resembles high-residue sprayed plots" |
| **Indirect crop response** | Stress, wax/water-surface change, spray pattern | More feasible for drone mapping | "Zone B shows abnormal post-spray spectral behavior" |
| **Contextual risk (fusion)** | Spray history + weather + pre-harvest interval + crop + spectral anomaly | Highly practical | "High risk: spray timing + spectral pattern + rain history match prior high-residue cases" |

Because the direct signal is weak, **contextual fusion of spectra with metadata** often carries the
most reliable risk information — and proving the *uplift* of spectroscopy over metadata alone is a
core validation goal ([`04`](04-ai-ml-modeling-plan.md) §7).

## 6. The science of the confounds (why this is hard)

The nuisance terms in §1.1 are not small; modeling them *is* the problem.

- **Mixed pixels / spectral unmixing:** each drone pixel can contain leaf, fruit, stem, soil, shadow,
  water droplets, dust, and mulch. The observed spectrum is a **mixture**; the residue contribution
  can be far smaller than crop/soil/illumination effects. → fly lower in trials, segment canopy/fruit,
  sample visible crop zones.
- **BRDF & sun–view geometry:** surfaces don't reflect equally in all directions. Reflectance changes
  with sun angle, view angle, wind, row geometry, and gimbal angle — the *same* plant looks different
  at 09:30 and 14:30. → constrain time-of-day and viewing geometry; model geometry with metadata.
- **Illumination & atmosphere:** clouds and changing sun angle distort spectra. → irradiance sensors,
  reference panels, controlled time windows, shadow/cloud masking.
- **Biological & physical variation:** growth stage, variety, moisture, disease, and dust all move the
  spectrum. → control plots, multi-factor experimental design, domain adaptation.

These confounds are why **calibration (§2), flight protocol (§ [`05`]), and metadata (§5)** are not
optional add-ons but parts of the measurement itself.

## 7. Detection limits — and why airborne MRL quantification is out of scope

- **LOD / LOQ:** every analytical method has a limit of detection/quantification. A weak, mixed,
  weathered surface signal seen from meters away has a *high effective detection limit* for trace
  residue — far above regulatory thresholds.
- **What an MRL actually is:** a **Maximum Residue Limit** is a concentration in the **homogenized,
  edible** food matrix (e.g., mg/kg), established by sampling → extraction → cleanup → separation →
  mass-spectrometric detection. A drone sees the **outer canopy/fruit surface from a distance**, not
  the homogenized edible sample.
- **The chemical ground truth:** validated multi-residue lab methods — **QuEChERS extraction followed
  by GC-MS/MS and/or LC-MS/MS** — remain the reference. They are what "truth" means for training and
  evaluation; FASAL never replaces them.

**Therefore FASAL estimates risk of residue presence / over-application, not certified mg/kg.**
Quantification may improve over time, but only with strong crop- and pesticide-specific calibration
against many lab-confirmed samples. (Governance of this boundary: [`06`](06-risk-compliance.md).)

## 8. From spectra to model features (the science → code bridge)

This is the section to keep open while coding the pipeline and feature layer.

### 8.1 Preprocessing — each step has a physical purpose
*(Implemented in `pipeline/preprocess`; the recipe is **version-locked before validation** to avoid
inflated performance — see [`04`](04-ai-ml-modeling-plan.md) §2.)*

| Step | Physical purpose |
|---|---|
| Dark-current subtraction | Remove sensor offset/thermal signal (`N_sensor`) |
| White/gray-reference normalization → reflectance | Remove illumination & sensor response (§2) |
| Spectral resampling | Put all sensors/flights on one wavelength grid for comparability |
| **Savitzky–Golay smoothing** | Suppress high-frequency noise while preserving band shape |
| **Derivative spectra (1st/2nd)** | Enhance subtle/overlapping absorption features; suppress slow baseline drift |
| **SNV / MSC** | Remove multiplicative scatter & path-length effects (particle size, surface roughness) |
| Bad-band removal | Drop noisy / water-saturated bands that carry no usable signal |
| Cloud/shadow masking | Remove pixels where `E_sun`/geometry is invalid → coverage-quality metric |
| Canopy/fruit segmentation | Restrict analysis to the surfaces that actually matter (reduce mixing, §6) |

### 8.2 Physically meaningful features
- **Vegetation indices** (e.g., NDVI and relatives): chlorophyll/greenness & biomass proxies.
- **Red-edge metrics** (position/slope): sensitive crop-stress indicators (§3.3).
- **Water-band indices** (≈970/1200/1450/1940 nm): canopy/leaf moisture, which modulates residue
  weathering and the spectral background.
- **Derivative & band-ratio features** around C–H/O–H/N–H overtone regions: candidate *direct*
  residue-related descriptors (weak; SWIR-favored).

### 8.3 Dimensionality & chemometrics
Hundreds of bands are highly correlated. The scientifically standard reductions are:
- **PCA** — decorrelate and compress while keeping variance.
- **PLS-R / PLS-DA** — chemometric workhorses that relate spectra to a target (risk/label) while
  handling collinearity; strong, interpretable baselines.
- Then **ML/DL** (RF/SVM/GBM → 1D/2D/3D CNN → fusion) for nonlinear spectral–spatial–metadata
  patterns. Detail and staging in [`04`](04-ai-ml-modeling-plan.md) §3.

### 8.4 How the science maps to the model branches
```
reflectance spectrum  ─► spectral branch   (chemistry/overtone & index features, §4/§8.2)
spatial neighborhood  ─► spatial branch    (texture, spray-pattern, mixed-pixel context, §6)
spray/weather/PHI     ─► metadata branch   (contextual risk, §5)
                         └► fusion ─► calibrated risk score + confidence + reason codes
```
Reason codes and wavelength-importance close the loop back to this document: a "SWIR anomaly" reason
code should be explainable in terms of §3.3 / §4.

## 9. Quantification & the SERS/Raman upgrade path (future)
**Surface-enhanced Raman spectroscopy (SERS)** offers strong molecular specificity for trace
residues, but needs close sample interaction, a suitable substrate, controlled geometry, and
reproducible enhancement — making it a **handheld/bench confirmation** technique, not a primary
high-altitude sensor. A future **UAV → ground-rover/operator hybrid** could use FASAL for zone
selection and close-range Raman/SERS (or other point spectroscopy) for confirmation. Out of scope
for v1, but the architecture and dataset are designed not to preclude it.

## 10. Scientific validity & reproducibility principles
The same rigor that makes a lab result trustworthy applies here:
- **Lock preprocessing before validation** (no peeking; avoid inflated accuracy).
- **Design the experiment**: blank/control, correct-dose, over-dose, mixed-pesticide, varied
  pre-harvest intervals and weather, multiple varieties — so the model learns *residue risk*, not
  location/soil/variety ([`05`](05-field-ops-hardware-plan.md) §4).
- **Split by field and date, not random pixels** (pixel-random splits leak field conditions).
- **Ablate** drone-only vs metadata-only vs fused to attribute the signal.
- **Track calibration stability and geospatial repeatability** as first-class metrics.
- **Version data + recipe + model together** for reproducibility ([`03`](03-data-architecture-governance.md)).

## 11. Glossary
- **Radiance** — light power reaching the sensor per wavelength (the raw observable).
- **Reflectance (ρ)** — fraction of incident light a surface reflects; (approx.) intrinsic, comparable.
- **DN (digital number)** — raw, uncalibrated pixel value; sensor/illumination-dependent.
- **Hypercube** — `(x, y, λ)` data: an image with a full spectrum per pixel.
- **GSD (ground sample distance)** — ground size of one pixel; set by altitude/optics.
- **BRDF** — bidirectional reflectance distribution function; reflectance's dependence on sun/view angles.
- **Overtone / combination band** — weaker NIR/SWIR features derived from mid-IR vibrational fundamentals.
- **Red-edge** — the steep VIS→NIR reflectance rise (~680–750 nm); a stress indicator.
- **SNV / MSC** — scatter corrections (standard normal variate / multiplicative scatter correction).
- **Derivative spectroscopy** — using spectral derivatives to enhance subtle/overlapping features.
- **PCA / PLS** — dimensionality reduction / chemometric regression-discrimination.
- **LOD / LOQ** — limits of detection / quantification of a method.
- **MRL** — Maximum Residue Limit; a concentration in the edible matrix set by regulation.
- **QuEChERS** — "Quick, Easy, Cheap, Effective, Rugged, Safe" sample-prep for residue analysis.
- **GC-MS/MS, LC-MS/MS** — tandem mass-spectrometry methods; the chemical reference truth.
- **OOD** — out-of-distribution; inputs outside the model's training experience (route to lab).

## 12. References (scientific)
1. He et al., *Spectroscopic & Imaging Technologies Combined with Machine Learning for Pesticide
   Residues in Fruits and Vegetables*, Foods, 2025 — https://www.mdpi.com/2304-8158/14/15/2679
2. Daniels et al., *Identifying the Optimal Radiometric Calibration Method for UAV-Based Multispectral
   Imaging*, Remote Sensing, 2023 — https://www.mdpi.com/2072-4292/15/11/2909
3. Adão et al., *Hyperspectral Imaging: A Review on UAV-Based Sensors, Data Processing and
   Applications for Agriculture and Forestry*, Remote Sensing, 2017 — https://www.mdpi.com/2072-4292/9/11/1110
4. García-Vera et al., *Hyperspectral Image Analysis and Machine Learning for Agricultural Crops*,
   Sustainability, 2024 — https://www.mdpi.com/2071-1050/16/14/6064
5. Yu et al., *Recent Developments and Applications of Surface-Enhanced Raman Spectroscopy in
   Pesticide Detection*, 2025 — https://pmc.ncbi.nlm.nih.gov/articles/PMC12199038/
6. USGS, *Absolute radiometric calibration evaluation of Uncrewed Aircraft Systems*, 2025 —
   https://pubs.usgs.gov/publication/70272649
7. Internationally harmonized multi-residue analytical methods — QuEChERS (e.g., **EN 15662**;
   **AOAC 2007.01**) with GC-MS/MS and LC-MS/MS determination.
