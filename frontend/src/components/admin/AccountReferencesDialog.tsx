"use client";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import type { Account, AccountReferenceGroup } from "@/types/admin";
import Link from "next/link";

interface AccountReferencesDialogProps {
  account: Account;
  references: AccountReferenceGroup[] | null;
  isLoadingReferences: boolean;
  referencesError: boolean;
  isDeleting: boolean;
  onConfirm: () => void;
  onCancel: () => void;
  onRetry: () => void;
}

export function AccountReferencesDialog({
  account,
  references,
  isLoadingReferences,
  referencesError,
  isDeleting,
  onConfirm,
  onCancel,
  onRetry,
}: AccountReferencesDialogProps) {
  // references is null until a check has actually resolved — that keeps
  // "check failed" from ever being visually indistinguishable from
  // "confirmed zero references" (a genuinely empty result is `[]`).
  const hasReferences = (references?.length ?? 0) > 0;
  const canDelete = !isLoadingReferences && !referencesError;

  return (
    <Dialog open onOpenChange={(open) => !open && onCancel()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>
            Delete {account.first_name} {account.last_name}?
          </DialogTitle>
          <DialogDescription>
            This action cannot be undone.
          </DialogDescription>
        </DialogHeader>

        {isLoadingReferences ? (
          <div className="flex items-center gap-3 py-4 text-sm text-slate-500">
            <div className="h-4 w-4 animate-spin rounded-full border-2 border-slate-200 border-t-blue-600" />
            Checking linked records...
          </div>
        ) : referencesError ? (
          <div className="space-y-3 rounded-md border border-amber-200 bg-amber-50 p-3">
            <p className="text-sm text-amber-800">
              Couldn't check whether this account has linked records. Deleting
              without checking could silently remove authorship/edit history
              from other records — try again before deleting.
            </p>
            <Button type="button" variant="outline" size="sm" onClick={onRetry}>
              Retry check
            </Button>
          </div>
        ) : hasReferences ? (
          <div className="space-y-4">
            <p className="text-sm text-slate-700">
              This account is linked to the following records. Deleting it will
              remove the author/editor link from each — the records themselves
              will not be deleted. Review or reassign them first if you want to
              keep that history.
            </p>
            <ul className="space-y-3">
              {references?.map((group) => (
                <li
                  key={group.type}
                  className="rounded-md border border-slate-200 p-3"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-slate-900">
                      {group.label}
                    </span>
                    <span className="text-xs font-medium text-slate-500">
                      {group.count}
                    </span>
                  </div>
                  <ul className="mt-1 space-y-0.5">
                    {group.items.map((item) => (
                      <li key={item.id} className="text-xs text-slate-600">
                        {item.label}
                      </li>
                    ))}
                    {group.count > group.items.length && (
                      <li className="text-xs text-slate-400">
                        +{group.count - group.items.length} more
                      </li>
                    )}
                  </ul>
                  {group.manage_url && (
                    <Link
                      href={group.manage_url}
                      className="mt-2 inline-block text-xs font-medium text-blue-700 hover:text-blue-800"
                    >
                      Go manage {group.label.toLowerCase()}
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </div>
        ) : (
          <p className="py-2 text-sm text-slate-600">
            This account has no linked records. It's safe to delete.
          </p>
        )}

        <DialogFooter>
          <Button type="button" variant="outline" onClick={onCancel} disabled={isDeleting}>
            Cancel
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={onConfirm}
            disabled={!canDelete || isDeleting}
          >
            {isDeleting ? "Deleting..." : "Delete Account"}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
