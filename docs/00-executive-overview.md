# 00 — Executive Overview

*Source: concept doc §1 (Executive summary), Core claim, §3 (Feasibility), Final positioning.*

## What FASAL is

FASAL is a drone-based **hyperspectral imaging + AI** system for **pre-harvest pesticide-residue
risk screening** in crop fields worldwide. A drone flies over a field before harvest, collects
radiometrically calibrated spectral images, converts raw radiance into surface reflectance,
segments crop canopy and fruit/leaf regions, and produces a **geospatial low / medium / high
risk heatmap**. That map tells operators **where to inspect, where to collect samples, and which
batches need certified lab confirmation**.

FASAL is a **decision-support and triage layer**. It moves part of the screening process
*upstream* — from reactive, blind, post-harvest sampling to proactive, field-scale risk mapping —
while preserving certified laboratory testing as the reference truth.

## The core claim (must survive every edit)

> **The drone will not directly certify pesticide concentrations. It will identify spatial risk
> patterns and guide targeted ground sampling, close-range spectroscopy, and confirmatory
> GC-MS/MS or LC-MS/MS testing.**

FASAL's defensible scientific target is a **high-recall pesticide-risk map**: minimize *missed*
high-risk zones even at the cost of some false alarms that ground sampling or the lab later resolves.
The physics and chemistry behind this — why a drone can *map risk* but not *certify concentration* —
are detailed in [`science.md`](science.md).

## What the drone can do well

- Capture **spatial variability across a whole field** instead of a few blind samples.
- Detect canopy stress, spray-pattern irregularity, residue-like spectral anomalies, drift zones,
  wash-off patterns, and likely over-application zones.
- Use **repeat flights** to observe change after spraying, rain, irrigation, or waiting periods.
- **Guide targeted sampling**, so lab samples better represent true field variation.
- Generate a scalable, multi-region spectral dataset linked to lab-confirmed results.

## What FASAL must NOT claim (v1)

- ❌ Certified pesticide concentration in mg/kg or ppm from flight data.
- ❌ Compliance / non-compliance with legal **Maximum Residue Limits (MRLs)** without lab confirmation.
- ❌ Universal detection across all crops, all pesticides, all weather.
- ❌ That AI confidence is chemical proof. **Model confidence ≠ regulatory proof.**

## Recommended approach (at a glance)

| Design element | Recommended approach | Reason |
|---|---|---|
| Primary output | Low / medium / high pesticide-**risk** heatmap | Field-scale screening is realistic; concentration certification from height is not |
| Sensor strategy | **VNIR hyperspectral first**, SWIR option later | VNIR is more accessible; SWIR adds organic/moisture features |
| AI model | Spectral + spatial + metadata **fusion** with uncertainty scoring | Residue signal is weak; must be separated from plant, soil, shadow, water, and spray-history effects |
| Truth source | GPS-tagged samples tested by **GC-MS/MS or LC-MS/MS** | Lab methods remain reference truth |
| Program fit | Agriculture AI application + dataset + responsible-AI workflow | Maps to common public-AI / agtech funding criteria: application, datasets, compute, startup, safe/trusted AI |

## Screening vs. lab — the trade-off being exploited

Drone hyperspectral imaging gives **high coverage and early, spatial signal**; certified lab
testing gives the **highest chemical specificity and regulatory reliability** but is costly,
centralized, sample-limited, and applied *after* produce enters the supply chain. FASAL sits
between them as a screening layer that makes scarce lab capacity go further by pointing it at the
right samples.

## Why now / funding & market fit (summary)

FASAL is an agriculture-focused AI application that produces a high-quality non-personal dataset,
an edge/cloud AI workflow, a startup commercialization path, and a safe/trusted-AI framework. These
map cleanly onto common public-interest AI and agtech funding criteria worldwide (application
development, datasets, compute, startup commercialization, and safe/trusted AI). Full alignment and
"the ask" are in [`08-pitch.md`](08-pitch.md).

## Final positioning

> FASAL is a **farm-scale AI surveillance and sampling-intelligence system**. It turns drone
> spectroscopy into an early-warning map and connects every high-risk claim back to a
> **lab-confirmed evidence loop**.
