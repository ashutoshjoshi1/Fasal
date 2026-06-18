"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";

import { useSelectedField } from "@/components/shell/field-context";
import { LayerSwitcher } from "@/components/map/LayerSwitcher";
import { MapLegend } from "@/components/map/MapLegend";
import type { LayerMode } from "@/components/map/RiskMap";
import { ZoneInspector } from "@/components/inspector/ZoneInspector";
import { ConfidenceChip } from "@/components/ui/ConfidenceChip";
import { CoverageMeter } from "@/components/ui/CoverageMeter";
import { RiskBadge } from "@/components/ui/RiskBadge";
import { ErrorState } from "@/components/ui/states";
import { useField, useFields, useFieldZones } from "@/lib/queries";

const RiskMap = dynamic(() => import("@/components/map/RiskMap").then((m) => m.RiskMap), {
  ssr: false,
  loading: () => <div className="grid h-full place-items-center text-sm text-text-muted">Loading map…</div>,
});

export default function FieldMapPage() {
  const { data: fields } = useFields();
  const { fieldId, setFieldId } = useSelectedField();
  useEffect(() => {
    if (!fieldId && fields?.length) setFieldId(fields[0].id);
  }, [fields, fieldId, setFieldId]);

  const activeId = fieldId ?? fields?.[0]?.id;
  const { data: field } = useField(activeId);
  const { data: zones, isError } = useFieldZones(activeId);
  const [layerMode, setLayerMode] = useState<LayerMode>("risk");
  const [selectedZoneId, setSelectedZoneId] = useState<string | null>(null);
  useEffect(() => setSelectedZoneId(null), [activeId]);

  return (
    <div className="flex h-full">
      <div className="relative min-w-0 flex-1">
        {isError ? (
          <div className="grid h-full place-items-center p-6">
            <ErrorState />
          </div>
        ) : (
          <RiskMap
            geojson={zones}
            bbox={field?.bbox}
            layerMode={layerMode}
            selectedZoneId={selectedZoneId}
            onZoneClick={setSelectedZoneId}
          />
        )}

        {field && (
          <div className="absolute left-3 top-3 max-w-xs rounded-card border border-border bg-surface-1 p-3 shadow-[var(--shadow-raised)]">
            <p className="text-sm font-semibold text-text-primary">{field.name}</p>
            <p className="font-mono text-xs text-text-muted">
              {field.crop} · {field.area_ha} ha · {field.n_zones} zones
            </p>
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <RiskBadge riskClass={field.risk_class} score={field.risk_score} size="sm" />
              <ConfidenceChip confidence={field.confidence} />
            </div>
            <div className="mt-2">
              <CoverageMeter value={field.coverage} />
            </div>
          </div>
        )}

        <div className="absolute right-3 top-3">
          <LayerSwitcher mode={layerMode} onChange={setLayerMode} />
        </div>
        <div className="absolute bottom-3 left-3">
          <MapLegend mode={layerMode} />
        </div>
      </div>

      <aside className="w-[380px] shrink-0 overflow-auto border-l border-border bg-surface-app p-4">
        <ZoneInspector zoneId={selectedZoneId} onClose={() => setSelectedZoneId(null)} />
      </aside>
    </div>
  );
}
