/** Risk/confidence/action presentation metadata + formatters.
 *  Risk is encoded by lightness-ordered color + a distinct icon + a text label
 *  (+ a hatch on HIGH) so it is never hue-only — colorblind-safe (design.md §10). */

import type { Action, Confidence, ReasonCodeType, RiskClass } from "./types";

export const RISK_META: Record<
  RiskClass,
  { label: string; short: string; icon: string; color: string; ink: string }
> = {
  low: { label: "Low risk", short: "Low", icon: "●", color: "var(--risk-low)", ink: "var(--risk-low-ink)" },
  medium: { label: "Medium risk", short: "Medium", icon: "◆", color: "var(--risk-medium)", ink: "var(--risk-medium-ink)" },
  high: { label: "High risk", short: "High", icon: "▲", color: "var(--risk-high)", ink: "var(--risk-high-ink)" },
};

export const CONFIDENCE_META: Record<Confidence, { label: string; icon: string; color: string }> = {
  high: { label: "High confidence", icon: "✓", color: "var(--confidence-high)" },
  uncertain: { label: "Uncertain", icon: "~", color: "var(--confidence-uncertain)" },
  ood: { label: "Out-of-distribution", icon: "⚠", color: "var(--ood)" },
};

export const ACTION_META: Record<Action, { label: string; short: string }> = {
  clear: { label: "Clear for normal monitoring", short: "Clear" },
  collect_sample: { label: "Collect a targeted sample", short: "Collect sample" },
  close_range_scan: { label: "Close-range scan", short: "Close-range scan" },
  send_to_lab: { label: "Send to lab for confirmation", short: "Send to lab" },
};

export const REASON_LABELS: Record<ReasonCodeType, string> = {
  swir_anomaly: "SWIR anomaly",
  water_band_anomaly: "Water-band anomaly",
  red_edge_shift: "Red-edge shift",
  high_stress_patch: "High-stress patch",
  spray_timing: "Recent spray",
  short_pre_harvest_interval: "Short pre-harvest interval",
  prior_high_risk_pattern: "Matches prior high-risk pattern",
  low_coverage: "Low coverage",
  ood_input: "Outside model experience",
};

// Concrete hex colors for the WebGL map fill (MapLibre can't read CSS oklch vars).
export const MAP_RISK_COLORS: Record<RiskClass, string> = {
  low: "#5cbf8b",
  medium: "#e3ab3e",
  high: "#d04a36",
};
export const MAP_CONF_COLORS: Record<Confidence, string> = {
  high: "#7c8aa0",
  uncertain: "#9b6bd6",
  ood: "#5b6472",
};
export const MAP_NO_DATA = "#cfc9bf";

export const fmtPct = (x: number, digits = 0) => `${(x * 100).toFixed(digits)}%`;
export const fmtScore = (x: number) => x.toFixed(2);
export const fmtDate = (iso: string) =>
  new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
export const fmtCoord = (lat: number, lon: number) =>
  `${Math.abs(lat).toFixed(2)}°${lat >= 0 ? "N" : "S"} ${Math.abs(lon).toFixed(2)}°${lon >= 0 ? "E" : "W"}`;
