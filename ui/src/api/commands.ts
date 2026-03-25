import { apiFetch } from "./client";
import type { Command, CommandCreateBody } from "../types";

export const createCommand = (siteId: string, body: CommandCreateBody) =>
  apiFetch<Command>(`/api/v1/sites/${siteId}/commands`, {
    method: "POST",
    body: JSON.stringify(body)
  });

export const listCommands = (siteId: string, status?: string) =>
  apiFetch<Command[]>(`/api/v1/sites/${siteId}/commands`, {
    params: status ? { status } : undefined
  });

export const acknowledgeCommand = (commandId: string) =>
  apiFetch<Command>(`/api/v1/commands/${commandId}/ack`, {
    method: "POST"
  });
