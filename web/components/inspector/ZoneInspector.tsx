"use client";

import { SpectralChart } from "@/components/charts/SpectralChart";
import { ActionCard } from "@/components/ui/ActionCard";
import { ConfidenceChip } from "@/components/ui/ConfidenceChip";
import { OODBanner } from "@/components/ui/OODBanner";
import { Card, Field } from "@/components/ui/primitives";
import { ProvenancePanel } from "@/components/ui/ProvenancePanel";
import { ReasonCodeList } from "@/components/ui/ReasonCodeList";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { EmptyState, ErrorState, Loading } from "@/components/ui/states";
import { useZone } from "@/lib/queries";

export function ZoneInspector({ zoneId, onClose }: { zoneId: string | null; onClose: () => void }) {
  const { data, isLoading, isError } = useZone(zoneId ?? undefined);

  if (!zoneId)
    return (
      <EmptyState
        title="Select a zone"
        hint="Tap a cell on the map to inspect its risk, drivers, and recommended action."
      />
    );
  if (isLoading) return <Loading label="Loading zone…" />;
  if (isError || !data) return <ErrorState />;

  const p = data.prediction;
  const m = data.metadata;

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-start justify-between">
        <div>
          <p className="font-mono text-xs text-text-muted">{data.zone_id}</p>
          <p className="text-sm text-text-secondary">
            {m.crop} · {m.variety}
          </p>
        </div>
        <button
          onClick={onClose}
          aria-label="Close inspector"
          className="rounded-input px-2 py-1 text-sm text-text-muted hover:bg-surface-2"
        >
          ✕
        </button>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        <RiskBadge riskClass={p.risk_class} score={p.risk_score} />
        <ConfidenceChip confidence={p.confidence} />
      </div>

      {p.confidence === "ood" && <OODBanner />}

      <ActionCard action={p.action} />

      <Card className="p-3">
        <p className="mb-1 text-xs uppercase tracking-wide text-text-muted">Spectral signature</p>
        <SpectralChart trace={data.spectrum} />
        <p className="mt-1 text-xs text-text-muted">Sample (solid) vs control (dashed); red-edge region shaded.</p>
      </Card>

      <Card className="p-3">
        <p className="mb-1 text-xs uppercase tracking-wide text-text-muted">Why this zone</p>
        <ReasonCodeList codes={p.reason_codes} />
      </Card>

      <Card className="p-3">
        <p className="mb-2 text-xs uppercase tracking-wide text-text-muted">Context</p>
        <Field label="Active ingredient">{m.active_ingredient}</Field>
        <Field label="Days since spray">{m.days_since_spray} d</Field>
        <Field label="Pre-harvest interval">{m.pre_harvest_interval_days} d</Field>
        <Field label="Temperature">{m.temperature_c.toFixed(1)} °C</Field>
        <Field label="Humidity">{m.humidity_pct.toFixed(0)} %</Field>
      </Card>

      <ProvenancePanel provenance={p.provenance} />
    </div>
  );
}
