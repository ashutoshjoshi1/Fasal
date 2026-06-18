# FASAL — UI/UX Design Brief

**Audience:** a design-to-code step ("Claude design") that will generate production-grade
React/Next.js UI from this brief. **Goal:** a distinctive, trustworthy, map-first interface — not a
template. The generated UI returns and is built against the planning docs in
[`docs/`](docs/README.md). Read [`docs/01-product-requirements.md`](docs/01-product-requirements.md)
(personas + output contract) and [`docs/02-system-architecture.md`](docs/02-system-architecture.md)
(Next.js + WebGL map stack) alongside this.

> **Product truth that the UI must embody (non-negotiable):** FASAL is **screening, not
> certification**. Every risk output is paired with **confidence**, optional **out-of-distribution
> (OOD)** flags, **reason codes**, and a path to **lab confirmation**. The UI never implies a
> certified residue result. Vocabulary is fixed: *screened · risk flagged · targeted sample
> recommended · lab confirmation required.*

---

## 1. Design principles

1. **Map-first.** The georeferenced field and its risk heatmap are the primary object on screen;
   everything else orbits it.
2. **Evidence-first / trust-first.** Risk is never shown alone — confidence, reason codes, coverage
   quality, and provenance are always one glance or one tap away.
3. **Make uncertainty visible.** Uncertain and OOD states are *designed*, prominent, and honest —
   never hidden to look more confident.
4. **Semantic color, not decoration.** Color carries meaning (risk, confidence, action). Decorative
   color is minimal and never competes with the semantic scales.
5. **Calm under density.** This is an operational console with a lot of data; hierarchy, rhythm, and
   restraint keep it legible in the field and the control room.
6. **Designed for gloves and sunlight.** Primary field surface is touch-first, high-contrast, with
   large targets; a true dark mode serves control rooms.

## 2. Visual direction — "Field Intelligence Console"

A **cartographic, data-precise, earth-grounded** aesthetic: the clarity and grid discipline of
Swiss/International data design, the materiality of agronomy (warm neutral surfaces, earth accents),
and the seriousness of an earth-observation mission console. Precise, quietly confident,
government-and-science credible — appropriate for a food-safety product that must read as
trustworthy to regulators and exporters worldwide.

- **Mood words:** precise · grounded · trustworthy · cartographic · calm-technical.
- **Light mode is primary** (sunlight legibility); **dark mode** is a first-class control-room theme.
- **Anti-template guardrails (do NOT ship):** uniform card grids with no hierarchy; stock centered
  hero + gradient blob; unmodified component-library defaults; flat layouts with no layering;
  identical radius/shadow/spacing everywhere; gray-on-white with one random accent; dashboard-by-
  numbers (sidebar + 4 stat cards + line chart) with no point of view.
- **Reference touchstones (for feel, not copy):** Mapbox/Felt cartographic UIs, earth-observation
  consoles (Sentinel Hub / Planet), precision-ag dashboards, scientific instrument readouts.

## 3. Design tokens

All color in **OKLCH**. Define once as CSS custom properties; never hardcode palette/spacing/type.

### 3.1 Neutrals & brand (light)
```css
:root {
  /* Surfaces — warm, paper-like neutrals (agronomic, not clinical gray) */
  --surface-app:     oklch(98.5% 0.004 95);   /* page background */
  --surface-1:       oklch(100%  0     0);     /* cards / panels */
  --surface-2:       oklch(96.6% 0.006 95);    /* raised / toolbars */
  --surface-sunken:  oklch(94.0% 0.006 95);    /* wells, map letterbox */
  --border:          oklch(90.5% 0.008 95);
  --border-strong:   oklch(83%   0.010 95);

  /* Text */
  --text-primary:    oklch(24%   0.02 262);
  --text-secondary:  oklch(46%   0.02 262);
  --text-muted:      oklch(60%   0.015 262);
  --text-on-brand:   oklch(99%   0     0);

  /* Brand — deep "remote-sensing" indigo. Chosen deliberately OUTSIDE the green-amber-red
     risk band and the teal data hues so it never collides with semantic meaning. */
  --brand:           oklch(52%  0.16 285);
  --brand-strong:    oklch(44%  0.17 285);
  --brand-tint:      oklch(95%  0.03 285);

  /* Accent — warm clay (human / agronomy warmth). Use sparingly. */
  --accent:          oklch(70%  0.12 60);
  --accent-tint:     oklch(95%  0.04 60);
}
```

