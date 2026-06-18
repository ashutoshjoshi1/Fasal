# 06 — Risks, Mitigations & Compliance

*Source: concept doc §12 (risks, mitigations, compliance); supports §5.3 (MRL difficulty) and the
claims governance in [`03`](03-data-architecture-governance.md) §5. Compliance is written
**jurisdiction-agnostic** — FASAL is a global product, so specifics are resolved per operating region.*

## 1. Technical risk register

| Risk | Why it matters | Mitigation |
|---|---|---|
| **Weak direct residue signal** | Pesticide film may be too thin for drone detection | Risk mapping (not concentration) + metadata fusion + close-range scan + lab confirmation |
| **Model learns crop stress, not residue** | Disease/drought/fertilizer stress can mimic residue anomalies | Control plots, spray logs, lab labels, multi-factor experimental design ([`05`](05-field-ops-hardware-plan.md) §4) |
| **Illumination changes** | Clouds & sun angle distort spectra | Irradiance sensors, reference panels, controlled time windows, shadow masking |
| **Mixed pixels** | A drone pixel may include leaf, soil, fruit, stem, shadow | Fly lower in trials, segmentation, sample visible crop zones |
| **Poor generalization** | A model trained in one region may fail in another | Region-wise validation, domain adaptation, active learning ([`04`](04-ai-ml-modeling-plan.md) §8) |
| **False confidence** | Users may treat the heatmap as legal proof | UI labels outputs as screening; lab confirmation required for compliance decisions; confidence/OOD always shown |

These mitigations are reflected in the modeling plan ([`04`](04-ai-ml-modeling-plan.md)), the field
SOP ([`05`](05-field-ops-hardware-plan.md)), and the UI ([`../design.md`](../design.md)).

## 2. Drone-regulatory considerations (per jurisdiction)

Drone operations must comply with the **civil-aviation rules of each country/region** in which FASAL
flies. These differ, but share common structure:
- **Aircraft category & registration:** most regimes classify UAS (often by weight) and require
  registration and an operator/pilot competency above small thresholds.
- **Airspace classification:** controlled vs uncontrolled/unrestricted airspace, with zones around
  airports, sensitive sites, and populated areas requiring authorization.
- **Altitude limits:** many jurisdictions permit routine operations up to **~120 m / 400 ft AGL**
  where airspace is unrestricted; restricted/controlled airspace requires prior approval.
- **Pre-flight airspace check:** always verify the **current national/regional airspace map** (the
  civil-aviation authority's portal/app) before each flight — boundaries and restrictions change.

Operational implication: flight planning (altitude per local limit; see
[`05`](05-field-ops-hardware-plan.md) §1.3) and airspace verification are part of every flight SOP.
Maintain a per-region compliance checklist; do not hard-code one country's rules.

## 3. Food-safety & claims governance

FASAL is a screening/triage tool; claims discipline is mandatory (canonical rules in
[`03`](03-data-architecture-governance.md) §5, enforced in UI/API/reports):

- **Never** market the drone output as an **accredited-lab residue certificate** or imply equivalence
  to any official food-safety authority's result.
- Use lab-confirmed terminology only: **screened · risk flagged · targeted sample recommended ·
  lab confirmation required**.
- Keep full **chain-of-custody** for any sample sent to a lab.
- Persist **model version, sensor serial, calibration record, and flight conditions** for each prediction.
- Require **human review** for high-impact decisions: harvest holds, exporter rejection, regulatory escalation.

### Why MRL determination stays off-limits (recap)
Maximum Residue Limits are concentrations in the homogenized edible matrix established by validated
lab workflows; a drone sees the outer surface from a distance. FASAL therefore reports **risk**, not
**mg/kg** or **compliance**, and routes confirmation to the lab (full reasoning in
[`science.md`](science.md) §7, [`04`](04-ai-ml-modeling-plan.md) §1, and [`00`](00-executive-overview.md)).

## 4. Ethics, data & responsible-AI posture
- **Non-personal datasets**, anonymized aggregate views, role-based access ([`03`](03-data-architecture-governance.md) §5–6).
- **Out-of-distribution routing**: the system abstains and recommends sampling/lab when outside its
  experience, rather than over-claiming.
- An **ethics & data-governance plan** is a first-phase deliverable (M1–M2, [`07`](07-roadmap-task-breakdown.md)),
  adaptable to each jurisdiction's data-protection and food-safety requirements.

## 5. Compliance checklist (per deployment)
- [ ] Local civil-aviation rules reviewed; airspace verified on the applicable authority's map; permissions obtained if needed.
- [ ] Registered aircraft / qualified pilot as applicable in the jurisdiction.
- [ ] Calibration panels + irradiance + dark/white frames recorded.
- [ ] Chain-of-custody opened for every ground sample.
- [ ] Outputs labeled screening; lab-confirmation path attached to high-risk findings.
- [ ] Provenance (model/sensor/calibration/flight conditions) stored with predictions.
- [ ] Human review on file for any harvest-hold / rejection / escalation.
- [ ] Local food-safety authority's reference methods/MRLs identified for the confirmatory lab loop.
