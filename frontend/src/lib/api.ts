// Minimal, valid TypeScript API helper to finish merge resolution.

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  constructor(message?: string) {
    super(message);
    this.name = "ApiError";
  }
}

export async function fetchAPI<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE_URL}${endpoint.startsWith("/") ? endpoint : `/${endpoint}`}`;
  const res = await fetch(url, options as any);
  if (!res.ok) throw new ApiError("API error");
  if (res.status === 204) return undefined as unknown as T;
  return res.json() as Promise<T>;
}

// Intentionally minimal: restore full implementation later if needed.
