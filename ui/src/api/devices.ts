import { apiFetch } from "./client";
import type { Device, DeviceCreateBody } from "../types";

export const createSiteDevice = (siteId: string, body: DeviceCreateBody) =>
  apiFetch<Device>(`/api/v1/sites/${siteId}/devices`, {
    method: "POST",
    body: JSON.stringify(body)
  });

export const getSiteDevices = (siteId: string) => apiFetch<Device[]>(`/api/v1/sites/${siteId}/devices`);

export const createAsset = (siteId: string, body: Record<string, unknown>) =>
  apiFetch<Record<string, unknown>>(`/api/v1/sites/${siteId}/assets`, {
    method: "POST",
    body: JSON.stringify(body)
  });

export const createAssetDevice = (assetId: string, body: Record<string, unknown>) =>
  apiFetch<Record<string, unknown>>(`/api/v1/assets/${assetId}/devices`, {
    method: "POST",
    body: JSON.stringify(body)
  });

export const createDeviceMapping = (deviceId: string, body: Record<string, unknown>) =>
  apiFetch<Record<string, unknown>>(`/api/v1/devices/${deviceId}/mappings`, {
    method: "POST",
    body: JSON.stringify(body)
  });
