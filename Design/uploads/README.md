# FASAL — Planning & Proposal Documentation

**FASAL** is a drone-based hyperspectral + AI system that screens **pesticide-residue *risk*** in
unplucked crop fields and produces a geospatial **low / medium / high risk heatmap**. The map tells
farmers, FPOs, exporters, mandis, food-safety labs, and agriculture departments *where to inspect,
where to sample, and which batches to send for certified lab confirmation*.

> **Core claim (non-negotiable, repeated in every document).**
> FASAL is a **decision-support and triage layer — not** a certified laboratory residue test.
> The drone does **not** directly certify pesticide concentrations. It identifies **spatial risk
> patterns** and guides **targeted ground sampling, close-range spectroscopy, and confirmatory
> GC-MS/MS or LC-MS/MS testing**. Lab methods remain the reference truth.

> **Project name.** This project is **FASAL**. The originating concept document
> (`../DroneSpectra_AI_Design_Document.docx`) used the working title *"DroneSpectra AI"*; that name
> is retired and appears only for provenance.

---

## What this folder is

This is a **planning & proposal documentation suite** that turns the FASAL concept document into
structured, build-ready, fundable artifacts. **This phase is documentation only — no code yet.**
Decisions baked in (set with the project owner):

| Decision | Choice |
|---|---|
| Deliverable | Planning/proposal docs only (this phase) |
| Data strategy | **Public datasets first** for pipeline/segmentation/vegetation modeling; the India-specific lab-linked dataset is the asset to be built |
| Dashboard | **React / Next.js** web app (documented, not built) |
| Build priority | **Solid long-term foundation** — clean architecture, full data schema, reproducibility, extensibility |

A separate top-level **[`../design.md`](../design.md)** is a production-grade UI/UX design brief
meant to be fed to a "Claude design" → UI-code step; the generated UI returns later and is built
against these docs.

---

## Document index

| # | Document | Purpose |
|---|---|---|
| — | [`00-executive-overview.md`](00-executive-overview.md) | One-page positioning, core claim, what FASAL can/can't claim |
| 1 | [`01-product-requirements.md`](01-product-requirements.md) | PRD — personas, goals, scope, requirements, success metrics |
| 2 | [`02-system-architecture.md`](02-system-architecture.md) | Components, data flow, tech stack, proposed repo structure |
| 3 | [`03-data-architecture-governance.md`](03-data-architecture-governance.md) | Data schema, dataset strategy, responsible-AI & claims governance |
| 4 | [`04-ai-ml-modeling-plan.md`](04-ai-ml-modeling-plan.md) | Preprocessing, baseline→DL→fusion models, uncertainty, XAI, validation |
| 5 | [`05-field-ops-hardware-plan.md`](05-field-ops-hardware-plan.md) | UAV payload, flight/calibration SOP, sampling design, lab methods |
| 6 | [`06-risk-compliance.md`](06-risk-compliance.md) | Technical risks, India drone rules, FSSAI, claims governance |
| 7 | [`07-roadmap-task-breakdown.md`](07-roadmap-task-breakdown.md) | 12-month roadmap → workstreams, epics, tasks, milestones |
| 8 | [`08-indiaai-pitch.md`](08-indiaai-pitch.md) | Pitch narrative, IndiaAI alignment, the ask, one-pager, abstract |
| — | [`../design.md`](../design.md) | Production-grade UI/UX design brief (frontend handoff) |

## Reading paths

- **Investor / IndiaAI reviewer:** `00` → `08` → `01` → `06`.
- **Engineer / builder:** `02` → `03` → `04` → `07`.
- **Field / lab / ops partner:** `00` → `05` → `06` → `03`.
- **Designer (UI handoff):** `00` → `01` (personas + outputs) → `02` (stack) → `../design.md`.

---

## Canonical vocabulary (use verbatim across all docs)

**Output terms.** *Risk class* (low / medium / high) · *Risk score* (calibrated 0–1) ·
*Confidence* (high / uncertain / out-of-distribution) · *Reason codes* (interpretable drivers) ·
*Action recommendation* (clear / collect sample / close-range scan / send to lab).

**Status terms (never use certification language).** *Screened* · *Risk flagged* ·
*Targeted sample recommended* · *Lab confirmation required*.

**Personas (5).** Farmer / FPO · Exporter · Food-testing lab · State agriculture department ·
Research partner.

**Pilot crops (5).** Grapes · Chilli · Tomato · Okra · Tea.

**Lab reference truth.** QuEChERS extraction → GC-MS/MS and/or LC-MS/MS (per pesticide chemistry
and matrix).

---

## Source-section coverage trace

Every section of the source concept document maps to at least one doc here (no orphaned material).

| Source §  | Topic | Covered in |
|---|---|---|
| §1 Executive summary | Positioning, core claim | `00`, `01`, `08` |
| §2 Problem & IndiaAI fit | Supply-chain problem, mission fit | `01`, `08` |
| §3 Feasibility | Can / cannot claim | `00`, `01` |
| §4 Remote-sensing science | Optical model, calibration, preprocessing | `02`, `04` |
| §5 Residue science | Direct/indirect detection, MRL difficulty, SERS | `04`, `06` |
| §6 UAV payload & hardware | Sensors, flight height | `05`, `02` |
| §7 Flight/calibration/field protocol | SOP, calibration eq., sampling | `05` |
| §8 Data architecture & AI | Schema, model stages, outputs, XAI, drift | `03`, `02`, `04` |
| §9 Ground truth & validation | Lab method, study design, metrics | `04`, `01` |
| §10 Product workflow & dashboard | Personas, dashboard features | `01`, `../design.md` |
| §11 Pilot crops/pesticides/scale | Crops, pesticide strategy, dataset scale | `01`, `03`, `07` |
| §12 Risks/mitigations/compliance | Technical risk, drone rules, claims governance | `06`, `03` |
| §13 12-month roadmap | Milestones M1–M12 | `07` |
| §14 References | Citations | carried per-doc + `08` |

## Status

| Doc | Status |
|---|---|
| README | Draft v1 |
| 00 / 01 / 02 / 03 | Draft v1 |
| design.md | Draft v1 |
| 04 / 05 / 06 | Draft v1 |
| 07 / 08 | Draft v1 |

*All documents are drafts pending owner review. Diagrams from the source doc are referenced by
figure number and described in text; no rendered figures in this phase.*
