"use client";

import { cn } from "@/lib/cn";

import type { LayerMode } from "./RiskMap";

const OPTS: { k: LayerMode; label: string }[] = [
  { k: "risk", label: "Risk" },
  { k: "confidence", label: "Confidence" },
];

export function LayerSwitcher({ mode, onChange }: { mode: LayerMode; onChange: (m: LayerMode) => void }) {
  return (
    <div className="flex rounded-full border border-border bg-surface-1 p-0.5 shadow-[var(--shadow-raised)]">
      {OPTS.map((o) => (
        <button
          key={o.k}
          onClick={() => onChange(o.k)}
          className={cn(
            "rounded-full px-3 py-1 text-xs font-medium transition-colors",
            mode === o.k ? "bg-brand text-text-on-brand" : "text-text-secondary hover:text-text-primary",
          )}
        >
          {o.label}
        </button>
      ))}
    </div>
  );
}
