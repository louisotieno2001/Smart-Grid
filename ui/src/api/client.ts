export const TOKEN_KEY = "ems_access_token";

export type ApiErrorShape = {
  status: number;
  message: string;
  detail?: unknown;
};

export class ApiError extends Error {
  status: number;
  detail?: unknown;

  constructor(payload: ApiErrorShape) {
    super(payload.message);
    this.name = "ApiError";
    this.status = payload.status;
    this.detail = payload.detail;
  }
}

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function apiFetch<T>(
  path: string,
  options: RequestInit & { params?: Record<string, string> } = {}
): Promise<T> {
  const { params, headers, ...rest } = options;
  const token = localStorage.getItem(TOKEN_KEY);
  const url = new URL(path, API_BASE);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== "") {
        url.searchParams.set(key, value);
      }
    });
  }

  const response = await fetch(url.toString(), {
    ...rest,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(headers || {})
    }
  });

  if (response.status === 401) {
    localStorage.removeItem(TOKEN_KEY);
    if (window.location.pathname !== "/login") {
      window.location.href = "/login";
    }
    throw new ApiError({ status: 401, message: "Unauthorized" });
  }

  if (!response.ok) {
    let detail: unknown = undefined;
    let message = response.statusText || "Request failed";
    try {
      const data = (await response.json()) as { detail?: unknown; message?: string };
      detail = data.detail ?? data;
      message = data.message || (typeof data.detail === "string" ? data.detail : message);
    } catch {
      message = response.statusText || "Request failed";
    }
    throw new ApiError({ status: response.status, message, detail });
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}
