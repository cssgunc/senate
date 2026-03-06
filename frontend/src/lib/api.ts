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
  } catch (error) {
    console.error("Failed to fetch news, falling back to mock data", error);
    const { mockNews } = await import("@/lib/mock/news");
    const start = (page - 1) * limit;
    return mockNews.slice(start, start + limit);
  }
}
