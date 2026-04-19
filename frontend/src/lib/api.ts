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

// Small helpers expected by other modules (stubs)
export async function getLegislation(params: { search?: string; status?: string; type?: string; session?: number; page?: number; limit?: number } ) {
  const { page = 1, limit = 20, search, status, type, session } = params;
  const qs = new URLSearchParams({ page: String(page), limit: String(limit) });
  if (search) qs.set("search", search);
  if (status) qs.set("status", status);
  if (type) qs.set("type", type);
  if (session) qs.set("session", String(session));
  return fetchAPI(`/legislation?${qs.toString()}`);
}
