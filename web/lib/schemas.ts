/**
 * Zod schemas mirroring the FASAL backend contract (fasal/shared + fasal/api).
 *
 * These are the single source of truth: TypeScript types are derived via `z.infer` and the API
 * client validates every response against them at runtime. Objects strip unknown keys by default,
 * so the backend can add fields without breaking the client.
 */

import { z } from "zod";

export const RiskClassSchema = z.enum(["low", "medium", "high"]);
export const ConfidenceSchema = z.enum(["high", "uncertain", "ood"]);
export const ActionSchema = z.enum(["clear", "collect_sample", "close_range_scan", "send_to_lab"]);
export const ReasonCodeTypeSchema = z.enum([
  "swir_anomaly",
  "water_band_anomaly",
  "red_edge_shift",
  "high_stress_patch",
  "spray_timing",
  "short_pre_harvest_interval",
  "prior_high_risk_pattern",
  "low_coverage",
  "ood_input",
]);

export const ReasonCodeSchema = z.object({
  type: ReasonCodeTypeSchema,
  detail: z.string(),
  weight: z.number(),
});

export const ProvenanceSchema = z.object({
  model_version: z.string(),
  sensor_id: z.string().nullable(),
  calibration_id: z.string().nullable(),
  flight_id: z.string().nullable(),
});

export const RiskPredictionSchema = z.object({
  zone_id: z.string(),
  risk_class: RiskClassSchema,
  risk_score: z.number(),
  confidence: ConfidenceSchema,
  action: ActionSchema,
  reason_codes: z.array(ReasonCodeSchema),
  provenance: ProvenanceSchema.nullable(),
});

export const GeoLocationSchema = z.object({ lat: z.number(), lon: z.number() });

export const FieldSummarySchema = z.object({
  id: z.string(),
  name: z.string(),
  crop: z.string(),
  location: GeoLocationSchema,
  area_ha: z.number(),
  risk_class: RiskClassSchema,
  risk_score: z.number(),
  confidence: ConfidenceSchema,
  coverage: z.number(),
  last_flight: z.string(),
});

export const FieldDetailSchema = FieldSummarySchema.extend({
  bbox: z.tuple([z.number(), z.number(), z.number(), z.number()]), // [west, south, east, north]
  prediction: RiskPredictionSchema,
  n_zones: z.number(),
});

export const FlightRowSchema = z.object({
  flight_id: z.string(),
  field_id: z.string(),
  field_name: z.string(),
  captured_at: z.string(),
  calibration: z.enum(["ok", "degraded", "failed"]),
  coverage_quality: z.number(),
  conditions: z.string(),
});

export const BatchRowSchema = z.object({
  lot_id: z.string(),
  field_id: z.string(),
  crop: z.string(),
  risk_class: RiskClassSchema,
  risk_score: z.number(),
  confidence: ConfidenceSchema,
  phi_days: z.number(),
});

export const SpectrumTraceSchema = z.object({
  wavelengths: z.array(z.number()),
  sample: z.array(z.number()),
  control: z.array(z.number()),
});

export const ZoneMetadataSchema = z.object({
  crop: z.string(),
  variety: z.string(),
  active_ingredient: z.string(),
  days_since_spray: z.number(),
  pre_harvest_interval_days: z.number(),
  temperature_c: z.number(),
  humidity_pct: z.number(),
});

export const ZoneDetailSchema = z.object({
  zone_id: z.string(),
  field_id: z.string(),
  prediction: RiskPredictionSchema,
  spectrum: SpectrumTraceSchema,
  metadata: ZoneMetadataSchema,
});

export const SampleRequestItemSchema = z.object({
  point_id: z.string(),
  lot_id: z.string(),
  target_risk: RiskClassSchema,
});

export const SampleRequestSchema = z.object({
  request_id: z.string(),
  lot_ids: z.array(z.string()),
  points: z.array(SampleRequestItemSchema),
  created_label: z.string(),
});

export const RegionalStatSchema = z.object({
  region: z.string(),
  crop: z.string(),
  high_risk_pct: z.number(),
  flights: z.number(),
  trend: z.array(z.number()),
});

export const LabelStatusSchema = z.enum(["lab-confirmed", "sample-queued", "screened"]);

export const DatasetSampleSchema = z.object({
  id: z.string(),
  field_id: z.string(),
  field_name: z.string(),
  crop: z.string(),
  captured_at: z.string(),
  sensor: z.string(),
  n_bands: z.number(),
  gsd_cm: z.number(),
  risk_class: RiskClassSchema,
  risk_score: z.number(),
  label_status: LabelStatusSchema,
  location: GeoLocationSchema,
});

export const DatasetSampleDetailSchema = DatasetSampleSchema.extend({
  spectrum: SpectrumTraceSchema,
});

export const CaptureImageKindSchema = z.enum(["rgb", "ndvi", "risk"]);

// GeoJSON risk-grid overlay (MapLibre fill layer source).
export const ZonePropertiesSchema = z.object({
  zone_id: z.string(),
  risk_score: z.number(),
  risk_class: RiskClassSchema,
  confidence: ConfidenceSchema,
});

export const ZoneFeatureSchema = z.object({
  type: z.literal("Feature"),
  geometry: z.object({
    type: z.literal("Polygon"),
    coordinates: z.array(z.array(z.array(z.number()))),
  }),
  properties: ZonePropertiesSchema,
});

export const ZoneFeatureCollectionSchema = z.object({
  type: z.literal("FeatureCollection"),
  features: z.array(ZoneFeatureSchema),
});

// --- Derived TypeScript types (single source of truth) ---

export type RiskClass = z.infer<typeof RiskClassSchema>;
export type Confidence = z.infer<typeof ConfidenceSchema>;
export type Action = z.infer<typeof ActionSchema>;
export type ReasonCodeType = z.infer<typeof ReasonCodeTypeSchema>;
export type ReasonCode = z.infer<typeof ReasonCodeSchema>;
export type Provenance = z.infer<typeof ProvenanceSchema>;
export type RiskPrediction = z.infer<typeof RiskPredictionSchema>;
export type GeoLocation = z.infer<typeof GeoLocationSchema>;
export type FieldSummary = z.infer<typeof FieldSummarySchema>;
export type FieldDetail = z.infer<typeof FieldDetailSchema>;
export type FlightRow = z.infer<typeof FlightRowSchema>;
export type BatchRow = z.infer<typeof BatchRowSchema>;
export type SpectrumTrace = z.infer<typeof SpectrumTraceSchema>;
export type ZoneMetadata = z.infer<typeof ZoneMetadataSchema>;
export type ZoneDetail = z.infer<typeof ZoneDetailSchema>;
export type SampleRequestItem = z.infer<typeof SampleRequestItemSchema>;
export type SampleRequest = z.infer<typeof SampleRequestSchema>;
export type RegionalStat = z.infer<typeof RegionalStatSchema>;
export type LabelStatus = z.infer<typeof LabelStatusSchema>;
export type DatasetSample = z.infer<typeof DatasetSampleSchema>;
export type DatasetSampleDetail = z.infer<typeof DatasetSampleDetailSchema>;
export type CaptureImageKind = z.infer<typeof CaptureImageKindSchema>;
export type ZoneProperties = z.infer<typeof ZonePropertiesSchema>;
export type ZoneFeature = z.infer<typeof ZoneFeatureSchema>;
export type ZoneFeatureCollection = z.infer<typeof ZoneFeatureCollectionSchema>;
