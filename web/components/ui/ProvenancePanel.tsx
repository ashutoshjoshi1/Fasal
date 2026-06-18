import type { Provenance } from "@/lib/types";

import { Field } from "./primitives";

/** Per-prediction provenance for auditability (docs/06 §3). */
export function ProvenancePanel({ provenance }: { provenance: Provenance | null }) {
  if (!provenance) return null;
  return (
    <div className="rounded-card border border-border bg-surface-1 p-3">
      <p className="mb-1 text-xs uppercase tracking-wide text-text-muted">Provenance</p>
      <Field label="Model">{provenance.model_version}</Field>
      {provenance.sensor_id && <Field label="Sensor">{provenance.sensor_id}</Field>}
      {provenance.flight_id && <Field label="Flight">{provenance.flight_id}</Field>}
      {provenance.calibration_id && <Field label="Calibration">{provenance.calibration_id}</Field>}
    </div>
  );
}
