"use client";

import { useState } from "react";

import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/primitives";

const STAGES = [
  "Ingest & validate (8 data objects)",
  "Calibrate → reflectance",
  "Preprocess (SG / derivative / SNV)",
  "QC masks + coverage",
  "Segment canopy / fruit",
  "Risk inference + confidence",
];

export default function UploadPage() {
  const [done, setDone] = useState(-1);
  const [running, setRunning] = useState(false);

  const run = () => {
    if (running) return;
    setRunning(true);
    setDone(-1);
    let i = 0;
    const tick = () => {
      setDone(i);
      i += 1;
      if (i < STAGES.length) setTimeout(tick, 500);
      else setRunning(false);
    };
    tick();
  };

  return (
    <div className="p-6">
      <header className="mb-4">
        <h1 className="text-xl font-semibold text-text-primary">Upload &amp; processing</h1>
        <p className="text-sm text-text-secondary">
          Ingest a flight + metadata, then watch the pipeline run. (Demo: simulated stages — the real
          pipeline lives in <span className="font-mono">fasal/pipeline</span>.)
        </p>
      </header>
      <div className="grid gap-4 md:grid-cols-2">
        <Card className="p-5">
          <p className="text-sm font-medium text-text-primary">New flight</p>
          <div className="mt-3 grid place-items-center rounded-card border border-dashed border-border-strong p-8 text-center text-sm text-text-muted">
            Drop a hyperspectral cube / Avantes scans + calibration frames
            <span className="mt-1 text-xs">flight · spray · weather metadata validated at the boundary</span>
          </div>
          <div className="mt-3">
            <Button variant="primary" onClick={run} disabled={running}>
              {running ? "Processing…" : "Run demo pipeline"}
            </Button>
          </div>
        </Card>

        <Card className="p-5">
          <p className="text-sm font-medium text-text-primary">Pipeline</p>
          <ol className="mt-3 flex flex-col gap-2.5">
            {STAGES.map((s, i) => {
              const state = i <= done ? "done" : i === done + 1 && running ? "active" : "todo";
              return (
                <li key={s} className="flex items-center gap-3 text-sm">
                  <span
                    className="grid h-6 w-6 shrink-0 place-items-center rounded-full border text-xs"
                    style={{
                      borderColor: state === "done" ? "var(--success)" : "var(--border-strong)",
                      background: state === "done" ? "color-mix(in oklch, var(--success) 18%, transparent)" : "transparent",
                      color: state === "done" ? "var(--success)" : "var(--text-muted)",
                    }}
                  >
                    {state === "done" ? "✓" : i + 1}
                  </span>
                  <span className={state === "todo" ? "text-text-muted" : "text-text-primary"}>{s}</span>
                  {state === "active" && (
                    <span className="ml-auto h-3 w-3 animate-spin rounded-full border-2 border-border border-t-brand" />
                  )}
                </li>
              );
            })}
          </ol>
          {done === STAGES.length - 1 && !running && (
            <p className="mt-3 rounded-input border border-border bg-surface-2 p-2 text-xs text-text-secondary">
              Reflectance + risk map ready — open the Field map to review zones.
            </p>
          )}
        </Card>
      </div>
    </div>
  );
}
