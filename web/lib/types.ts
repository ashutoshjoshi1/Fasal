/**
 * TypeScript mirror of the FASAL backend contract.
 *
 * Types are derived from the Zod schemas in ./schemas (the single source of truth) and re-exported
 * here so existing imports (`@/lib/types`) keep working. Add or change shapes in ./schemas.
 */

export type {
  RiskClass,
  Confidence,
  Action,
  ReasonCodeType,
  ReasonCode,
  Provenance,
  RiskPrediction,
  GeoLocation,
  FieldSummary,
  FieldDetail,
  FlightRow,
  BatchRow,
  SpectrumTrace,
  ZoneMetadata,
  ZoneDetail,
  SampleRequestItem,
  SampleRequest,
  RegionalStat,
  LabelStatus,
  DatasetSample,
  DatasetSampleDetail,
  CaptureImageKind,
  ZoneProperties,
  ZoneFeature,
  ZoneFeatureCollection,
} from "./schemas";
