"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { ConfidenceChip } from "@/components/ui/ConfidenceChip";
import { DataTable } from "@/components/ui/DataTable";
import { Card } from "@/components/ui/primitives";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { ErrorState, Loading } from "@/components/ui/states";
import { useBatches, useLabQueue } from "@/lib/queries";
import type { BatchRow, SampleRequest } from "@/lib/types";

export default function BatchesPage() {
  const { data, isLoading, isError } = useBatches();
  const labQueue = useLabQueue();
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [request, setRequest] = useState<SampleRequest | null>(null);

  const toggle = (id: string) =>
    setSelected((s) => {
      const next = new Set(s);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });

  const generate = () =>
    labQueue.mutate([...selected], { onSuccess: (r) => setRequest(r) });

  return (
    <div className="flex h-full">
      <div className="min-w-0 flex-1 overflow-auto p-6">
        <header className="mb-4">
          <h1 className="text-xl font-semibold text-text-primary">Batch risk &amp; lab queue</h1>
          <p className="text-sm text-text-secondary">
            Rank lots by risk and queue the right ones for certified lab confirmation.
          </p>
        </header>
        {isLoading ? (
          <Loading />
        ) : isError ? (
          <ErrorState />
        ) : (
          <DataTable<BatchRow>
            rows={data ?? []}
            getRowId={(r) => r.lot_id}
            onRowClick={(r) => toggle(r.lot_id)}
            columns={[
              {
                key: "select",
                header: "",
                render: (r) => (
                  <input type="checkbox" readOnly checked={selected.has(r.lot_id)} aria-label={`Select ${r.lot_id}`} />
                ),
              },
              {
                key: "lot",
                header: "Lot",
                sortValue: (r) => r.lot_id,
                render: (r) => (
                  <div>
                    <p className="font-mono text-xs text-text-muted">{r.lot_id}</p>
                    <p className="capitalize text-text-primary">{r.crop}</p>
                  </div>
                ),
              },
              { key: "risk", header: "Risk", sortValue: (r) => r.risk_score, render: (r) => <RiskBadge riskClass={r.risk_class} score={r.risk_score} size="sm" /> },
              { key: "conf", header: "Confidence", render: (r) => <ConfidenceChip confidence={r.confidence} /> },
              { key: "phi", header: "PHI", align: "right", sortValue: (r) => r.phi_days, render: (r) => `${r.phi_days} d` },
            ]}
          />
        )}
      </div>

      <aside className="w-80 shrink-0 overflow-auto border-l border-border bg-surface-app p-4">
        <h2 className="text-sm font-semibold text-text-primary">Lab queue</h2>
        <p className="mt-0.5 text-xs text-text-muted">{selected.size} lot(s) selected for confirmation.</p>
        <div className="mt-3 flex flex-col gap-1.5">
          {[...selected].map((id) => (
            <div key={id} className="flex items-center justify-between rounded-input border border-border bg-surface-1 px-2.5 py-1.5 text-sm">
              <span className="font-mono text-xs">{id}</span>
              <button onClick={() => toggle(id)} className="text-text-muted hover:text-text-primary" aria-label={`Remove ${id}`}>
                ✕
              </button>
            </div>
          ))}
          {!selected.size && <p className="text-sm text-text-muted">Select lots from the table.</p>}
        </div>
        <div className="mt-3 flex gap-2">
          <Button variant="primary" disabled={!selected.size || labQueue.isPending} onClick={generate}>
            {labQueue.isPending ? "Generating…" : "Generate sample request"}
          </Button>
          <Button variant="ghost" onClick={() => { setSelected(new Set()); setRequest(null); }}>
            Clear
          </Button>
        </div>
        {request && (
          <Card className="mt-4 p-3">
            <p className="text-xs uppercase tracking-wide text-text-muted">Sample request</p>
            <p className="mt-1 font-mono text-sm text-text-primary">{request.request_id}</p>
            <p className="mt-1 text-sm text-text-secondary">
              {request.points.length} GPS-tagged sampling point(s) · chain-of-custody opened. Confirm with a
              certified lab (GC-MS/MS / LC-MS/MS).
            </p>
          </Card>
        )}
      </aside>
    </div>
  );
}
