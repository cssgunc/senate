import type {
  BudgetData,
  CalendarEvent,
  CarouselSlide,
  Committee,
  District,
  FinanceHearingConfig,
  Leadership,
  Legislation,
  News,
  Senator,
  Staff,
  StaticPage,
} from "@/types";
import type { PaginatedResponse } from "@/types/api";

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  details: unknown;

  constructor(status: number, message: string, details?: unknown) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.details = details;
  }
}

type QueryPrimitive = string | number | boolean | null | undefined;
type QueryValue = QueryPrimitive | QueryPrimitive[];

export interface GetSenatorsParams {
  search?: string;
  districtId?: number;
  committee?: number;
  session?: number;
}

export interface GetLegislationParams {
  search?: string;
  status?: string;
  type?: string;
  session?: number;
  sponsor?: string;
  page?: number;
  limit?: number;
}

export interface GetEventsParams {
  startDate?: string;
  endDate?: string;
  eventType?: string;
}

function createQueryString(params: Record<string, QueryValue>): string {
  const searchParams = new URLSearchParams();

  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === "") {
      return;
    }

    if (Array.isArray(value)) {
      value.forEach((item) => {
        if (item !== undefined && item !== null && item !== "") {
          searchParams.append(key, String(item));
        }
      });
      return;
    }

    searchParams.set(key, String(value));
  });

  const query = searchParams.toString();
  return query ? `?${query}` : "";
}

function normalizeEndpoint(endpoint: string): string {
  return endpoint.startsWith("/") ? endpoint : `/${endpoint}`;
}

function buildLeadershipEndpoint(session?: number): string {
  const query = createQueryString({ session_number: session });
  const endpoint = `/api/leadership${query}`;

  // Guard against accidental regressions like /api/leadership/?session_number=...
  console.assert(
    !endpoint.includes("/?"),
    "Leadership endpoint should not include a trailing slash before query params",
  );

  return endpoint;
}

async function extractErrorDetails(response: Response): Promise<unknown> {
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/json")) {
    return response.json();
  }

  try {
    return await response.text();
  } catch {
    return null;
  }
}

export async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${API_BASE_URL}${normalizeEndpoint(endpoint)}`;

  let response: Response;
  try {
    response = await fetch(url, options);
  } catch (error) {
    throw new ApiError(0, "Network request failed", error);
  }

  if (!response.ok) {
    const details = await extractErrorDetails(response);
    const message =
      typeof details === "object" &&
      details !== null &&
      "detail" in details &&
      typeof details.detail === "string"
        ? details.detail
        : `API request failed with status ${response.status}`;

    throw new ApiError(response.status, message, details);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json() as Promise<T>;
}

export async function getNews(
  page: number = 1,
  limit: number = 10,
): Promise<PaginatedResponse<News>> {
  const query = createQueryString({ page, limit });
  return fetchAPI<PaginatedResponse<News>>(`/api/news${query}`);
}

export async function getNewsById(id: string | number): Promise<News> {
  return fetchAPI<News>(`/api/news/${id}`);
}

export async function getSenators(
  params: GetSenatorsParams = {},
): Promise<Senator[]> {
  const query = createQueryString({
    search: params.search,
    district_id: params.districtId,
    committee: params.committee,
    session: params.session,
  });
  return fetchAPI<Senator[]>(`/api/senators${query}`);
}

export async function getSenatorById(id: string | number): Promise<Senator> {
  return fetchAPI<Senator>(`/api/senators/${id}`);
}

export async function getLeadership(session?: number): Promise<Leadership[]> {
  return fetchAPI<Leadership[]>(buildLeadershipEndpoint(session));
}

export async function getCommittees(): Promise<Committee[]> {
  return fetchAPI<Committee[]>("/api/committees/");
}

export async function getCommitteeById(
  id: string | number,
): Promise<Committee> {
  return fetchAPI<Committee>(`/api/committees/${id}`);
}

export async function getLegislation(
  params: GetLegislationParams = {},
): Promise<PaginatedResponse<Legislation>> {
  const query = createQueryString({
    search: params.search,
    status: params.status,
    type: params.type,
    session: params.session,
    sponsor: params.sponsor,
    page: params.page,
    limit: params.limit,
  });
  return fetchAPI<PaginatedResponse<Legislation>>(`/api/legislation${query}`);
}

export async function getLegislationById(
  id: string | number,
): Promise<Legislation> {
  return fetchAPI<Legislation>(`/api/legislation/${id}`);
}

export async function getRecentLegislation(
  limit: number = 10,
  type?: string,
): Promise<Legislation[]> {
  const query = createQueryString({ limit, type });
  return fetchAPI<Legislation[]>(`/api/legislation/recent${query}`);
}

export async function getEvents(
  params: GetEventsParams = {},
): Promise<CalendarEvent[]> {
  const query = createQueryString({
    start_date: params.startDate,
    end_date: params.endDate,
    event_type: params.eventType,
  });
  return fetchAPI<CalendarEvent[]>(`/api/events${query}`);
}

export async function getCarousel(): Promise<CarouselSlide[]> {
  return fetchAPI<CarouselSlide[]>("/api/carousel");
}

export async function getFinanceHearings(): Promise<FinanceHearingConfig> {
  return fetchAPI<FinanceHearingConfig>("/api/finance-hearings");
}

export async function getStaff(): Promise<Staff[]> {
  return fetchAPI<Staff[]>("/api/staff");
}

export async function getDistricts(): Promise<District[]> {
  return fetchAPI<District[]>("/api/districts");
}

export async function getBudget(fiscalYear?: string): Promise<BudgetData[]> {
  const query = createQueryString({ fiscal_year: fiscalYear });
  return fetchAPI<BudgetData[]>(`/api/budget${query}`);
}

export async function getBudgetYears(): Promise<string[]> {
  return fetchAPI<string[]>("/api/budget/years");
}

export async function getStaticPage(slug: string): Promise<StaticPage> {
  return fetchAPI<StaticPage>(`/api/pages/${slug}`);
}

export interface ContactFormData {
  name: string;
  email: string;
  message: string;
  senator_id?: number;
}

export async function submitContactForm(
  data: ContactFormData,
): Promise<{ success: boolean }> {
  return fetchAPI<{ success: boolean }>("/api/contact", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
}