### 3.2 Risk semantic scale (the most important system)
Risk is an **ordered** low→high scale. It MUST be readable without relying on hue (see §10):
encode risk with **lightness order + text label + distinct icon + a hatch fill on High**.
```css
:root {
  /* ordered by lightness: low (lightest) → high (darkest/most saturated) */
  --risk-low:        oklch(74% 0.13 155);   /* green   */
  --risk-low-ink:    oklch(40% 0.10 155);
  --risk-medium:     oklch(79% 0.15 78);    /* amber   */
  --risk-medium-ink: oklch(45% 0.12 70);
  --risk-high:       oklch(57% 0.21 25);    /* red     */
  --risk-high-ink:   oklch(40% 0.18 25);
  --risk-none:       oklch(88% 0.01 95);    /* unscanned / no-data */
}
```
- **Heatmap overlay** uses these as semi-transparent fills over the orthomosaic/basemap; High also
  carries a diagonal-hatch texture so it is unambiguous in grayscale and for color-vision deficiency.
- **Never** use the risk hues for non-risk UI (buttons, links, decoration).

### 3.3 Confidence & status (a separate visual channel from risk)
Confidence uses **violet/slate + texture + icon**, deliberately *not* the risk hues, so "uncertain"
is never mistaken for "medium risk".
```css
:root {
  --confidence-high:      oklch(55% 0.03 262);  /* neutral-strong + ✓ */
  --confidence-uncertain: oklch(62% 0.13 300);  /* violet + ~ (hatched chip) */
  --ood:                  oklch(52% 0.04 255);  /* slate + ⚠ (striped chip) */

  /* System semantics (non-risk UI only) */
  --info:    oklch(60% 0.12 240);
  --success: oklch(62% 0.13 150);
  --warning: oklch(75% 0.14 75);
  --danger:  oklch(58% 0.20 25);
}
```

### 3.4 Typography
Deliberate pairing — **IBM Plex Sans** (humanist-technical, open-source, government/science
credible) for UI and **IBM Plex Mono** for data/coordinates/spectra readouts. The IBM Plex family
covers many scripts (Latin, Cyrillic, Greek, Arabic, CJK, and more), so localized UI in multiple
languages/scripts is a first-class requirement for field users across regions.
```css
:root {
  --font-sans: "IBM Plex Sans", system-ui, sans-serif; /* add locale-specific Plex script families as needed */
  --font-mono: "IBM Plex Mono", ui-monospace, monospace;

  --text-display: clamp(2.2rem, 1.4rem + 3vw, 3.4rem);  /* big risk numbers / hero stats */
  --text-h1:      clamp(1.6rem, 1.2rem + 1.4vw, 2.1rem);
  --text-h2:      clamp(1.3rem, 1.1rem + 0.8vw, 1.6rem);
  --text-h3:      1.15rem;
  --text-body:    1rem;          /* 16px floor for field legibility */
  --text-sm:      0.875rem;
  --text-xs:      0.78rem;       /* labels, never for primary content */
  --leading-tight: 1.15;
  --leading-body:  1.55;
}
```
- **Numerals & coordinates** (risk score, GPS, wavelengths, doses) use mono + `font-variant-numeric:
  tabular-nums` for stable alignment.
- Hierarchy comes from **scale contrast** (big calibrated risk score vs. quiet metadata), not from
  many weights. Use 2–3 weights (400/500/600).

### 3.5 Spacing, radius, elevation, motion
```css
:root {
  /* 4px base rhythm */
  --space-1:.25rem; --space-2:.5rem; --space-3:.75rem; --space-4:1rem;
  --space-5:1.5rem; --space-6:2rem; --space-8:3rem; --space-section:clamp(2.5rem,2rem+3vw,5rem);

  /* Intentional, NON-uniform radii: cartographic/data panels are crisp, content is softer */
  --radius-map:   4px;    /* map panels, legend, data tables — precise */
  --radius-card:  12px;   /* content cards, drawers */
  --radius-pill:  999px;  /* chips, badges, status */
  --radius-input: 8px;

  /* Soft, layered elevation (floating map controls / drawers) */
  --shadow-1: 0 1px 2px oklch(24% 0.02 262 / .06), 0 1px 3px oklch(24% 0.02 262 / .08);
  --shadow-2: 0 4px 12px oklch(24% 0.02 262 / .10);
  --shadow-float: 0 8px 28px oklch(24% 0.02 262 / .16);

  --dur-fast:120ms; --dur-normal:240ms; --ease-out: cubic-bezier(.16,1,.3,1);
}
```

