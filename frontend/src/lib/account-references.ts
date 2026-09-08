/**
 * A GET /accounts/{id}/references response should only be applied to the
 * delete-confirmation dialog if it's still the account being reviewed —
 * the dialog may have been cancelled, or reopened for a different account,
 * while the request was in flight.
 */
export function shouldApplyReferencesResponse(
  activeAccountId: number | null,
  responseAccountId: number,
): boolean {
  return activeAccountId === responseAccountId;
}
