import type { Staff } from "@/types";

export async function loadStaffForPage(
  getStaff: () => Promise<Staff[]>,
): Promise<Staff[]> {
  try {
    return await getStaff();
  } catch (error) {
    console.warn(
      "Failed to fetch staff from API, rendering empty state:",
      error,
    );
    return [];
  }
}
