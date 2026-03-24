/**
 * API client utilities
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

class ApiError extends Error {
  status: number;

  constructor(status: number, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

interface NewsApiArticle {
  id: number | string;
  title: string;
  summary?: string;
  description?: string;
  body: string;
  author_name?: string | null;
  author?: string | null;
  image_url: string | null;
  date_published: string;
  date_last_edited?: string | null;
  date_edited?: string | null;
}

interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}

export interface NewsArticle {
  id: string;
  title: string;
  description: string;
  body: string;
  author: string | null;
  image_url: string | null;
  date_published: string;
  date_edited: string | null;
}

function mapNewsArticle(article: NewsApiArticle): NewsArticle {
  return {
    id: String(article.id),
    title: article.title,
    description: article.summary ?? article.description ?? "",
    body: article.body,
    author: article.author_name ?? article.author ?? null,
    image_url: article.image_url,
    date_published: article.date_published,
    date_edited: article.date_last_edited ?? article.date_edited ?? null,
  };
}

function sortMostRecentFirst(articles: NewsArticle[]): NewsArticle[] {
  return [...articles].sort(
    (a, b) =>
      new Date(b.date_published).getTime() -
      new Date(a.date_published).getTime(),
  );
}

export async function fetchAPI<T>(
  endpoint: string,
  options?: RequestInit,
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, options);

  if (!response.ok) {
    throw new ApiError(response.status, `API error: ${response.statusText}`);
  }

  return response.json() as Promise<T>;
}

export async function getNews(
  page: number = 1,
  limit: number = 10,
): Promise<NewsArticle[]> {
  try {
    const data = await fetchAPI<PaginatedResponse<NewsApiArticle>>(
      `/news?page=${page}&limit=${limit}`,
    );
    return sortMostRecentFirst(data.items.map(mapNewsArticle));
  } catch (error) {
    if (error instanceof ApiError && error.status < 500) {
      throw error;
    }

    console.warn("[API] Backend unavailable — using mock news data");
    const { mockNews } = await import("@/lib/mock/news");
    const start = (page - 1) * limit;
    return sortMostRecentFirst(mockNews).slice(start, start + limit);
  }
}

export async function getNewsById(id: string): Promise<NewsArticle | null> {
  try {
    const data = await fetchAPI<NewsApiArticle>(`/news/${id}`);
    return mapNewsArticle(data);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      return null;
    }

    if (error instanceof ApiError && error.status < 500) {
      throw error;
    }

    console.warn("[API] Backend unavailable — using mock news article");
    const { mockNews } = await import("@/lib/mock/news");
    return mockNews.find((article) => article.id === id) ?? null;
  }
}
