import type { SpectrumTrace } from "@/lib/types";

/** Reflectance vs wavelength (sample vs control), with the red-edge region shaded (science.md §3.3). */
export function SpectralChart({ trace, height = 170 }: { trace: SpectrumTrace; height?: number }) {
  const xs = trace.wavelengths;
  if (!xs.length) return null;
  const w = 560;
  const h = height;
  const pad = { l: 40, r: 10, t: 10, b: 24 };
  const xmin = xs[0];
  const xmax = xs[xs.length - 1];
  const all = [...trace.sample, ...trace.control];
  const ymin = Math.min(...all);
  const ymax = Math.max(...all);
  const X = (v: number) => pad.l + ((v - xmin) / (xmax - xmin)) * (w - pad.l - pad.r);
  const Y = (v: number) => h - pad.b - ((v - ymin) / (ymax - ymin || 1)) * (h - pad.t - pad.b);
  const path = (ys: number[]) => ys.map((y, i) => `${i ? "L" : "M"}${X(xs[i]).toFixed(1)},${Y(y).toFixed(1)}`).join(" ");
  const reLo = X(680);
  const reHi = X(750);

  return (
    <svg viewBox={`0 0 ${w} ${h}`} className="w-full" role="img" aria-label="Reflectance spectrum (sample vs control)">
      <rect
        x={reLo}
        y={pad.t}
        width={Math.max(0, reHi - reLo)}
        height={h - pad.t - pad.b}
        fill="color-mix(in oklch, var(--risk-medium) 12%, transparent)"
      />
      <line x1={pad.l} y1={h - pad.b} x2={w - pad.r} y2={h - pad.b} stroke="var(--border-strong)" />
      <path d={path(trace.control)} fill="none" stroke="var(--text-muted)" strokeWidth={1.25} strokeDasharray="4 3" />
      <path d={path(trace.sample)} fill="none" stroke="var(--brand)" strokeWidth={1.75} />
      <text x={pad.l} y={h - 6} fontSize="10" fill="var(--text-muted)" style={{ fontFamily: "var(--font-mono)" }}>
        {Math.round(xmin)} nm
      </text>
      <text x={w - pad.r} y={h - 6} fontSize="10" textAnchor="end" fill="var(--text-muted)" style={{ fontFamily: "var(--font-mono)" }}>
        {Math.round(xmax)} nm
      </text>
      <text x={reLo + 3} y={pad.t + 10} fontSize="9" fill="var(--text-muted)">
        red-edge
      </text>
    </svg>
  );
}
