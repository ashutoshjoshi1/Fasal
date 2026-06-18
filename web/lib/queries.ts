/** TanStack Query hooks over the typed API client. */

import { useMutation, useQuery } from "@tanstack/react-query";

import { api } from "./api";

export const useFields = () => useQuery({ queryKey: ["fields"], queryFn: api.fields });

export const useField = (id?: string) =>
  useQuery({ queryKey: ["field", id], queryFn: () => api.field(id as string), enabled: !!id });

export const useFieldZones = (id?: string) =>
  useQuery({ queryKey: ["zones", id], queryFn: () => api.fieldZones(id as string), enabled: !!id });

export const useZone = (id?: string | null) =>
  useQuery({ queryKey: ["zone", id], queryFn: () => api.zone(id as string), enabled: !!id });

export const useFlights = () => useQuery({ queryKey: ["flights"], queryFn: api.flights });

export const useBatches = () => useQuery({ queryKey: ["batches"], queryFn: api.batches });

export const useRegional = () => useQuery({ queryKey: ["regional"], queryFn: api.regional });

export const useLabQueue = () => useMutation({ mutationFn: (lotIds: string[]) => api.labQueue(lotIds) });

export const useDataset = () => useQuery({ queryKey: ["dataset"], queryFn: api.dataset });

export const useDatasetSample = (id?: string | null) =>
  useQuery({ queryKey: ["dataset", id], queryFn: () => api.datasetSample(id as string), enabled: !!id });
