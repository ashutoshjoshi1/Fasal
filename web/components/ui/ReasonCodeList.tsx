import { REASON_LABELS } from "@/lib/risk";
import type { ReasonCode } from "@/lib/types";

/** Interpretable drivers behind a prediction (docs/03 §5.4). */
export function ReasonCodeList({ codes }: { codes: ReasonCode[] }) {
  if (!codes.length) return <p className="text-sm text-text-muted">No drivers reported.</p>;
  return (
    <ul className="flex flex-col gap-1.5">
      {codes.map((c, i) => (
        <li key={i} className="flex items-start gap-2 text-sm">
          <span aria-hidden className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-brand" />
          <span>
            <span className="font-medium text-text-primary">
              {REASON_LABELS[c.type] ?? c.type}
            </span>
            <span className="text-text-secondary"> — {c.detail}</span>
          </span>
        </li>
      ))}
    </ul>
  );
}
