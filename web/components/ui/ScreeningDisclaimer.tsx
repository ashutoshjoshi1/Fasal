"use client";

import { useEffect, useRef, useState } from "react";

import { Button } from "./Button";

/** Persistent, low-noise "screening, not certification" pill that expands to the full statement. */
export function ScreeningDisclaimer() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    const onClickOutside = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener("keydown", onKeyDown);
    document.addEventListener("mousedown", onClickOutside);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.removeEventListener("mousedown", onClickOutside);
    };
  }, [open]);

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
        aria-controls="screening-disclaimer"
        className="inline-flex items-center gap-1.5 rounded-full border border-border bg-surface-2 px-3 py-1 text-xs font-medium text-text-secondary hover:bg-surface-1"
      >
        <span aria-hidden className="h-1.5 w-1.5 rounded-full" style={{ background: "var(--warning)" }} />
        Screening — not a lab result
      </button>
      {open && (
        <div
          id="screening-disclaimer"
          role="dialog"
          aria-label="Screening disclaimer"
          className="absolute right-0 z-50 mt-2 w-80 rounded-card border border-border bg-surface-1 p-3 text-sm shadow-[var(--shadow-float)]"
        >
          <p className="text-text-secondary">
            FASAL identifies <strong className="text-text-primary">spatial risk patterns</strong>; it
            does not certify pesticide concentrations or MRL compliance. Confirm high-risk findings
            with a certified lab (GC-MS/MS / LC-MS/MS) before any compliance decision.
          </p>
          <div className="mt-3">
            <Button variant="primary" className="w-full">
              Request lab confirmation
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
