import { CONFIDENCE_META } from "@/lib/risk";
import type { Confidence } from "@/lib/types";

/** Confidence chip — a separate visual channel from risk (violet/slate + icon). */
export function ConfidenceChip({ confidence }: { confidence: Confidence }) {
  const m = CONFIDENCE_META[confidence] ?? CONFIDENCE_META.uncertain;
  return (
    <span
      className="inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-sm font-medium"
      style={{
        background: `color-mix(in oklch, ${m.color} 12%, transparent)`,
        color: m.color,
        borderColor: `color-mix(in oklch, ${m.color} 36%, transparent)`,
        borderStyle: confidence === "high" ? "solid" : "dashed",
      }}
      title="Model reliability — not chemical proof"
    >
      <span aria-hidden className="font-mono">
        {m.icon}
      </span>
      {m.label}
    </span>
  );
}
