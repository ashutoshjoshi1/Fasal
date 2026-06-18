# Growth Plan

*Source: derived from [`README.md`](README.md), [`00-executive-overview.md`](00-executive-overview.md),
[`01-product-requirements.md`](01-product-requirements.md), [`02-system-architecture.md`](02-system-architecture.md),
[`03-data-architecture-governance.md`](03-data-architecture-governance.md),
[`04-ai-ml-modeling-plan.md`](04-ai-ml-modeling-plan.md),
[`05-field-ops-hardware-plan.md`](05-field-ops-hardware-plan.md),
[`06-risk-compliance.md`](06-risk-compliance.md), [`07-roadmap-task-breakdown.md`](07-roadmap-task-breakdown.md),
[`08-pitch.md`](08-pitch.md), [`science.md`](science.md), and [`../design.md`](../design.md).*

## 1. Growth thesis

FASAL should grow as a **validated screening and sampling-intelligence platform**, not as a shortcut
replacement for certified residue testing. The project earns adoption by proving that calibrated
drone hyperspectral imagery, spray/weather/PHI metadata, and lab-linked learning can identify
field zones that deserve targeted sampling before harvest.

The growth wedge is simple:

> **Help growers, exporters, labs, and agencies find more true high-risk residue cases per lab test
> than blind sampling, while keeping every compliance decision tied to certified lab confirmation.**

This thesis preserves the core claim from the existing docs: FASAL produces a **low / medium / high
pesticide-risk map** with confidence, reason codes, and recommended next action. It does **not**
certify pesticide concentration, mg/kg, ppm, or MRL compliance from the drone.

## 2. Growth principles

| Principle | What it means for growth |
|---|---|
| **Trust before scale** | Adoption depends on scientific discipline, calibrated outputs, provenance, and claims governance. |
| **Validation before promotion** | Marketing should follow controlled-plot and independent-farm evidence, not lead it. |
| **Partners before mass distribution** | Early growth comes through agricultural universities, grower cooperatives, accredited labs, exporters, and public programs. |
| **Dataset as a durable asset** | The multi-region crop-pesticide-spectra-lab dataset becomes a scientific and commercial moat. |
| **Workflow, not model demo** | The product must help users act: inspect, sample, queue lab tests, review provenance, and close the lab feedback loop. |
| **Region-agnostic, locally adapted** | The platform architecture stays global, while crops, pesticides, drone rules, lab methods, and language/localization adapt per region. |

## 3. Beachhead customers

FASAL has five documented personas, but the first commercial wedge should focus on users with urgent
economic pain and clear ability to act on risk information.

| Segment | Pain | First offer | Adoption signal |
|---|---|---|---|
| **Grower cooperatives** | Need field-level harvest and sampling guidance across many farms. | Pilot scans + sampling plans for high-residue-risk crops. | Repeat seasonal flights, cooperative-wide rollout, accepted sampling plan. |
| **Exporters** | Shipment rejection, delayed lots, unnecessary testing, reputation risk. | Batch-risk dashboard + lab queue before shipment. | Paid pilot, lab-confirmation uplift, fewer blind tests per accepted shipment. |
| **Food-testing labs** | Receive blind or poorly representative samples. | GPS-tagged sample-plan workflow + chain-of-custody intake. | Lab partner MoU, sample manifest adoption, turnaround integration. |
| **Agriculture / regulatory agencies** | Need anonymized hotspot and spray-practice intelligence. | Aggregated regional trend dashboard after pilot validation. | Public-sector pilot, anonymized reporting request, policy/research use. |
| **Research partners** | Need calibrated spectra, metadata, and lab labels. | Governed dataset access + joint validation studies. | Data-sharing agreement, co-authored validation report, dataset citation. |

**Recommended first wedge:** one region, one accredited lab partner, one agricultural university or
grower cooperative, and **3 priority crops x 5-8 active ingredients** as described in
[`01-product-requirements.md`](01-product-requirements.md). Exporters and cooperatives should be the
primary buyer targets; labs and universities should be the trust and evidence partners.

## 4. Growth stages

