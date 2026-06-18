import { CONFIDENCE_META, MAP_CONF_COLORS, MAP_RISK_COLORS, RISK_META } from "@/lib/risk";

import type { LayerMode } from "./RiskMap";

export function MapLegend({ mode }: { mode: LayerMode }) {
  const items =
    mode === "risk"
      ? (["low", "medium", "high"] as const).map((k) => ({ color: MAP_RISK_COLORS[k], label: RISK_META[k].label }))
      : (["high", "uncertain", "ood"] as const).map((k) => ({ color: MAP_CONF_COLORS[k], label: CONFIDENCE_META[k].label }));
  return (
    <div className="rounded-card border border-border bg-surface-1 p-2.5 text-xs shadow-[var(--shadow-raised)]">
      <p className="mb-1.5 font-medium text-text-secondary">{mode === "risk" ? "Risk" : "Confidence"}</p>
      <ul className="flex flex-col gap-1">
        {items.map((it, i) => (
          <li key={i} className="flex items-center gap-2">
            <span className="h-3 w-3 rounded-sm" style={{ background: it.color }} />
            <span className="text-text-primary">{it.label}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
