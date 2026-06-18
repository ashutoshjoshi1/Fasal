import { fmtPct } from "@/lib/risk";

/** How much of the zone/field was usable (QC). A key operational signal. */
export function CoverageMeter({ value, label = "Coverage quality" }: { value: number; label?: string }) {
  const pct = Math.round(value * 100);
  const tone = value >= 0.8 ? "var(--success)" : value >= 0.5 ? "var(--warning)" : "var(--danger)";
  return (
    <div>
      <div className="flex items-center justify-between text-xs">
        <span className="text-text-muted">{label}</span>
        <span className="tnum font-medium text-text-primary">{fmtPct(value)}</span>
      </div>
      <div className="mt-1 h-2 w-full overflow-hidden rounded-full bg-surface-sunken">
        <div className="h-full rounded-full transition-[width] duration-300" style={{ width: `${pct}%`, background: tone }} />
      </div>
    </div>
  );
}
