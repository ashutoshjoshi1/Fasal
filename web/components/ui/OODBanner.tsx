/** Shown when a prediction is out-of-distribution: the model is outside its training experience. */
export function OODBanner() {
  return (
    <div
      className="flex items-start gap-2 rounded-input border px-3 py-2 text-sm"
      style={{
        background: "color-mix(in oklch, var(--ood) 10%, transparent)",
        borderColor: "color-mix(in oklch, var(--ood) 35%, transparent)",
        color: "var(--text-secondary)",
      }}
      role="status"
    >
      <span aria-hidden className="font-mono" style={{ color: "var(--ood)" }}>
        ⚠
      </span>
      <span>
        <strong className="text-text-primary">Outside model experience.</strong> FASAL is not
        confident here — collect a targeted sample and confirm in the lab.
      </span>
    </div>
  );
}
