import type {
  BudgetData,
  CalendarEvent,
  CarouselSlide,
  Committee,
  FinanceHearingConfig,
  FinanceHearingDate,
  Legislation,
  LegislationAction,
  News,
  Senator,
  Staff,
  StaticPage,
} from "@/types";
import type {
  Account,
  AdminDistrict,
  AdminLeadership,
  AdminNews,
  AdminStaff,
  AssignCommitteeMember,
  CreateAccount,
  CreateBudgetData,
  CreateCalendarEvent,
  CreateCarouselSlide,
  CreateCommittee,
  CreateDistrict,
  CreateDistrictMapping,
  CreateFinanceHearingDate,
  CreateLeadership,
  CreateLegislation,
  CreateLegislationAction,
  CreateNews,
  CreateSenator,
  CreateStaff,
  DistrictMapping,
  LoginCredentials,
  LoginResponse,
  UpdateDistrict,
  UpdateFinanceHearingConfig,
  UpdateFinanceHearingDate,
  UpdateLeadership,
  UpdateLegislationAction,
  UpdateNews,
  UpdateSenator,
  UpdateStaff,
  UpdateStaticPage,
} from "@/types/admin";
import type { PaginatedResponse } from "@/types/api";
import { clearToken, getToken, setToken } from "./token";

const API_BASE = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api"
).replace(/\/+$/, "");

function buildApiPath(path: string): string {
  if (path.startsWith("/api/")) return path;
  return API_BASE.endsWith("/api") ? path : `/api${path}`;
}

interface AssignCommitteeMemberResponse {
  message: string;
}

function authHeaders(): HeadersInit {
  const token = getToken();
  return {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${buildApiPath(path)}`, {
    ...init,
    headers: {
      ...authHeaders(),
      ...(init?.headers ?? {}),
    },
  });

  if (!res.ok) {
    const errorText = await res.text();
    throw new Error(
      `Admin API request failed (${res.status} ${res.statusText}): ${errorText}`,
    );
  }

  // Some successful endpoints may return no response body.
  if (res.status === 204) return undefined as T;

  const rawBody = await res.text();
  if (!rawBody) return undefined as T;

  return JSON.parse(rawBody) as T;
}

export interface UploadImageResponse {
  url: string;
}

export async function uploadAdminImage(
  file: File,
  onProgress?: (percent: number) => void,
): Promise<UploadImageResponse> {
  const token = getToken();
  const formData = new FormData();
  formData.append("file", file);

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_BASE}${buildApiPath("/admin/upload")}`);

    if (token) {
      xhr.setRequestHeader("Authorization", `Bearer ${token}`);
    }

    xhr.upload.onprogress = (event: ProgressEvent<EventTarget>) => {
      if (!event.lengthComputable || !onProgress) return;
      const percent = Math.round((event.loaded / event.total) * 100);
      onProgress(percent);
    };

    xhr.onerror = () => {
      reject(new Error("Upload failed. Please try again."));
    };

    xhr.onload = () => {
      const responseText = xhr.responseText || "";
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const parsed = JSON.parse(responseText) as UploadImageResponse;
          if (!parsed.url) {
            reject(new Error("Upload succeeded but no URL was returned."));
            return;
          }
          resolve(parsed);
        } catch {
          reject(new Error("Upload succeeded but response parsing failed."));
        }
        return;
      }

      let message = `Upload failed (${xhr.status}).`;
      if (responseText) {
        try {
          const parsed = JSON.parse(responseText) as { detail?: string };
          if (parsed.detail) {
            message = parsed.detail;
          }
        } catch {
          message = responseText;
        }
      }

      reject(new Error(message));
    };

    xhr.send(formData);
  });
}

// Auth
export async function login(
  email: string,
  pid: string,
): Promise<LoginResponse> {
  const body: LoginCredentials = { email, pid };
  const data = await request<LoginResponse>("/auth/login", {
    method: "POST",
    body: JSON.stringify(body),
  });
  setToken(data.access_token);
  return data;
}

export async function getMe(): Promise<Account> {
  return request<Account>("/auth/me", { method: "GET" });
}

export function logout(): void {
  clearToken();
}

