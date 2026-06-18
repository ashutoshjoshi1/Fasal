"use client";

import { ACTION_META } from "@/lib/risk";
import type { Action } from "@/lib/types";

import { Button } from "./Button";

/** The single safety-first next step. Never implies compliance. */
export function ActionCard({ action, onRequestLab }: { action: Action; onRequestLab?: () => void }) {
  const m = ACTION_META[action];
  const urgent = action === "send_to_lab" || action === "collect_sample";
  return (
    <div className="rounded-card border border-border bg-surface-2 p-4">
      <p className="text-xs uppercase tracking-wide text-text-muted">Recommended action</p>
      <p className="mt-1 text-base font-semibold text-text-primary">{m.label}</p>
      <div className="mt-3 flex flex-wrap gap-2">
        <Button variant={urgent ? "primary" : "secondary"} onClick={onRequestLab}>
          {action === "send_to_lab" ? "Request lab confirmation" : "Add to sampling plan"}
        </Button>
        <Button variant="ghost">View flight</Button>
      </div>
      <p className="mt-2 text-xs text-text-muted">
        Screening only — confirm with a certified lab before any compliance decision.
      </p>
    </div>
  );
}
