"use client";

import maplibregl, {
  type GeoJSONSource,
  type Map as MapLibreMap,
  type StyleSpecification,
} from "maplibre-gl";
import { useCallback, useEffect, useRef } from "react";

import { MAP_CONF_COLORS, MAP_NO_DATA, MAP_RISK_COLORS } from "@/lib/risk";
import type { ZoneFeatureCollection } from "@/lib/types";

export type LayerMode = "risk" | "confidence";

const BLANK_STYLE: StyleSpecification = {
  version: 8,
  sources: {},
  layers: [{ id: "bg", type: "background", paint: { "background-color": "#e7e3da" } }],
};

const SRC = "zones";
const FILL = "zones-fill";
const LINE = "zones-line";
const SEL = "zones-selected";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
function fillColor(mode: LayerMode): any {
  if (mode === "confidence") {
    return ["match", ["get", "confidence"], "high", MAP_CONF_COLORS.high, "uncertain", MAP_CONF_COLORS.uncertain, "ood", MAP_CONF_COLORS.ood, MAP_NO_DATA];
  }
  return ["match", ["get", "risk_class"], "low", MAP_RISK_COLORS.low, "medium", MAP_RISK_COLORS.medium, "high", MAP_RISK_COLORS.high, MAP_NO_DATA];
}

export function RiskMap({
  geojson,
  bbox,
  layerMode = "risk",
  selectedZoneId,
  onZoneClick,
}: {
  geojson?: ZoneFeatureCollection;
  bbox?: [number, number, number, number];
  layerMode?: LayerMode;
  selectedZoneId?: string | null;
  onZoneClick?: (zoneId: string) => void;
}) {
  const container = useRef<HTMLDivElement>(null);
  const mapRef = useRef<MapLibreMap | null>(null);
  const ready = useRef(false);
  const geojsonRef = useRef(geojson);
  geojsonRef.current = geojson;
  const layerModeRef = useRef(layerMode);
  layerModeRef.current = layerMode;
  const clickRef = useRef(onZoneClick);
  clickRef.current = onZoneClick;

  const apply = useCallback(() => {
    const map = mapRef.current;
    if (!map || !ready.current || !geojsonRef.current) return;
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const data = geojsonRef.current as any;
    if (map.getSource(SRC)) {
      (map.getSource(SRC) as GeoJSONSource).setData(data);
      return;
    }
    map.addSource(SRC, { type: "geojson", data });
    map.addLayer({ id: FILL, type: "fill", source: SRC, paint: { "fill-color": fillColor(layerModeRef.current), "fill-opacity": 0.58 } });
    map.addLayer({ id: LINE, type: "line", source: SRC, paint: { "line-color": "#ffffff", "line-width": 0.4, "line-opacity": 0.5 } });
    map.addLayer({ id: SEL, type: "line", source: SRC, paint: { "line-color": "#16161a", "line-width": 2.2 }, filter: ["==", ["get", "zone_id"], "__none__"] });
    map.on("click", FILL, (e) => {
      const id = e.features?.[0]?.properties?.zone_id as string | undefined;
      if (id) clickRef.current?.(id);
    });
    map.on("mouseenter", FILL, () => (map.getCanvas().style.cursor = "pointer"));
    map.on("mouseleave", FILL, () => (map.getCanvas().style.cursor = ""));
  }, []);

  useEffect(() => {
    if (!container.current || mapRef.current) return;
    const style = (process.env.NEXT_PUBLIC_MAP_STYLE as string | undefined) ?? BLANK_STYLE;
    const map = new maplibregl.Map({ container: container.current, style, center: [0, 0], zoom: 12, attributionControl: false });
    map.addControl(new maplibregl.NavigationControl({ showCompass: false }), "bottom-right");
    map.on("load", () => {
      ready.current = true;
      apply();
    });
    mapRef.current = map;
    return () => {
      map.remove();
      mapRef.current = null;
      ready.current = false;
    };
  }, [apply]);

  useEffect(() => {
    apply();
  }, [geojson, apply]);

  useEffect(() => {
    const map = mapRef.current;
    if (map && ready.current && map.getLayer(FILL)) map.setPaintProperty(FILL, "fill-color", fillColor(layerMode));
  }, [layerMode]);

  useEffect(() => {
    const map = mapRef.current;
    if (map && ready.current && map.getLayer(SEL)) map.setFilter(SEL, ["==", ["get", "zone_id"], selectedZoneId ?? "__none__"]);
  }, [selectedZoneId]);

  useEffect(() => {
    const map = mapRef.current;
    if (map && ready.current && bbox) {
      map.fitBounds(
        [
          [bbox[0], bbox[1]],
          [bbox[2], bbox[3]],
        ],
        { padding: 48, duration: 600 },
      );
    }
  }, [bbox]);

  return <div ref={container} className="h-full w-full" aria-label="Field risk map" role="application" />;
}