### 3.6 Dark theme (`[data-theme="dark"]`)
Invert surfaces to deep desaturated indigo-slate; keep risk hues but raise lightness/chroma for
contrast on dark; preserve the lightness *ordering* of the risk scale.
```css
[data-theme="dark"] {
  --surface-app: oklch(20% 0.02 262); --surface-1: oklch(24% 0.02 262);
  --surface-2:   oklch(27% 0.02 262); --surface-sunken: oklch(17% 0.02 262);
  --border: oklch(33% 0.02 262); --border-strong: oklch(42% 0.02 262);
  --text-primary: oklch(95% 0.01 95); --text-secondary: oklch(78% 0.015 95);
  --text-muted: oklch(64% 0.015 95); --brand-tint: oklch(30% 0.05 285);
  --risk-low: oklch(78% 0.14 155); --risk-medium: oklch(82% 0.16 80); --risk-high: oklch(64% 0.21 25);
}
```

## 4. Layout system & app shell

- **Three-zone shell:** (1) slim left **rail** (icon nav, role-aware), (2) top **context bar**
  (field/flight selector, date, search, theme, account, and a persistent quiet **screening-mode
  badge**), (3) main canvas. On the map view the main canvas is **map-dominant** with a floating
  **inspector drawer** on the right.
- **Bento composition** where it earns its place (e.g., the field overview combines a large map tile
  with smaller stat/coverage/lab-queue tiles of varying size) — avoid a uniform 4-card grid.
- **12-col fluid grid**, generous gutters; data tables and map panels align to a crisp 4px sub-grid.
- **Persistent disclaimer**, low-noise: a small "Screening — not a lab result" pill in the context
  bar that expands on hover/tap to the full statement and the "request lab confirmation" action.

## 5. Core screens

For each: purpose · layout · key components · data shown · states.

### 5.1 Field Risk Map (the hero)
- **Purpose:** see the field's low/med/high risk heatmap and act on it.
- **Layout:** full-bleed map canvas; floating layer switcher (top-left), legend (bottom-left),
  flight/time scrubber (bottom), inspector drawer (right, collapsible).
- **Components:** WebGL map (orthomosaic/basemap), **risk heatmap overlay**, **coverage-quality**
  overlay toggle, **confidence** overlay toggle, **sample-point markers**, **map legend**,
  layer switcher, flight scrubber, screening badge.
- **Data:** per-zone risk class/score + confidence; coverage quality; selected flight metadata;
  recommended sampling points.
- **States:** processing (cube still being computed → skeleton + progress), low-coverage warning
  band, partial-cloud mask shown, OOD regions visibly flagged, empty (no flight yet → guided CTA).

### 5.2 Zone Inspector (drawer / detail)
- **Purpose:** explain *why* a zone is risk-flagged and what to do.
- **Layout:** right drawer (desktop) / bottom sheet (tablet). Top: big **risk class + calibrated
  score** with **confidence chip**; below: **reason codes**, **spectral signature chart**,
  **wavelength-importance**, **comparison to controls**, **spray/weather/PHI metadata**, and a
  prominent **action card**.
- **Components:** RiskBadge, ConfidenceChip, OOD banner (if applicable), ReasonCodeList,
  SpectralChart, WavelengthImportanceChart, ProvenancePanel (model version, sensor, calibration,
  flight conditions), ActionCard (clear / collect sample / close-range scan / send to lab).
- **States:** uncertain/OOD → action card forces "targeted sample / lab confirmation" and tones
  down the score's visual weight; high-confidence-high-risk → strong but still screening-labeled.

### 5.3 Flights & Data Quality
- **Purpose:** trust the inputs. List flights with calibration status, coverage quality, mask
  coverage, weather-at-capture; drill into QC.
