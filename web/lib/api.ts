/** Typed client for the FASAL FastAPI backend. */

import type {
  BatchRow,
  CaptureImageKind,
  DatasetSample,
  DatasetSampleDetail,
  FieldDetail,
  FieldSummary,
  FlightRow,
  RegionalStat,
  SampleRequest,
  ZoneDetail,
  ZoneFeatureCollection,
} from "./types";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

/** Absolute URL of a rendered capture image (used directly in <img src>). */
export const datasetImageUrl = (id: string, kind: CaptureImageKind) =>
  `${BASE}/dataset/${id}/image/${kind}.png`;

async function getJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { headers: { Accept: "application/json" } });
  if (!res.ok) throw new Error(`GET ${path} → ${res.status}`);
  return res.json() as Promise<T>;
}

async function postJSON<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path} → ${res.status}`);
  return res.json() as Promise<T>;
}

export const api = {
  health: () => getJSON<{ status: string }>("/health"),
  models: () => getJSON<{ available: string[] }>("/models"),
  fields: () => getJSON<FieldSummary[]>("/fields"),
  field: (id: string) => getJSON<FieldDetail>(`/fields/${id}`),
  fieldZones: (id: string) => getJSON<ZoneFeatureCollection>(`/fields/${id}/zones`),
  zone: (id: string) => getJSON<ZoneDetail>(`/zones/${id}`),
  flights: () => getJSON<FlightRow[]>("/flights"),
  batches: () => getJSON<BatchRow[]>("/batches"),
  regional: () => getJSON<RegionalStat[]>("/regional"),
  labQueue: (lotIds: string[]) => postJSON<SampleRequest>("/lab-queue", { lot_ids: lotIds }),
  dataset: () => getJSON<DatasetSample[]>("/dataset"),
  datasetSample: (id: string) => getJSON<DatasetSampleDetail>(`/dataset/${id}`),
};