| Stage | Timing | Goal | Proof needed | Growth motion |
|---|---|---|---|---|
| **0. Credibility foundation** | M1-M2 | Secure partners, crop/pesticide shortlist, governance, and claims discipline. | MoUs, ethics/data-governance plan, lab chain-of-custody path. | Partner-led pilots and funder conversations. |
| **1. Controlled proof** | M2-M7 | Prove calibrated spectral pipeline and baseline residue-risk separation. | Controlled plots, reflectance pipeline, baseline metrics by crop/pesticide. | Technical briefs, research validation, early customer discovery. |
| **2. Farm pilot adoption** | M8-M12 | Show field workflow value on independent farms. | Targeted sampling, lab comparison, recall/precision, lab-confirmation uplift. | Paid pilots, exporter/cooperative case studies, dashboard demos. |
| **3. Pre-commercial expansion** | Year 2 | Repeat across seasons, farms, crops, and regions. | Generalization metrics, unit economics, repeat usage, operator SOP maturity. | Regional partner network, service packages, enterprise dashboards. |
| **4. Platform ecosystem** | Year 3+ | Become the trusted field intelligence layer for residue-risk screening. | Multi-region dataset, validated models, APIs, lab/regulatory integrations. | SaaS plus services, dataset partnerships, agency/regional monitoring. |

## 5. Phase detail

### Stage 0 - Credibility foundation

Growth starts before the product is fully built. The first objective is to become fundable,
partnerable, and scientifically credible.

Key actions:
- Sign MoUs with an agricultural university, grower cooperative, and accredited residue lab.
- Lock the initial crop/pesticide shortlist using local usage, export/import rejection history,
  regulatory residue priorities, and lab capability.
- Finalize the ethics, data governance, chain-of-custody, and claims-governance plan.
- Package a reviewer-safe pitch: **screening, not certification**.
- Build a pilot charter that names the scientific success metrics, field SOP, sample counts, and
  lab methods.

Exit condition: partners agree that FASAL is a decision-support and targeted-sampling system, and
the first controlled trial can run without claims ambiguity.

### Stage 1 - Controlled proof

The controlled-plot phase should grow evidence, not hype. The goal is to prove whether the chosen
crops and pesticides create measurable, operationally useful risk patterns.

Key actions:
- Run untreated, legal-dose, over-dose, and mixed-spray plots.
- Capture VNIR hyperspectral, RGB, irradiance, calibration panels, GNSS/IMU, spray metadata, weather
  metadata, and lab samples.
- Build the reproducible reflectance pipeline, QC masks, segmentation, and baseline models.
- Compare drone-only, metadata-only, and fused models to prove spectroscopy's uplift.
- Report metrics by crop, pesticide family, field, date, and season.

Exit condition: the team can show a reproducible baseline with honest limitations, including where
the signal is weak, where OOD routing is needed, and whether SWIR is worth adding.

### Stage 2 - Farm pilot adoption

The farm pilot converts science into workflow value. This is where FASAL must prove that users can
act on the output.

Key actions:
- Run independent farm pilots with real cooperative/exporter/lab workflows.
- Produce heatmaps, confidence, reason codes, action recommendations, GPS sample plans, and
  chain-of-custody records.
- Measure lab-confirmation uplift versus blind sampling.
- Test the dashboard surfaces: field risk map, zone inspector, flights/QC, batch risk, lab queue,
  sampling plan, regional trends, and dataset/labeling.
- Create case studies that state both the value and the boundary: FASAL routes samples to labs; it
  does not certify residue concentration.

Exit condition: at least one customer segment can justify repeat use because FASAL improves sampling
quality, reduces blind testing, or catches risk earlier before harvest.

### Stage 3 - Pre-commercial expansion

Pre-commercial growth should happen region-by-region and crop-by-crop, not through a universal model
claim.

Key actions:
- Expand within the first region across more farms and repeat seasons.
- Add adjacent crops only when lab capability, field access, and validation design are available.
- Create operator training, calibration QA, and field SOP certification for partner drone teams.
- Decide the VNIR-only versus VNIR+SWIR package using a cost/benefit gate.
- Establish support, onboarding, lab turnaround expectations, and customer success workflows.

Exit condition: the business has repeatable acquisition, repeatable field operations, repeatable
model validation, and early unit economics.

### Stage 4 - Platform ecosystem

The long-term growth opportunity is a trusted residue-risk intelligence network: field sensing,
targeted sampling, lab confirmation, dataset publication, and continuously improving models.

Key actions:
- Publish governed dataset cards and research releases under FAIR principles.
- Offer API integrations for labs, exporters, agencies, and farm-management systems.
- Add close-range confirmation paths over time, such as handheld spectroscopy, Raman/SERS, or
  operator/rover workflows for high-risk zones.
- Support regional agencies with anonymized hotspot and trend dashboards.
- Build model monitoring for drift, OOD rate, calibration stability, and generalization across
  crops/regions.

Exit condition: FASAL becomes a trusted layer between field operations and lab confirmation, with a
dataset and workflow that are difficult to replicate.