- **Components:** flights table (mono numerics), CalibrationStatus, CoverageQualityMeter, QC mask
  preview, re-process action.
- **States:** failed calibration (blocked, with reason), degraded coverage (warn), good (quiet).

### 5.4 Batch Risk & Lab Queue (Exporter)
- **Purpose:** rank batches by risk; queue the right lots for lab confirmation.
- **Components:** batch table sortable by risk/confidence/PHI, batch risk distribution, **Lab Queue**
  builder (select batches → generate sample request), export to lab.
- **States:** empty queue, queued-awaiting-lab, lab-results-returned (joins back to batch).

### 5.5 Sampling Plan & Chain of Custody (Lab)
- **Purpose:** receive a GPS-tagged sampling plan and a traceable custody record.
- **Components:** sample-plan map (low/med/high points), sample list with GPS + mass + type,
  ChainOfCustody timeline, downloadable manifest, result-entry/upload.
- **States:** plan draft → dispatched → in-transit → received → results-in.

### 5.6 Regional Trends (Agriculture / regulatory agency — anonymized)
- **Purpose:** monitor spray practice & risk hotspots across regions/administrative areas.
- **Components:** choropleth/hotspot map (aggregated, **anonymized**), trend lines by crop/season,
  spray-practice indicators. No farm-level identifiers.
- **States:** insufficient-data areas shown as no-data, not zero-risk.

### 5.7 Dataset & Labeling (Research partner)
- **Purpose:** governed access to calibrated spectra + metadata + lab labels.
- **Components:** dataset cards (coverage, licensing, known gaps, calibration provenance), version
  selector (DVC tags), spectra browser, label join viewer, export under access policy.

### 5.8 Upload / Processing Status
- **Purpose:** ingest a flight + metadata; watch the pipeline run.
- **Components:** schema-validated upload (flight, cube, RGB, irradiance, calibration frames,
  crop/spray/weather metadata), **pipeline stepper** (ingest → calibrate → preprocess → QC →
  segment → infer), per-stage logs/provenance.
- **States:** validation errors at boundary (clear, field-level), stage failure (retry), success.

### 5.9 Auth & role onboarding
- Role-based sign-in for the five personas; first-run picks the persona surface and default field;
  governed/anonymized scopes per [`docs/03-data-architecture-governance.md`](docs/03-data-architecture-governance.md).

## 6. Component library (design once, reuse)

- **RiskBadge** — class + score; lightness-ordered color **+ icon + text label** (+ hatch on High).
- **ConfidenceChip** — high (solid ✓) / uncertain (violet, hatched, ~) / OOD (slate, striped, ⚠).
- **OODBanner** — explains the model is outside training experience; routes to sampling/lab.
- **ReasonCodeList** — ranked interpretable drivers (e.g., "SWIR anomaly", "spray 2 d ago",
  "high-stress patch", "matches prior high-risk").
- **ActionCard** — the single clear next step; visually dominant; never says "compliant/non-compliant".
- **CoverageQualityMeter** — how much of the zone was usable (masking, cloud, blur).
- **ProvenancePanel** — model version, sensor serial, calibration record, flight conditions, timestamp.
- **ScreeningDisclaimer** — persistent pill → expandable statement + "request lab confirmation".
- **MapLegend / LayerSwitcher / FlightScrubber / SamplePointMarker.**
- **DataTable** — mono tabular numerics, sortable, density toggle, sticky header.
- **Filters** — crop, pesticide family, date/flight, risk, confidence (URL-persisted state).
- **Charts** — SpectralChart, WavelengthImportanceChart, RiskDistribution, ConfusionMatrix (research/validation),
  CalibrationDriftChart.
- **Feedback** — Toast, EmptyState, ErrorState, Skeleton, ProgressStepper.

## 7. Data visualization guidelines

Treat charts as part of the design system, not an afterthought.
- **Spectral signature chart:** x = wavelength (nm), y = reflectance; lightly shade **VNIR
  (400–1000 nm)** and **SWIR (1000–2500 nm)** regions; overlay the zone's spectrum vs. a control;
  mono axis labels, tabular numerics.
- **Wavelength-importance:** horizontal bars over the same wavelength axis so users can map
  importance to spectral regions.
