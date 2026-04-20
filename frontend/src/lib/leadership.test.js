import {
  getFallbackLeadership,
  loadLeadershipForPage,
  selectCurrentLeadership,
} from "@/lib/leadership";
import { describe, expect, it } from "vitest";

const sampleLeadership = [
  {
    id: 1,
    title: "Speaker",
    first_name: "Ari",
    last_name: "Ng",
    email: "ari@unc.edu",
    photo_url: null,
    session_number: 2025,
    is_current: true,
  },
  {
    id: 2,
    title: "Deputy",
    first_name: "Bo",
    last_name: "Lee",
    email: "bo@unc.edu",
    photo_url: null,
    session_number: 2024,
    is_current: false,
  },
];

describe("leadership helpers", () => {
  it("selects only current leadership records", () => {
    const result = selectCurrentLeadership(sampleLeadership);
    expect(result).toHaveLength(1);
    expect(result[0].id).toBe(1);
  });

  it("returns empty fallback in production", () => {
    const result = getFallbackLeadership(true);
    expect(result).toEqual([]);
  });

  it("returns current-only mock fallback in development", () => {
    const result = getFallbackLeadership(false);
    expect(result.length).toBeGreaterThan(0);
    expect(result.every((leader) => leader.is_current)).toBe(true);
  });

  it("filters API data to current leadership", async () => {
    const result = await loadLeadershipForPage(
      async () => sampleLeadership,
      true,
    );

    expect(result).toHaveLength(1);
    expect(result[0].id).toBe(1);
  });

  it("falls back to empty list in production when API fails", async () => {
    const result = await loadLeadershipForPage(async () => {
      throw new Error("network");
    }, true);

    expect(result).toEqual([]);
  });
});
