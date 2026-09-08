import { describe, expect, it } from "vitest";

import { shouldApplyReferencesResponse } from "@/lib/account-references";

describe("shouldApplyReferencesResponse", () => {
  it("applies a response that matches the currently open account", () => {
    expect(shouldApplyReferencesResponse(5, 5)).toBe(true);
  });

  it("discards a response for a dialog that was cancelled in the meantime", () => {
    expect(shouldApplyReferencesResponse(null, 5)).toBe(false);
  });

  it("discards a stale response superseded by a different account's dialog", () => {
    // Regression test: clicking Delete on account 5 (slow request), then
    // Cancel, then Delete on account 7 (fast) used to let account 5's
    // late-arriving response silently overwrite the dialog that was by
    // then showing account 7 — including a false "safe to delete".
    expect(shouldApplyReferencesResponse(7, 5)).toBe(false);
  });
});
