import { apiFetch } from "./client";
import type { SimulationRunBody, SimulationRunDetail } from "../types";

export const runSimulation = (siteId: string, body: SimulationRunBody) =>
  apiFetch<SimulationRunDetail>(`/api/v1/sites/${siteId}/simulation/run`, {
    method: "POST",
    body: JSON.stringify(body)
  });

export const getSimulationDetail = (siteId: string, simId: string) =>
  apiFetch<SimulationRunDetail>(`/api/v1/sites/${siteId}/simulation/${simId}`);
