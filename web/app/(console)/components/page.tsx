"use client";

import type { ReactNode } from "react";

import { SpectralChart } from "@/components/charts/SpectralChart";
import { ActionCard } from "@/components/ui/ActionCard";
import { Button } from "@/components/ui/Button";
import { ConfidenceChip } from "@/components/ui/ConfidenceChip";
import { CoverageMeter } from "@/components/ui/CoverageMeter";
import { OODBanner } from "@/components/ui/OODBanner";
import { Card } from "@/components/ui/primitives";
import { ReasonCodeList } from "@/components/ui/ReasonCodeList";
import { RiskBadge } from "@/components/ui/RiskBadge";
import type { Action, ReasonCode, SpectrumTrace } from "@/lib/types";

const TRACE: SpectrumTrace = (() => {
  const wavelengths: number[] = [];
  const sample: number[] = [];
  const control: number[] = [];
  for (let x = 450; x <= 995; x += 5) {
    wavelengths.push(x);
    const base = 0.05 + (0.5 - 0.05) / (1 + Math.exp(-(x - 715) / 12));
    control.push(base);
    sample.push(Math.max(0, base - 0.06 * Math.exp(-0.5 * ((x - 920) / 18) ** 2)));
  }
  return { wavelengths, sample, control };
})();

const REASONS: ReasonCode[] = [
  { type: "swir_anomaly", detail: "band ~925 nm strongly influenced this zone", weight: 1 },
  { type: "spray_timing", detail: "recent spray application", weight: 1 },
  { type: "low_coverage", detail: "low usable coverage (42%)", weight: 1 },
];

const ACTIONS: Action[] = ["clear", "collect_sample", "close_range_scan", "send_to_lab"];

function Row({ title, children }: { title: string; children: ReactNode }) {
  return (
    <Card className="p-4">
      <p className="mb-3 text-xs uppercase tracking-wide text-text-muted">{title}</p>
      <div className="flex flex-wrap items-center gap-3">{children}</div>
    </Card>
  );
}

export default function ComponentsPage() {
  return (
    <div className="p-6">
      <header className="mb-4">
        <h1 className="text-xl font-semibold text-text-primary">Component library</h1>
        <p className="text-sm text-text-secondary">
          The FASAL design system — risk semantics, trust-first UX, and data visualization.
        </p>
      </header>
      <div className="grid gap-4 lg:grid-cols-2">
        <Row title="Risk badges — color + icon + label (hatch on high)">
          <RiskBadge riskClass="low" score={0.18} />
          <RiskBadge riskClass="medium" score={0.52} />
          <RiskBadge riskClass="high" score={0.91} />
        </Row>
        <Row title="Confidence chips (separate channel from risk)">
          <ConfidenceChip confidence="high" />
          <ConfidenceChip confidence="uncertain" />
          <ConfidenceChip confidence="ood" />
        </Row>
        <Row title="Buttons">
          <Button variant="primary">Primary</Button>
          <Button variant="secondary">Secondary</Button>
          <Button variant="ghost">Ghost</Button>
          <Button variant="danger">Danger</Button>
        </Row>
        <Card className="p-4">
          <p className="mb-3 text-xs uppercase tracking-wide text-text-muted">Coverage meter</p>
          <div className="flex flex-col gap-2">
            <CoverageMeter value={0.92} />
            <CoverageMeter value={0.61} />
            <CoverageMeter value={0.34} />
          </div>
        </Card>
        <Card className="p-4">
          <p className="mb-2 text-xs uppercase tracking-wide text-text-muted">Reason codes</p>
          <ReasonCodeList codes={REASONS} />
        </Card>
        <Card className="p-4">
          <p className="mb-2 text-xs uppercase tracking-wide text-text-muted">OOD banner</p>
          <OODBanner />
        </Card>
        {ACTIONS.map((a) => (
          <ActionCard key={a} action={a} />
        ))}
        <Card className="p-4 lg:col-span-2">
          <p className="mb-2 text-xs uppercase tracking-wide text-text-muted">Spectral chart</p>
          <SpectralChart trace={TRACE} />
        </Card>
      </div>
    </div>
  );
}