// News
export async function getAdminNews(
  page: number = 1,
  limit: number = 20,
  isPublished?: boolean,
): Promise<PaginatedResponse<AdminNews>> {
  const searchParams = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });
  if (isPublished !== undefined) {
    searchParams.set("is_published", isPublished.toString());
  }
  return request(`/admin/news?${searchParams.toString()}`, {
    method: "GET",
  });
}
export async function createNews(data: CreateNews): Promise<News> {
  return request("/admin/news", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateNews(id: number, data: UpdateNews): Promise<News> {
  return request(`/admin/news/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteNews(id: number) {
  return request<void>(`/admin/news/${id}`, { method: "DELETE" });
}

// Senators
export async function createSenator(data: CreateSenator): Promise<Senator> {
  return request("/admin/senators", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function getAdminSenators(
  page: number = 1,
  limit: number = 20,
  is_active?: boolean,
  session?: number,
): Promise<PaginatedResponse<Senator>> {
  const searchParams = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });
  if (is_active !== undefined) {
    searchParams.set("is_active", is_active.toString());
  }
  if (session !== undefined) {
    searchParams.set("session", session.toString());
  }
  return request(`/admin/senators?${searchParams.toString()}`, {
    method: "GET",
  });
}

export async function updateSenator(
  id: number,
  data: UpdateSenator,
): Promise<Senator> {
  return request(`/admin/senators/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteSenator(id: number) {
  return request<void>(`/admin/senators/${id}`, { method: "DELETE" });
}

// Leadership
export async function getAdminLeadership(
  page: number = 1,
  limit: number = 20,
  session_number?: number,
): Promise<PaginatedResponse<AdminLeadership>> {
  const searchParams = new URLSearchParams({
    page: page.toString(),
    limit: limit.toString(),
  });
  if (session_number !== undefined) {
    searchParams.set("session_number", session_number.toString());
  }
  return request(`/admin/leadership?${searchParams.toString()}`, {
    method: "GET",
  });
}

export async function createLeadership(
  data: CreateLeadership,
): Promise<AdminLeadership> {
  return request("/admin/leadership", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateLeadership(
  id: number,
  data: UpdateLeadership,
): Promise<AdminLeadership> {
  return request(`/admin/leadership/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteLeadership(id: number): Promise<void> {
  return request<void>(`/admin/leadership/${id}`, { method: "DELETE" });
}

// Legislation
export async function createLegislation(
  data: CreateLegislation,
): Promise<Legislation> {
  return request("/admin/legislation", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateLegislation(
  id: number,
  data: CreateLegislation,
): Promise<Legislation> {
  return request(`/admin/legislation/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteLegislation(id: number): Promise<void> {
  return request<void>(`/admin/legislation/${id}`, { method: "DELETE" });
}

export async function createLegislationAction(
  legislationId: number,
  data: Omit<CreateLegislationAction, "legislation_id">,
): Promise<LegislationAction> {
  return request(`/admin/legislation/${legislationId}/actions`, {
    method: "POST",
    body: JSON.stringify({ legislation_id: legislationId, ...data }),
  });
}

export async function updateLegislationAction(
  legislationId: number,
  actionId: number,
  data: UpdateLegislationAction,
): Promise<LegislationAction> {
  return request(`/admin/legislation/${legislationId}/actions/${actionId}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteLegislationAction(
  legislationId: number,
  actionId: number,
): Promise<void> {
  return request<void>(
    `/admin/legislation/${legislationId}/actions/${actionId}`,
    {
      method: "DELETE",
    },
  );
}

// Calendar events
export async function createCalendarEvent(
  data: CreateCalendarEvent,
): Promise<CalendarEvent> {
  return request("/admin/events", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateCalendarEvent(
  id: number,
  data: CreateCalendarEvent,
): Promise<CalendarEvent> {
  return request(`/admin/events/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteCalendarEvent(id: number): Promise<void> {
  return request<void>(`/admin/events/${id}`, { method: "DELETE" });
}

// Carousel slides
export async function createCarouselSlide(
  data: CreateCarouselSlide,
): Promise<CarouselSlide> {
  return request("/admin/carousel", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateCarouselSlide(
  id: number,
  data: CreateCarouselSlide,
): Promise<CarouselSlide> {
  return request(`/admin/carousel/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteCarouselSlide(id: number): Promise<void> {
  return request<void>(`/admin/carousel/${id}`, { method: "DELETE" });
}

// Finance hearings
export async function updateFinanceHearingConfig(
  data: UpdateFinanceHearingConfig,
): Promise<FinanceHearingConfig> {
  return request("/admin/finance-hearings/config", {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function createFinanceHearingDate(
  data: CreateFinanceHearingDate,
): Promise<FinanceHearingDate> {
  return request("/admin/finance-hearings/dates", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateFinanceHearingDate(
  id: number,
  data: UpdateFinanceHearingDate,
): Promise<FinanceHearingDate> {
  return request(`/admin/finance-hearings/dates/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteFinanceHearingDate(id: number): Promise<void> {
  return request<void>(`/admin/finance-hearings/dates/${id}`, {
    method: "DELETE",
  });
}

// Committees
export async function getAdminCommittees(): Promise<Committee[]> {
  return request("/admin/committees", {
    method: "GET",
  });
}

export async function createCommittee(
  data: CreateCommittee,
): Promise<Committee> {
  return request("/admin/committees", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateCommittee(
  id: number,
  data: CreateCommittee,
): Promise<Committee> {
  return request(`/admin/committees/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteCommittee(id: number): Promise<void> {
  return request<void>(`/admin/committees/${id}`, { method: "DELETE" });
}

export async function assignCommitteeMember(
  committeeId: number,
  data: AssignCommitteeMember,
): Promise<AssignCommitteeMemberResponse> {
  return request(`/admin/committees/${committeeId}/members`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function removeCommitteeMember(
  committeeId: number,
  senatorId: number,
): Promise<void> {
  return request<void>(
    `/admin/committees/${committeeId}/members/${senatorId}`,
    {
      method: "DELETE",
    },
  );
}

// Staff
export async function listAdminStaff(): Promise<AdminStaff[]> {
  return request("/admin/staff", { method: "GET" });
}

export async function createStaff(data: CreateStaff): Promise<Staff> {
  return request("/admin/staff", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateStaff(
  id: number,
  data: UpdateStaff,
): Promise<Staff> {
  return request(`/admin/staff/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteStaff(id: number): Promise<void> {
  return request<void>(`/admin/staff/${id}`, { method: "DELETE" });
}

// Budget
export async function createBudgetData(
  data: CreateBudgetData,
): Promise<BudgetData> {
  return request("/admin/budget", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateBudgetData(
  id: number,
  data: CreateBudgetData,
): Promise<BudgetData> {
  return request(`/admin/budget/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteBudgetData(id: number): Promise<void> {
  return request<void>(`/admin/budget/${id}`, { method: "DELETE" });
}

// Districts
export async function listAdminDistricts(): Promise<AdminDistrict[]> {
  return request("/admin/districts", { method: "GET" });
}

export async function createDistrict(
  data: CreateDistrict,
): Promise<AdminDistrict> {
  return request("/admin/districts", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateDistrict(
  id: number,
  data: UpdateDistrict,
): Promise<AdminDistrict> {
  return request(`/admin/districts/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteDistrict(id: number): Promise<void> {
  return request<void>(`/admin/districts/${id}`, { method: "DELETE" });
}

// District Mappings
export async function listDistrictMappings(
  districtId: number,
): Promise<DistrictMapping[]> {
  return request(`/admin/districts/${districtId}/mappings`, { method: "GET" });
}

export async function createDistrictMapping(
  districtId: number,
  data: CreateDistrictMapping,
): Promise<DistrictMapping> {
  return request(`/admin/districts/${districtId}/mappings`, {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function deleteDistrictMapping(
  districtId: number,
  mapId: number,
): Promise<void> {
  return request<void>(`/admin/districts/${districtId}/mappings/${mapId}`, {
    method: "DELETE",
  });
}

// Static pages
export async function listStaticPages(): Promise<StaticPage[]> {
  return request("/admin/pages", { method: "GET" });
}

export async function updateStaticPage(
  slug: string,
  data: UpdateStaticPage,
): Promise<StaticPage> {
  return request(`/admin/pages/${slug}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

// Accounts
export async function listAdminAccounts(
  page: number = 1,
  limit: number = 100,
): Promise<PaginatedResponse<Account>> {
  return request(`/admin/accounts?page=${page}&limit=${limit}`, {
    method: "GET",
  });
}

export async function createAccount(data: CreateAccount): Promise<Account> {
  return request("/admin/accounts", {
    method: "POST",
    body: JSON.stringify(data),
  });
}

export async function updateAccount(
  id: number,
  data: CreateAccount,
): Promise<Account> {
  return request(`/admin/accounts/${id}`, {
    method: "PUT",
    body: JSON.stringify(data),
  });
}

export async function deleteAccount(id: number): Promise<void> {
  return request<void>(`/admin/accounts/${id}`, { method: "DELETE" });
}

export async function getAdminEvents(): Promise<CalendarEvent[]> {
  return request<CalendarEvent[]>("/admin/events", { method: "GET" });
}

export async function getAdminCarouselSlides(): Promise<CarouselSlide[]> {
  return request<CarouselSlide[]>("/admin/carousel", { method: "GET" });
}

export async function reorderCarouselSlides(
  slide_ids: number[],
): Promise<void> {
  return request<void>("/admin/carousel/reorder", {
    method: "PUT",
    body: JSON.stringify({ slide_ids }),
  });
}