## 6. Product growth loop

FASAL's strongest growth loop is evidence-driven:

1. A partner field is flown before harvest.
2. The system generates calibrated risk maps, confidence, reason codes, and sample plans.
3. Ground teams collect GPS-tagged samples from low, medium, and high zones.
4. The lab returns GC-MS/MS or LC-MS/MS results.
5. Results join back to field zones in the dataset.
6. The model improves through validated retraining and active learning.
7. Better maps create more trust, more flights, more lab-linked data, and more repeat usage.

The loop only works if the product preserves provenance: model version, sensor serial, calibration
record, flight conditions, sample chain-of-custody, and lab method.

## 7. Go-to-market motions

### Partner-led pilots
Use agricultural universities, cooperatives, accredited labs, and public-interest AI programs to
fund and validate the first pilots. This matches the funding alignment in [`08-pitch.md`](08-pitch.md)
and lowers trust barriers.

### Exporter assurance workflow
Sell to exporters as a pre-shipment risk-screening and lab-routing workflow. The value is fewer
blind samples, better targeted lab confirmation, and fewer surprises after produce enters the chain.

### Cooperative field service
Package FASAL as a seasonal field-screening service for grower cooperatives. This is likely easier
than pure self-serve software early because payload calibration, flight SOP, and lab coordination
remain operationally heavy.

### Lab channel
Labs can become distribution partners because FASAL sends them better-structured samples with GPS
context and chain-of-custody records. The message should be "make lab testing more representative,"
not "replace lab testing."

### Research and dataset partnerships
Use governed dataset access, benchmark reports, and co-authored studies to build credibility and
attract funding, talent, and ecosystem partners.

## 8. Commercial packaging

| Package | Buyer | What is included | Guardrail |
|---|---|---|---|
| **Validation pilot** | Funder, cooperative, exporter, agency | Field campaign, controlled protocol, dashboard demo, lab comparison, validation report. | No commercial claims beyond measured pilot scope. |
| **Field screening service** | Grower cooperative, large farm | Flight, calibration, risk map, sample plan, report, lab handoff. | Report says screened / risk flagged / lab confirmation required. |
| **Exporter risk dashboard** | Exporter, packhouse | Batch ranking, lab queue, PHI/spray context, provenance, exportable reports. | No shipment compliance certification without lab result. |
| **Lab sampling workflow** | Accredited lab | GPS sample manifest, custody timeline, result upload/join, lab-loop integration. | Lab remains reference truth. |
| **Agency trends dashboard** | Public agency, regulator, research program | Aggregated anonymized hotspots, crop/season trends, data-quality coverage. | No farm-level exposure without governance and permission. |
| **Research dataset access** | University, research partner | Calibrated spectra, metadata, lab labels, dataset cards, benchmark splits. | Governed access, licensing, and known-gap disclosure. |

## 9. Expansion scorecard

Before entering a new crop, region, or jurisdiction, score the opportunity against these criteria.
FASAL should expand only where both scientific validation and commercial pull are plausible.

| Criterion | What to look for |
|---|---|
| **Residue-risk pain** | Export rejections, strict buyer standards, high pesticide scrutiny, or public-health concern. |
| **Crop suitability** | Canopy/fruit visibility, repeatable flight windows, meaningful surface signal, feasible sampling. |
| **Lab capability** | Accredited lab can test the chosen active ingredients with GC-MS/MS or LC-MS/MS. |
| **Partner density** | Cooperative, university, exporter, and lab partners exist in the same operating region. |
| **Drone feasibility** | Civil-aviation permissions, safe flight areas, weather windows, trained pilots. |
| **Dataset value** | New region/crop improves generalization and fills a known dataset gap. |
| **Economic buyer** | Someone pays for reduced sampling waste, avoided rejection, earlier detection, or regional monitoring. |

## 10. Metrics

### North-star metric

**Lab-confirmation uplift:** how many more true high-risk zones or batches are found per lab test
when using FASAL-guided sampling compared with blind or conventional sampling.

### Scientific and model metrics

| Metric | Target / use |
|---|---|
| High-risk zone recall | Primary safety metric; pilot target is >= 90% in controlled plots. |
| High-risk precision | Keep lab workload manageable; initial target is 65-75%. |
| AUC / PR-AUC | Report by crop and pesticide family. |
| Geospatial repeatability | Same zone should classify stably across repeat flights within tolerance. |
| Calibration stability | Reflectance drift must stay within defined tolerance across days. |
| Abstention quality | Uncertain/OOD cases should route to manual sampling or lab confirmation. |
| Ablation uplift | Fused model should outperform metadata-only and drone-only baselines where spectroscopy adds value. |

