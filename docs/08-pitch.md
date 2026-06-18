# 08 — Positioning & Pitch

*Source: concept doc §1, §2, §13, proposal-ready abstract, §14 references. Written for a **global**
audience — public-interest AI funders, agtech investors, food-safety agencies, export bodies, and
research grants in any region.*

## 1. Narrative

Produce moves from farms through wholesale markets, grower cooperatives, warehouses, exporters, and
processors to consumers. Pesticide-residue safety matters for public health, export/import
compliance, grower reputation, and consumer trust — yet lab testing is **costly, centralized,
sample-limited, and applied after produce has already entered the chain**. Sampling is largely blind.

**FASAL moves screening upstream.** A drone scans a field **before harvest**, and AI turns calibrated
hyperspectral imagery + spray/weather/PHI metadata into a **geospatial low/medium/high risk
heatmap**. That map points scarce lab capacity at the samples most likely to matter — converting
*reactive testing* into *proactive risk mapping*, while **certified labs remain the reference truth**.

FASAL is positioned as a **safe, trusted, decision-support layer**: every output carries confidence,
reason codes, out-of-distribution warnings, and a **lab-confirmation path** — never a certification.
It is region-agnostic by design and adapts to each jurisdiction's crops, pesticides, and rules.

## 2. Funding & program alignment

FASAL maps cleanly onto the criteria common to public-interest AI programs, agtech investors, and
agricultural-research grants worldwide:

| Funding/program criterion | FASAL alignment |
|---|---|
| **AI application with real-world impact** | A field-scale AI application for agriculture and food safety |
| **Open / high-value datasets** | A multi-region crop, pesticide, spray-history, hyperspectral, and lab-reference dataset (published under FAIR principles) |
| **Scalable compute use** | Training spectral-spatial deep models and multimodal fusion for agriculture |
| **Startup commercialization** | A clear path to a portable drone-analytics product for grower cooperatives, exporters, labs, and regulators |
| **Safe & trusted AI** | Confidence scores, explainability, OOD warnings, and lab-confirmation routing |

(Adapt the framing to the specific funder/program; the value dimensions above are intentionally
generic.)

## 3. Differentiation

- **Honest scope = trustworthy product.** FASAL screens risk and routes to the lab; it does not
  overclaim certification. That discipline is a feature for regulators and exporters.
- **Fusion, not just spectra.** Spray/weather/PHI metadata fused with spectral + spatial signal —
  with validated **uplift of spectroscopy over metadata** as a core result.
- **Dataset as a durable asset.** A reproducible, lab-linked, multi-region spectral dataset
  (versioned, documented) usable beyond this product.
- **Reproducibility & governance built in.** Locked preprocessing, provenance per prediction, OOD
  abstention, anonymized aggregates, per-jurisdiction compliance.

## 4. The ask

- **Compute:** access to GPU capacity (cloud grants or program compute) for spectral-spatial and fusion training.
- **Funding:** support across the 12-month plan ([`07`](07-roadmap-task-breakdown.md)) — payload,
  field campaigns, lab testing, and engineering.
- **Partners:** agricultural university / grower cooperative field sites and an accredited residue
  lab; introductions to regulators and exporters for pilots.
- **Dataset platform:** a path to publish the multi-region dataset under governed, FAIR access.

## 5. One-pager

> **FASAL — pre-harvest pesticide-risk screening for crop fields worldwide.**
> **Problem:** lab residue testing is costly, centralized, and post-harvest; sampling is blind.
> **Solution:** drone hyperspectral + AI → a field-scale low/medium/high **risk heatmap** that guides
> targeted sampling and lab confirmation.
> **Not:** a certified residue test. Labs remain the truth; FASAL is screening/triage.
> **Outputs:** risk class + calibrated score + confidence + reason codes + action (clear / sample /
> close-range scan / send to lab).
> **Users:** farmers/grower cooperatives, exporters, food labs, agriculture/regulatory agencies, researchers.
> **Targets (pilot):** ≥90% high-risk recall, 65–75% precision, validated per crop/pesticide/season.
> **Fit:** agriculture AI application + multi-region dataset + safe/trusted-AI workflow.
> **Ask:** compute + funding + field/lab partners + dataset-platform path.

## 6. Proposal-ready abstract

> **FASAL** is a UAV-based hyperspectral and artificial-intelligence platform for pre-harvest
> pesticide-risk screening in agricultural fields. The system combines VNIR/SWIR hyperspectral
> imaging, RGB imagery, flight metadata, spray-history metadata, radiometric calibration, and
> lab-confirmed GC-MS/MS or LC-MS/MS labels to generate geospatial risk maps for unplucked crops. It
> is designed to identify suspicious zones, guide targeted sampling, and reduce unnecessary laboratory
> testing while preserving certified lab methods as the reference truth. FASAL will create a
> multi-region crop–pesticide spectral dataset, a responsible-AI screening workflow with confidence
> and uncertainty scores, and a field dashboard for farmers, grower cooperatives, exporters, food
> labs, and agriculture/regulatory agencies. The platform is region-agnostic and adapts to each
> jurisdiction's crops, pesticides, and regulations, advancing agriculture AI application
> development, open dataset creation, scalable compute use, startup commercialization, and
> safe/trusted-AI deployment.

## 7. Suggested pitch-deck outline (for the design/deck step)
1. Problem (blind, post-harvest, costly testing) · 2. Insight (screen upstream) · 3. FASAL solution
(map → sample → lab) · 4. The reviewer-safe boundary (screening, not certification) · 5. How it works
(pipeline + fusion + uncertainty) · 6. Validation plan & targets · 7. Dataset asset · 8. Funding/market
alignment & the ask · 9. 12-month roadmap · 10. Team & partners.

## 8. References (scientific)

1. He et al., *Spectroscopic & Imaging Technologies + ML for Pesticide Residues in Fruits & Vegetables*, Foods, 2025 — https://www.mdpi.com/2304-8158/14/15/2679
2. Daniels et al., *Optimal Radiometric Calibration for UAV Multispectral Imaging*, Remote Sensing, 2023 — https://www.mdpi.com/2072-4292/15/11/2909
3. Adão et al., *Hyperspectral Imaging: UAV-Based Sensors, Data Processing & Applications*, Remote Sensing, 2017 — https://www.mdpi.com/2072-4292/9/11/1110
4. García-Vera et al., *Hyperspectral Image Analysis & ML for Agricultural Crops*, Sustainability, 2024 — https://www.mdpi.com/2071-1050/16/14/6064
5. Yu et al., *SERS in Pesticide Detection*, 2025 — https://pmc.ncbi.nlm.nih.gov/articles/PMC12199038/
6. USGS, *Absolute radiometric calibration of UAS*, 2025 — https://pubs.usgs.gov/publication/70272649
7. Internationally harmonized multi-residue methods — QuEChERS (**EN 15662**; **AOAC 2007.01**) with GC-MS/MS and LC-MS/MS.

*(See [`science.md`](science.md) for the full scientific basis and citations.)*
