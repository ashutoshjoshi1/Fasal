"use client";

import { Card } from "@/components/ui/primitives";
import { ErrorState, Loading } from "@/components/ui/states";
import { useRegional } from "@/lib/queries";

function Sparkline({ values }: { values: number[] }) {
  if (values.length < 2) return null;
  const w = 120;
  const h = 28;
  const max = Math.max(...values, 1);
  const min = Math.min(...values, 0);
  const x = (i: number) => (i / (values.length - 1)) * w;
  const y = (v: number) => h - ((v - min) / (max - min || 1)) * h;
  const d = values.map((v, i) => `${i ? "L" : "M"}${x(i).toFixed(1)},${y(v).toFixed(1)}`).join(" ");
  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full" preserveAspectRatio="none" style={{ height: 28 }}>
      <path d={d} fill="none" stroke="var(--brand)" strokeWidth={1.5} />
    </svg>
  );
}

export default function RegionalPage() {
  const { data, isLoading, isError } = useRegional();
  return (
    <div className="p-6">
      <header className="mb-4">
        <h1 className="text-xl font-semibold text-text-primary">Regional trends</h1>
        <p className="text-sm text-text-secondary">Aggregated, anonymized hotspots and trends across regions.</p>
      </header>
      {isLoading ? (
        <Loading />
      ) : isError ? (
        <ErrorState />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {(data ?? []).map((r, i) => (
            <Card key={i} className="p-4">
              <p className="text-sm font-semibold text-text-primary">{r.region}</p>
              <p className="font-mono text-xs capitalize text-text-muted">
                {r.crop} · {r.flights} flights
              </p>
              <p className="mt-3 text-2xl font-semibold tnum text-text-primary">{r.high_risk_pct.toFixed(1)}%</p>
              <p className="text-xs text-text-muted">high-risk zones</p>
              <div className="mt-2">
                <Sparkline values={r.trend} />
              </div>
            </Card>
          ))}
        </div>
      )}
      <p className="mt-4 text-xs text-text-muted">
        Aggregated &amp; anonymized — no farm-level identifiers. Screening only.
      </p>
    </div>
  );
}
