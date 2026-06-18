# 05 — Field Operations & Hardware Plan

*Source: concept doc §6 (UAV payload & hardware), §7 (flight/calibration/field protocol),
§9.1 (lab reference method). **This is planned, not built** — it specifies the physical/operational
layer the software is designed around.*

## 1. UAV payload

### 1.1 Minimum-viable vs ideal
| Subsystem | Minimum choice | Ideal choice | Purpose |
|---|---|---|---|
| **Airframe** | Small/medium multirotor with stable gimbal | Industrial multirotor with RTK/PPK + payload headroom | Stable low-altitude, repeatable imaging |
| **Spectral sensor** | VNIR hyperspectral 400–1000 nm | VNIR + SWIR (900–1700 nm or 1000–2500 nm) | Capture crop-stress & residue-related patterns |
| **RGB camera** | Synchronized RGB | High-res RGB, global shutter | Canopy/fruit detection, row mapping, context |
| **Irradiance sensor** | Downwelling light sensor | Gimbal-stabilized upward irradiance spectrometer | Correct for changing sunlight |
| **Navigation** | GNSS + IMU | RTK/PPK GNSS + IMU + GCPs | Accurate geospatial heatmaps & repeat flights |
| **Compute** | Post-flight laptop processing | Edge GPU + cloud training pipeline | Faster inference & model updates |
| **Calibration** | Gray/white panels | Multi-level calibrated panels + field spectrometer checks | Radiometric repeatability across flights |

### 1.2 Why VNIR first, SWIR second
VNIR cameras are lighter, more available, and easier to fly; strong for vegetation health, red-edge,
canopy structure, and stress. SWIR is heavier/pricier but captures more water- and organic-bond
information. **Strategy:** start with **VNIR for field mapping**, then add **SWIR in controlled pilot
plots** to test whether the extra cost improves pesticide-risk discrimination enough to justify
deployment (cost/benefit gate; ties to the open question in [`01`](01-product-requirements.md)).

### 1.3 Flight-height trade-offs
| Altitude | Ground sample distance | Use case | Risk |
|---|---|---|---|
| 10–20 m | Very high detail | Experimental plots, fruit/leaf-zone mapping | Small coverage; flight/safety constraints |
| **20–50 m** | High detail | **Pilot farms & targeted mapping** | **Good balance for early trials** |
| 50–120 m | Moderate detail | Large-field coverage | More mixed pixels; weaker residue signal |
| Satellite/aircraft | Low–moderate | Regional crop-stress mapping | Not suitable for residue screening without major assumptions |

Early trials favor **20–50 m**; fly **lower in trials** to reduce mixed pixels (a key technical-risk
mitigation, [`06`](06-risk-compliance.md)).

### 1.4 Spectral sensor in practice — Avantes (AvaSpec) point spectrometer

The current spectral sensor is an **Avantes point spectrometer** (fiber-fed), not an imager. Its
output is **counts vs detector pixel**, which dictates the data path and the field controls
(see science.md "The instrument in practice"; code in `fasal/pipeline/spectrum.py`):

| Aspect | Record / set | Why |
|---|---|---|
| **Wavelength calibration** | Device polynomial coefficients (`AVS_GetLambda` / device file) | Maps pixel→wavelength; required before analysis |
| **Integration time** | Per-scan integration time (ms) | Counts (and dark) scale with it; used to normalize and avoid saturation |
| **Optical filter** | Active filter + passband | Sets the valid range/response; references taken with the same filter |
| **Field of view (FOV)** | Fiber/lens FOV (deg) | Footprint ≈ 2·d·tan(FOV/2) sets spatial resolution & scan overlap |
| **Dark & white references** | Dark + white-panel scans at the same filter & integration time | Reflectance = (sample−dark)/(white−dark)·ρ_white |

Because each scan is one footprint, the field "map" is a **set of geo-tagged point scans** along the
flight path (sparse/interpolated), not a dense raster. Plan flight speed, scan rate, FOV, and
altitude so footprints overlap enough for the intended sampling density.

## 2. Standard operating procedure (per flight)

1. **Before flight, record metadata:** crop type, variety, growth stage, spray history, pesticide
   product, formulation, dose, spray date/time, irrigation, rain, expected harvest date.
2. Place **calibrated white/gray/black reference panels** and record their GPS coordinates.
3. Perform **dark-current and white-reference checks** before takeoff and after landing.
4. Fly at **fixed altitude, speed, side/front overlap, and stable gimbal angle**.
5. Fly **near solar noon / within a controlled time window** to limit changing shadows & sun angle.
6. Capture **downwelling irradiance** continuously if possible.
7. Generate **radiance and reflectance** products; remove saturated/blurred/cloudy/shadow-dominated pixels.
8. **Segment canopy and visible fruit/leaf** regions before AI inference.
9. Generate the **risk heatmap**; select **GPS-tagged ground samples** from low, medium, and high zones.
10. **Send samples to the lab**; update the training dataset when results arrive (the lab loop).

These steps map 1:1 onto the software pipeline stages in [`02`](02-system-architecture.md) and the
data objects in [`03`](03-data-architecture-governance.md).

## 3. Calibration

**Reflectance normalization (controlled imaging):**
`ρ_sample(λ) = [(DN_sample(λ) − DN_dark(λ)) / (DN_white(λ) − DN_dark(λ))] · ρ_white(λ)`

Field work additionally needs **irradiance correction, geometry handling (sun-view/BRDF),
panel-based empirical-line calibration, and quality filtering** (see [`science.md`](science.md) §2 for why each step matters). Calibration records (panels,
irradiance, dark/white frames) are persisted (Calibration record object) for QC and reproducibility,
and **calibration stability** is a tracked success metric.

## 4. Field sampling strategy (design for training *and* validation)

Sampling must **train and validate** the model, not merely demonstrate it. The dataset must include:
**blank/control zones, correctly sprayed zones, over-sprayed zones, mixed-pesticide zones, varied
pre-harvest intervals, varied weather histories, and multiple crop varieties.** Without this design,
the model may learn **location, soil, disease, or variety** instead of residue risk.

- Draw GPS-tagged samples from **low, medium, and high** risk zones (not only suspected-high) to
  support calibration and validation.
- Maintain **chain-of-custody** for every sample ([`03`](03-data-architecture-governance.md) §4).
- Coordinate sample counts with the phased dataset scale in [`03`](03-data-architecture-governance.md) §2.1.

## 5. Lab reference method (the truth source)

For pesticide residues, the lab reference uses validated **multi-residue methods**: **QuEChERS
extraction** followed by **GC-MS/MS and/or LC-MS/MS**, depending on pesticide chemistry and matrix
(extraction → cleanup → separation → MS identification/quantification for fruits and vegetables).
Each result records **pesticide, concentration, LOQ, recovery, method, and uncertainty** (Lab result
object). These remain the **reference truth**; FASAL never replaces them.

## 6. People & partners (planning note)
- Trained/registered pilots as applicable under the operating jurisdiction's drone regulations ([`06`](06-risk-compliance.md)).
- Agricultural-university / grower-cooperative field partners for plots and pilot farms.
- An accredited residue lab for confirmatory testing and chain-of-custody handling.
(Partnership timeline in [`07`](07-roadmap-task-breakdown.md), M1–M3.)
