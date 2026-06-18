"use client";

import { useMemo, useState } from "react";

import { DatasetModal } from "@/components/dataset/DatasetModal";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { EmptyState, ErrorState, Loading } from "@/components/ui/states";
import { datasetImageUrl } from "@/lib/api";
import { cn } from "@/lib/cn";
import { useDataset } from "@/lib/queries";
import { fmtDate } from "@/lib/risk";
import type { LabelStatus, RiskClass } from "@/lib/types";

const LABEL_TONE: Record<LabelStatus, string> = {
  "lab-confirmed": "var(--success)",
  "sample-queued": "var(--warning)",
  screened: "var(--text-muted)",
};

const RISK_FILTERS: ("all" | RiskClass)[] = ["all", "low", "medium", "high"];

export default function DatasetPage() {
  const { data, isLoading, isError } = useDataset();
  const [risk, setRisk] = useState<"all" | RiskClass>("all");
  const [crop, setCrop] = useState("all");
  const [selected, setSelected] = useState<string | null>(null);

  const crops = useMemo(() => ["all", ...Array.from(new Set((data ?? []).map((s) => s.crop)))], [data]);
  const filtered = (data ?? []).filter(
    (s) => (risk === "all" || s.risk_class === risk) && (crop === "all" || s.crop === crop),
  );

  return (
    <div className="p-6">
      <header className="mb-4">
        <h1 className="text-xl font-semibold text-text-primary">Drone capture dataset</h1>
        <p className="text-sm text-text-secondary">
          Imaging samples collected by drone — RGB composite, NDVI, and the risk raster per capture.
        </p>
      </header>

      <div className="mb-4 flex flex-wrap items-center gap-3">
        <div className="flex rounded-full border border-border bg-surface-1 p-0.5">
          {RISK_FILTERS.map((r) => (
            <button
              key={r}
              onClick={() => setRisk(r)}
              className={cn(
                "rounded-full px-3 py-1 text-xs font-medium capitalize",
                risk === r ? "bg-brand text-text-on-brand" : "text-text-secondary hover:text-text-primary",
              )}
            >
              {r}
            </button>
          ))}
        </div>
        <select
          value={crop}
          onChange={(e) => setCrop(e.target.value)}
          className="rounded-input border border-border-strong bg-surface-1 px-3 py-1.5 text-sm capitalize"
          aria-label="Filter by crop"
        >
          {crops.map((c) => (
            <option key={c} value={c}>
              {c === "all" ? "All crops" : c}
            </option>
          ))}
        </select>
        <span className="text-xs text-text-muted">{filtered.length} capture(s)</span>
      </div>

      {isLoading ? (
        <Loading />
      ) : isError ? (
        <ErrorState />
      ) : !filtered.length ? (
        <EmptyState title="No captures match" hint="Adjust the risk or crop filter." />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
          {filtered.map((s) => (
            <button
              key={s.id}
              onClick={() => setSelected(s.id)}
              className="group overflow-hidden rounded-card border border-border bg-surface-1 text-left shadow-[var(--shadow-soft)] transition-shadow hover:shadow-[var(--shadow-raised)]"
            >
              <div className="relative">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={datasetImageUrl(s.id, "rgb")}
                  alt={`Drone capture of ${s.field_name}`}
                  width={300}
                  height={300}
                  className="aspect-square w-full object-cover transition-transform duration-200 group-hover:scale-[1.02]"
                />
                <div className="absolute left-2 top-2">
                  <RiskBadge riskClass={s.risk_class} score={s.risk_score} size="sm" />
                </div>
                <span
                  className="absolute right-2 top-2 rounded-full px-2 py-0.5 text-[10px] font-medium"
                  style={{
                    background: `color-mix(in oklch, ${LABEL_TONE[s.label_status]} 22%, var(--surface-1))`,
                    color: LABEL_TONE[s.label_status],
                  }}
                >
                  {s.label_status}
                </span>
              </div>
              <div className="p-3">
                <p className="truncate text-sm font-medium text-text-primary">{s.field_name}</p>
                <p className="font-mono text-xs capitalize text-text-muted">
                  {s.crop} · {fmtDate(s.captured_at)}
                </p>
                <p className="mt-0.5 text-xs text-text-muted">
                  {s.sensor} · {s.n_bands} bands · {s.gsd_cm} cm
                </p>
              </div>
            </button>
          ))}
        </div>
      )}

      {selected && <DatasetModal sampleId={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