### Operational metrics

| Metric | Why it matters |
|---|---|
| Flight-to-map turnaround time | Determines whether the system can inform pre-harvest action. |
| Coverage-quality pass rate | Shows whether field conditions and SOP are reliable. |
| Sample-plan acceptance rate | Measures whether ground teams trust and use the recommended GPS points. |
| Lab-result join rate | Measures whether the data loop closes cleanly. |
| Chain-of-custody completeness | Required for trust and downstream compliance decisions. |

### Growth metrics

| Metric | Why it matters |
|---|---|
| Signed partner MoUs | Early trust and field access. |
| Paid pilots / pilot renewals | Evidence that the value proposition survives procurement. |
| Repeat flights per season | Shows operational usefulness beyond a one-time demo. |
| Acres / fields / batches screened | Coverage growth, tracked alongside quality. |
| Lab tests routed through FASAL plans | Indicates workflow adoption by labs/exporters. |
| Dataset size and diversity | Long-term moat: records by crop, pesticide, region, season, sensor, and lab method. |

### Safety and trust metrics

| Metric | Why it matters |
|---|---|
| OOD rate by region/crop | Drift and expansion readiness signal. |
| Claims-governance incidents | Should remain zero; no certification language in reports/UI. |
| Human-review completion | Required for harvest holds, exporter rejection, or regulatory escalation. |
| Provenance completeness | Every prediction must be reproducible and auditable. |

## 11. First 12 months: growth operating plan

| Window | Growth objective | Deliverables |
|---|---|---|
| **M1-M2** | Become partner-ready. | Partner pitch, MoUs, crop/pesticide shortlist, governance plan, claims vocabulary, pilot charter. |
| **M1-M3** | Become field-ready. | Payload decision, calibration SOP, flight SOP, chain-of-custody setup, data schema. |
| **M2-M5** | Build first evidence. | Controlled plots, first flights, lab sample design, early dataset cards. |
| **M3-M7** | Become technically credible. | Reflectance pipeline, QC masks, segmentation, baseline models, first metric report. |
| **M5-M8** | Become demo-ready. | Model v1, confidence/OOD, reason codes, dashboard surfaces, sample-plan workflow. |
| **M8-M11** | Prove field value. | Independent farm pilots, targeted sampling, lab comparison, lab-confirmation uplift report. |
| **M10-M12** | Convert evidence into growth. | Validation report, demo package, case studies, funding ask, dataset publication plan, paid-pilot/LOI pipeline. |

## 12. Growth risks and mitigations

| Growth risk | Why it can slow adoption | Mitigation |
|---|---|---|
| **Overclaiming certification** | Regulators, labs, and exporters will reject unsafe claims. | Keep screening vocabulary in every report, UI, pitch, and contract. |
| **Too many false positives** | Labs and exporters may see FASAL as creating work, not saving work. | Track precision, lab workload, and lab-confirmation uplift; tune thresholds by use case. |
| **Poor regional generalization** | A model that works in one region may fail elsewhere. | Validate by region, crop, pesticide, season, field, and date; use OOD routing and active learning. |
| **Field operations are too complex** | Calibration and SOP failures can block repeatability. | Standardized SOP, operator training, calibration QA, coverage-quality gates. |
| **Slow lab turnaround** | The lab loop may be too slow for pre-harvest decisions. | Set partner SLAs, prioritize high-risk samples, and expose lab queue status in the dashboard. |
| **Hardware cost pressure** | SWIR and high-end payloads may hurt unit economics. | Start VNIR; add SWIR only after controlled cost/benefit evidence. |
| **Farmer trust gap** | Users may not trust a black-box risk map. | Use reason codes, spectral comparisons, provenance panels, agronomist-facing explanations, and human review. |

## 13. Year-one success definition

At the end of the first 12 months, FASAL should be able to say:

- We have signed field, lab, and research partners.
- We have a calibrated, reproducible pipeline from flight data to risk product.
- We have controlled-plot and independent-farm evidence reported by crop/pesticide/season.
- We can generate GPS-tagged sample plans and close the lab feedback loop.
- We can show whether FASAL-guided sampling improves lab-confirmed high-risk discovery versus blind
  sampling.
- We have a dashboard demo that communicates uncertainty, provenance, and lab-confirmation routing.
- We have a governed dataset publication plan and a credible funder/customer pipeline.

That is the right foundation for growth: not a louder claim, but a stronger evidence loop.
