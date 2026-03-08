/**
 * API client utilities
 */

export const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export async function fetchAPI(endpoint: string, options?: RequestInit) {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, options);

  if (!response.ok) {
    throw new Error(`API error: ${response.statusText}`);
  }

  return response.json();
}

export async function getNews(page: number = 1, limit: number = 10) {
  try {
    const data = await fetchAPI(`/news?page=${page}&limit=${limit}`);
    return data;
  } catch {
    console.warn("[API] Backend unavailable — using mock news data");
    const { mockNews } = await import("@/lib/mock/news");
    const start = (page - 1) * limit;
    return mockNews.slice(start, start + limit);
  }
}

export async function getNewsById(id: string) {
  try {
    const data = await fetchAPI(`/news/${id}`);
    return data;
  } catch {
    console.warn("[API] Backend unavailable — using mock news article");
    const { mockNews } = await import("@/lib/mock/news");
    return mockNews.find((article) => article.id === id) ?? null;
  }
}
