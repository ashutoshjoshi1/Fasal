/** TypeScript mirror of the FASAL backend contract (fasal/shared + fasal/api/demo_data). */

export type RiskClass = "low" | "medium" | "high";
export type Confidence = "high" | "uncertain" | "ood";
export type Action = "clear" | "collect_sample" | "close_range_scan" | "send_to_lab";
export type ReasonCodeType =
  | "swir_anomaly"
  | "water_band_anomaly"
  | "red_edge_shift"
  | "high_stress_patch"
  | "spray_timing"
  | "short_pre_harvest_interval"
  | "prior_high_risk_pattern"
  | "low_coverage"
  | "ood_input";

export interface ReasonCode {
  type: ReasonCodeType;
  detail: string;
  weight: number;
}

export interface Provenance {
  model_version: string;
  sensor_id: string | null;
  calibration_id: string | null;
  flight_id: string | null;
}

export interface RiskPrediction {
  zone_id: string;
  risk_class: RiskClass;
  risk_score: number;
  confidence: Confidence;
  action: Action;
  reason_codes: ReasonCode[];
  provenance: Provenance | null;
}

export interface GeoLocation {
  lat: number;
  lon: number;
}

export interface FieldSummary {
  id: string;
  name: string;
  crop: string;
  location: GeoLocation;
  area_ha: number;
  risk_class: RiskClass;
  risk_score: number;
  confidence: Confidence;
  coverage: number;
  last_flight: string;
}

export interface FieldDetail extends FieldSummary {
  bbox: [number, number, number, number]; // [west, south, east, north]
  prediction: RiskPrediction;
  n_zones: number;
}

export interface FlightRow {
  flight_id: string;
  field_id: string;
  field_name: string;
  captured_at: string;
  calibration: "ok" | "degraded" | "failed";
  coverage_quality: number;
  conditions: string;
}

export interface BatchRow {
  lot_id: string;
  field_id: string;
  crop: string;
  risk_class: RiskClass;
  risk_score: number;
  confidence: Confidence;
  phi_days: number;
}

export interface SpectrumTrace {
  wavelengths: number[];
  sample: number[];
  control: number[];
}

export interface ZoneMetadata {
  crop: string;
  variety: string;
  active_ingredient: string;
  days_since_spray: number;
  pre_harvest_interval_days: number;
  temperature_c: number;
  humidity_pct: number;
}

export interface ZoneDetail {
  zone_id: string;
  field_id: string;
  prediction: RiskPrediction;
  spectrum: SpectrumTrace;
  metadata: ZoneMetadata;
}

export interface SampleRequestItem {
  point_id: string;
  lot_id: string;
  target_risk: RiskClass;
}

export interface SampleRequest {
  request_id: string;
  lot_ids: string[];
  points: SampleRequestItem[];
  created_label: string;
}

export interface RegionalStat {
  region: string;
  crop: string;
  high_risk_pct: number;
  flights: number;
  trend: number[];
}

export type LabelStatus = "lab-confirmed" | "sample-queued" | "screened";

export interface DatasetSample {
  id: string;
  field_id: string;
  field_name: string;
  crop: string;
  captured_at: string;
  sensor: string;
  n_bands: number;
  gsd_cm: number;
  risk_class: RiskClass;
  risk_score: number;
  label_status: LabelStatus;
  location: GeoLocation;
}

export interface DatasetSampleDetail extends DatasetSample {
  spectrum: SpectrumTrace;
}

export type CaptureImageKind = "rgb" | "ndvi" | "risk";

// GeoJSON risk-grid overlay
export interface ZoneProperties {
  zone_id: string;
  risk_score: number;
  risk_class: RiskClass;
  confidence: Confidence;
}
export interface ZoneFeature {
  type: "Feature";
  geometry: { type: "Polygon"; coordinates: number[][][] };
  properties: ZoneProperties;
}
export interface ZoneFeatureCollection {
  type: "FeatureCollection";
  features: ZoneFeature[];
}