- **Spatial attention:** optional heat overlay on the zone thumbnail showing where the model "looked".
- **Sequential data scales** (for spectra/attention heat) use a **perceptually-uniform** ramp
  (viridis-like) — distinct from the categorical risk triad.
- **Categorical palette** (crops/pesticide families) is a separate 6-color set that avoids the risk
  hues and is CVD-checked.
- **Never** use a rainbow scale for quantitative data; never red↔green as the only quantitative cue.

## 8. States, feedback & motion

- **Every data surface defines five states:** loading (skeleton), empty (guided CTA), partial/low-
  coverage (honest warning), error (recoverable), OOD/uncertain (routes to lab). Design all five.
- **Motion:** purposeful and compositor-friendly — animate `transform`/`opacity`/`clip-path` only;
  durations `--dur-fast`/`--dur-normal`, `--ease-out`. Map transitions and drawer slides are the
  main motions; data does not bounce. Respect `prefers-reduced-motion` (disable non-essential motion).
- **Hover/focus/active/selected** are explicitly designed for every interactive element (visible
  focus ring meeting contrast; selected map zone has a distinct outline + elevation).

## 9. Responsive behavior

- **Breakpoints:** 360 · 768 · 1024 · 1440 · 1920. Test all; no horizontal overflow.
- **Primary touch target is a field tablet** (≈768–1024, often outdoors): large hit areas (≥44px,
  prefer 48px for gloved use), bottom-sheet inspector, high-contrast field mode.
- **Desktop/control-room (≥1440):** map + persistent right inspector + denser tables.
- **Small phones (360–430):** map-first with a peekable bottom sheet; tables collapse to cards.
- The map is always the anchor; panels reflow around it rather than pushing it off-screen.

## 10. Accessibility (must-pass)

- **WCAG 2.2 AA**: text contrast ≥ 4.5:1 (≥ 3:1 large); UI/graphic objects ≥ 3:1.
- **Color-vision safety (critical):** risk is **never hue-only** — always label + icon + lightness
  order, with a **hatch texture on High**. Validate the risk + categorical palettes against
  deuteranopia/protanopia/tritanopia simulations.
- **Keyboard:** full operability, logical order, visible focus, skip links; map has keyboard pan/zoom
  and a list-based fallback for zones.
- **Reduced motion:** honor `prefers-reduced-motion`.
- **Sunlight / field mode:** an optional high-contrast theme toggle for outdoor legibility.
- **Multilingual / localization:** layout tolerates long localized strings and non-Latin scripts; never bake text into images.
- **Semantic HTML & ARIA:** landmarks (`header`/`nav`/`main`), labeled controls, live regions for
  pipeline progress and toasts.

## 11. Microcopy & content rules

- Use the fixed vocabulary: **screened · risk flagged · targeted sample recommended · lab
  confirmation required**. Never "safe", "certified", "compliant", "passed", "mg/kg", or "MRL met".
- Example zone summary: *"High risk flagged · score 0.86 · confidence: high. Drivers: SWIR anomaly,
  spray 2 days ago, high-stress patch. Recommended: collect targeted sample → lab confirmation."*
- Example OOD: *"Outside model experience (new variety). FASAL is not confident here — collect a
  sample and confirm in the lab."*
- Plain language for farmers/grower cooperatives; precise/technical for labs and researchers (persona-aware tone).

## 12. Deliverables expected from the design step

1. A **design-token file** (CSS custom properties / Tailwind theme) implementing §3, light + dark.
2. **Component library** (§6) as React/Next.js components with all states (§8) and a11y (§10).
3. The **core screens** (§5), responsive across §9 breakpoints, with realistic placeholder data
   matching the **output contract** in [`docs/01-product-requirements.md`](docs/01-product-requirements.md).
4. The **risk color system + chart components** (§7) as reusable primitives.
5. Light + dark + field-high-contrast themes; reduced-motion support.

## 13. Out of scope / respect-the-docs

- No real data, backend, or model integration in the design step — placeholder data only, shaped to
  the output contract.
- Do not invent claims or metrics; the screening-not-certification framing and the five personas are
  fixed by the planning docs.
- Map basemap, auth, and API wiring are integrated later when we build against
  [`docs/02-system-architecture.md`](docs/02-system-architecture.md).
