"use client";

import { CoverageMeter } from "@/components/ui/CoverageMeter";
import { DataTable } from "@/components/ui/DataTable";
import { EmptyState, ErrorState, Loading } from "@/components/ui/states";
import { useFlights } from "@/lib/queries";
import { fmtDate } from "@/lib/risk";
import type { FlightRow } from "@/lib/types";

const CAL_TONE: Record<FlightRow["calibration"], string> = {
  ok: "var(--success)",
  degraded: "var(--warning)",
  failed: "var(--danger)",
};

export default function FlightsPage() {
  const { data, isLoading, isError } = useFlights();
  return (
    <div className="p-6">
      <header className="mb-4">
        <h1 className="text-xl font-semibold text-text-primary">Flights &amp; data quality</h1>
        <p className="text-sm text-text-secondary">
          Trust the inputs: calibration status, coverage quality, and capture conditions per flight.
        </p>
      </header>
      {isLoading ? (
        <Loading />
      ) : isError ? (
        <ErrorState />
      ) : !data?.length ? (
        <EmptyState title="No flights yet" />
      ) : (
        <DataTable<FlightRow>
          rows={data}
          getRowId={(r) => r.flight_id}
          columns={[
            {
              key: "flight",
              header: "Flight",
              sortValue: (r) => r.field_name,
              render: (r) => (
                <div>
                  <p className="font-mono text-xs text-text-muted">{r.flight_id}</p>
                  <p className="text-text-primary">{r.field_name}</p>
                </div>
              ),
            },
            { key: "captured", header: "Captured", sortValue: (r) => r.captured_at, render: (r) => fmtDate(r.captured_at) },
            {
              key: "cal",
              header: "Calibration",
              render: (r) => (
                <span className="inline-flex items-center gap-1.5 capitalize">
                  <span className="h-2 w-2 rounded-full" style={{ background: CAL_TONE[r.calibration] }} />
                  {r.calibration}
                </span>
              ),
            },
            {
              key: "coverage",
              header: "Coverage quality",
              sortValue: (r) => r.coverage_quality,
              render: (r) => (
                <div className="w-44">
                  <CoverageMeter value={r.coverage_quality} label="" />
                </div>
              ),
            },
            { key: "cond", header: "Conditions", render: (r) => <span className="text-text-secondary">{r.conditions}</span> },
          ]}
        />
      )}
    </div>
  );
}
