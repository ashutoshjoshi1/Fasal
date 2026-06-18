"use client";

import { useEffect, useRef, useState } from "react";

import { SpectralChart } from "@/components/charts/SpectralChart";
import { Button } from "@/components/ui/Button";
import { Card, Field } from "@/components/ui/primitives";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { ErrorState, Loading } from "@/components/ui/states";
import { datasetImageUrl } from "@/lib/api";
import { cn } from "@/lib/cn";
import { useDatasetSample } from "@/lib/queries";
import { fmtDate } from "@/lib/risk";
import type { CaptureImageKind } from "@/lib/types";

const KINDS: { k: CaptureImageKind; label: string; note: string }[] = [
  { k: "rgb", label: "RGB", note: "RGB composite" },
  { k: "ndvi", label: "NDVI", note: "NDVI — vegetation vigor" },
  { k: "risk", label: "Risk", note: "Risk raster (screening)" },
];

export function DatasetModal({ sampleId, onClose }: { sampleId: string; onClose: () => void }) {
  const { data, isLoading, isError } = useDatasetSample(sampleId);
  const [kind, setKind] = useState<CaptureImageKind>("rgb");
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const previouslyFocused = document.activeElement as HTMLElement | null;
    dialogRef.current?.focus();
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") {
        onClose();
        return;
      }
      if (e.key === "Tab" && dialogRef.current) {
        const focusable = dialogRef.current.querySelectorAll<HTMLElement>(
          'a[href],button:not([disabled]),input,select,textarea,[tabindex]:not([tabindex="-1"])',
        );
        if (focusable.length) {
          const first = focusable[0];
          const last = focusable[focusable.length - 1];
          if (e.shiftKey && document.activeElement === first) {
            e.preventDefault();
            last.focus();
          } else if (!e.shiftKey && document.activeElement === last) {
            e.preventDefault();
            first.focus();
          }
        }
      }
    };
    document.addEventListener("keydown", onKeyDown);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      previouslyFocused?.focus?.();
    };
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 grid place-items-center bg-black/40 p-4" onClick={onClose}>
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby="dataset-modal-title"
        tabIndex={-1}
        className="max-h-[90vh] w-full max-w-3xl overflow-auto rounded-card border border-border bg-surface-1 shadow-[var(--shadow-float)]"
        onClick={(e) => e.stopPropagation()}
      >
        {isLoading ? (
          <Loading label="Loading capture…" />
        ) : isError || !data ? (
          <div className="p-4">
            <ErrorState />
          </div>
        ) : (
          <div className="flex flex-col gap-4 p-5">
            <div className="flex items-start justify-between">
              <div>
                <p className="font-mono text-xs text-text-muted">{data.id}</p>
                <h2 id="dataset-modal-title" className="text-lg font-semibold text-text-primary">
                  {data.field_name}
                </h2>
                <p className="text-sm capitalize text-text-secondary">
                  {data.crop} · {fmtDate(data.captured_at)}
                </p>
              </div>
              <button onClick={onClose} aria-label="Close" className="rounded-input px-2 py-1 text-text-muted hover:bg-surface-2">
                ✕
              </button>
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <div>
                <div className="mb-2 flex w-max rounded-full border border-border bg-surface-2 p-0.5">
                  {KINDS.map((o) => (
                    <button
                      key={o.k}
                      onClick={() => setKind(o.k)}
                      className={cn(
                        "rounded-full px-3 py-1 text-xs font-medium",
                        kind === o.k ? "bg-brand text-text-on-brand" : "text-text-secondary hover:text-text-primary",
                      )}
                    >
                      {o.label}
                    </button>
                  ))}
                </div>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src={datasetImageUrl(data.id, kind)}
                  alt={`${kind} capture of ${data.field_name}`}
                  width={360}
                  height={360}
                  className="aspect-square w-full rounded-card border border-border object-cover"
                />
                <p className="mt-1 text-xs text-text-muted">
                  {KINDS.find((o) => o.k === kind)?.note} · {data.sensor}
                </p>
              </div>

              <div className="flex flex-col gap-3">
                <div>
                  <RiskBadge riskClass={data.risk_class} score={data.risk_score} />
                </div>
                <Card className="p-3">
                  <Field label="Sensor">{data.sensor}</Field>
                  <Field label="Bands">{data.n_bands}</Field>
                  <Field label="Ground sample distance">{data.gsd_cm} cm</Field>
                  <Field label="Label status">{data.label_status}</Field>
                  <Field label="Location">
                    {data.location.lat.toFixed(2)}, {data.location.lon.toFixed(2)}
                  </Field>
                </Card>
                <Card className="p-3">
                  <p className="mb-1 text-xs uppercase tracking-wide text-text-muted">Spectral signature</p>
                  <SpectralChart trace={data.spectrum} height={140} />
                </Card>
                <div className="flex gap-2">
                  <Button variant="primary">Request lab confirmation</Button>
                  <Button variant="ghost">Add to labels</Button>
                </div>
              </div>
            </div>

            <p className="text-xs text-text-muted">
              Screening imagery — confirm with a certified lab before any compliance decision.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
