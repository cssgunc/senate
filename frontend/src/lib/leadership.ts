import { mockLeadership } from "@/lib/mock/leadership";
import type { Leadership } from "@/types";

export function selectCurrentLeadership(
  leadership: Leadership[],
): Leadership[] {
  return leadership.filter((leader) => leader.is_current);
}

export function getFallbackLeadership(isProduction: boolean): Leadership[] {
  return isProduction ? [] : selectCurrentLeadership(mockLeadership);
}

export async function loadLeadershipForPage(
  getLeadership: () => Promise<Leadership[]>,
  isProduction: boolean = process.env.NODE_ENV === "production",
): Promise<Leadership[]> {
  try {
    const leadership = await getLeadership();
    return selectCurrentLeadership(leadership);
  } catch (error) {
    console.warn(
      "Failed to fetch leadership from API, using environment fallback:",
      error,
    );
    return getFallbackLeadership(isProduction);
  }
}
