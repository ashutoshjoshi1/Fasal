/** Typed client for the FASAL FastAPI backend. Every response is validated against a Zod schema. */

import { z } from "zod";

import {
  BatchRowSchema,
  DatasetSampleDetailSchema,
  DatasetSampleSchema,
  FieldDetailSchema,
  FieldSummarySchema,
  FlightRowSchema,
  RegionalStatSchema,
  SampleRequestSchema,
  ZoneDetailSchema,
  ZoneFeatureCollectionSchema,
} from "./schemas";
import type { CaptureImageKind } from "./types";

const BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
const API_KEY = process.env.NEXT_PUBLIC_API_KEY;

/** Common headers, including the API key when one is configured (auth is open in dev). */
function authHeaders(extra?: Record<string, string>): Record<string, string> {
  return {
    Accept: "application/json",
    ...(API_KEY ? { "X-API-Key": API_KEY } : {}),
    ...extra,
  };
}

/** Absolute URL of a rendered capture image (used directly in <img src>). */
export const datasetImageUrl = (id: string, kind: CaptureImageKind) =>
  `${BASE}/dataset/${id}/image/${kind}.png`;

async function getJSON<S extends z.ZodType>(path: string, schema: S): Promise<z.infer<S>> {
  const res = await fetch(`${BASE}${path}`, { headers: authHeaders() });
  if (!res.ok) throw new Error(`GET ${path} → ${res.status}`);
  return schema.parse(await res.json());
}

async function postJSON<S extends z.ZodType>(
  path: string,
  body: unknown,
  schema: S,
): Promise<z.infer<S>> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: authHeaders({ "Content-Type": "application/json" }),
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path} → ${res.status}`);
  return schema.parse(await res.json());
}

export const api = {
  health: () => getJSON("/health", z.object({ status: z.string() })),
  models: () => getJSON("/models", z.object({ available: z.array(z.string()) })),
  fields: () => getJSON("/fields", z.array(FieldSummarySchema)),
  field: (id: string) => getJSON(`/fields/${id}`, FieldDetailSchema),
  fieldZones: (id: string) => getJSON(`/fields/${id}/zones`, ZoneFeatureCollectionSchema),
  zone: (id: string) => getJSON(`/zones/${id}`, ZoneDetailSchema),
  flights: () => getJSON("/flights", z.array(FlightRowSchema)),
  batches: () => getJSON("/batches", z.array(BatchRowSchema)),
  regional: () => getJSON("/regional", z.array(RegionalStatSchema)),
  labQueue: (lotIds: string[]) => postJSON("/lab-queue", { lot_ids: lotIds }, SampleRequestSchema),
  dataset: () => getJSON("/dataset", z.array(DatasetSampleSchema)),
  datasetSample: (id: string) => getJSON(`/dataset/${id}`, DatasetSampleDetailSchema),
};
