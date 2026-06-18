import { cn } from "@/lib/cn";
import { RISK_META, fmtScore } from "@/lib/risk";
import type { RiskClass } from "@/lib/types";

/** Risk pill: lightness-ordered color + distinct icon + label (+ hatch on HIGH) — colorblind-safe. */
export function RiskBadge({
  riskClass,
  score,
  size = "md",
}: {
  riskClass: RiskClass;
  score?: number;
  size?: "sm" | "md";
}) {
  const m = RISK_META[riskClass];
  return (
    <span
      className={cn(
        "relative inline-flex items-center gap-1.5 overflow-hidden rounded-full border font-medium",
        size === "sm" ? "px-2 py-0.5 text-xs" : "px-2.5 py-1 text-sm",
      )}
      style={{
        background: `color-mix(in oklch, ${m.color} 16%, transparent)`,
        color: m.ink,
        borderColor: `color-mix(in oklch, ${m.color} 40%, transparent)`,
      }}
    >
      {riskClass === "high" && <span aria-hidden className="risk-hatch absolute inset-0 opacity-60" />}
      <span aria-hidden className="relative" style={{ color: m.color }}>
        {m.icon}
      </span>
      <span className="relative">{m.label}</span>
      {score != null && <span className="relative tnum opacity-80">· {fmtScore(score)}</span>}
    </span>
  );
}
