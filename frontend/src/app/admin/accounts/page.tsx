"use client";

import { AccountForm } from "@/components/admin/AccountForm";
import { AccountReferencesDialog } from "@/components/admin/AccountReferencesDialog";
import {
  AdminBackButton,
  AdminCard,
  AdminPageHeader,
  AdminPageShell,
} from "@/components/admin/AdminPageShell";
import { DataTable } from "@/components/admin/DataTable";
import { Button } from "@/components/ui/button";
import {
  createAccount,
  deleteAccount,
  getAccountReferences,
  getMe,
  listAdminAccounts,
  updateAccount,
} from "@/lib/admin-api";
import type {
  Account,
  AccountReferenceGroup,
  CreateAccount,
  UpdateAccount,
} from "@/types/admin";
import type { ColumnDef } from "@tanstack/react-table";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";

export default function AdminAccountsPage() {
  const router = useRouter();
  const [data, setData] = useState<Account[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [currentUser, setCurrentUser] = useState<Account | null>(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingAccount, setEditingAccount] = useState<Account | undefined>(
    undefined,
  );
  const [isSaving, setIsSaving] = useState(false);
  const [pendingDelete, setPendingDelete] = useState<Account | null>(null);
  const [pendingReferences, setPendingReferences] = useState<
    AccountReferenceGroup[] | null
  >(null);
  const [isLoadingReferences, setIsLoadingReferences] = useState(false);
  const [referencesError, setReferencesError] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  // Tracks which account the dialog is currently open for, so a slow
  // references response for an account that's no longer the open one
  // (cancelled, or superseded by a click on a different account) can be
  // discarded instead of silently overwriting the dialog with stale data.
  const activeDeleteAccountId = useRef<number | null>(null);

  const fetchAccounts = async () => {
    setIsLoading(true);
    try {
      const response = await listAdminAccounts();
      setData(Array.isArray(response) ? response : response.items);
    } catch (error) {
      console.error("Failed to fetch accounts:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    const init = async () => {
      try {
        const me = await getMe();
        if (me.role !== "admin") {
          router.replace("/admin");
          return;
        }
        setCurrentUser(me);
        await fetchAccounts();
      } catch {
        router.replace("/admin/login");
      }
    };
    init();
  }, [router]);

  const handleEdit = (account: Account) => {
    setEditingAccount(account);
    setIsFormOpen(true);
  };

  const loadReferences = async (accountId: number) => {
    setIsLoadingReferences(true);
    setReferencesError(false);
    try {
      const { references } = await getAccountReferences(accountId);
      // The dialog may have been cancelled or reopened for a different
      // account while this request was in flight — only apply the result
      // if it's still the one being reviewed.
      if (activeDeleteAccountId.current !== accountId) return;
      setPendingReferences(references);
    } catch (error) {
      console.error("Failed to load account references:", error);
      if (activeDeleteAccountId.current !== accountId) return;
      // Leave pendingReferences as null (distinct from a confirmed-empty
      // []) so the dialog can't present a failed check as "safe to delete".
      setPendingReferences(null);
      setReferencesError(true);
    } finally {
      if (activeDeleteAccountId.current === accountId) {
        setIsLoadingReferences(false);
      }
    }
  };

  const handleDeleteClick = (account: Account) => {
    activeDeleteAccountId.current = account.id;
    setPendingDelete(account);
    setPendingReferences(null);
    setReferencesError(false);
    loadReferences(account.id);
  };

  const handleRetryReferences = () => {
    if (!pendingDelete) return;
    loadReferences(pendingDelete.id);
  };

  const handleCancelDelete = () => {
    if (isDeleting) return;
    activeDeleteAccountId.current = null;
    setPendingDelete(null);
    setPendingReferences(null);
    setReferencesError(false);
  };

  const handleConfirmDelete = async () => {
    if (!pendingDelete) return;
    setIsDeleting(true);
    try {
      await deleteAccount(pendingDelete.id);
      activeDeleteAccountId.current = null;
      setPendingDelete(null);
      setPendingReferences(null);
      setReferencesError(false);
      await fetchAccounts();
    } catch (error) {
      console.error("Failed to delete account:", error);
      alert(error instanceof Error ? error.message : "Failed to delete account");
    } finally {
      setIsDeleting(false);
    }
  };

  const handleFormSubmit = async (formData: CreateAccount | UpdateAccount) => {
    setIsSaving(true);
    try {
      if (editingAccount) {
        await updateAccount(editingAccount.id, formData as UpdateAccount);
      } else {
        await createAccount(formData as CreateAccount);
      }
      setIsFormOpen(false);
      setEditingAccount(undefined);
      fetchAccounts();
    } catch (error) {
      console.error("Failed to save account:", error);
      alert(
        error instanceof Error
          ? error.message
          : "Failed to save account. The email or Onyen may already be in use.",
      );
    } finally {
      setIsSaving(false);
    }
  };

  const columns: ColumnDef<Account>[] = [
    {
      id: "name",
      header: "Name",
      cell: ({ row }) => `${row.original.first_name} ${row.original.last_name}`,
    },
    {
      accessorKey: "email",
      header: "Email",
    },
    {
      accessorKey: "onyen",
      header: "Onyen",
      cell: ({ row }) => (
        <span className="font-mono text-sm">{row.getValue("onyen")}</span>
      ),
    },
    {
      accessorKey: "role",
      header: "Role",
      cell: ({ row }) => {
        const role = row.getValue("role") as string;
        return (
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium ${role === "admin" ? "bg-purple-100 text-purple-800" : "bg-blue-100 text-blue-800"}`}
          >
            {role.charAt(0).toUpperCase() + role.slice(1)}
          </span>
        );
      },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const account = row.original;
        const isSelf = currentUser?.id === account.id;
        return (
          <div className="flex gap-3">
            <button
              onClick={() => handleEdit(account)}
              className="text-sm font-medium text-blue-700 hover:text-blue-800"
            >
              Edit
            </button>
            {!isSelf && (
              <button
                onClick={() => handleDeleteClick(account)}
                className="text-sm font-medium text-rose-700 hover:text-rose-800"
              >
                Delete
              </button>
            )}
          </div>
        );
      },
    },
  ];

  const deleteDialog = pendingDelete && (
    <AccountReferencesDialog
      account={pendingDelete}
      references={pendingReferences}
      isLoadingReferences={isLoadingReferences}
      referencesError={referencesError}
      isDeleting={isDeleting}
      onConfirm={handleConfirmDelete}
      onCancel={handleCancelDelete}
      onRetry={handleRetryReferences}
    />
  );

  if (isFormOpen) {
    return (
      <AdminPageShell className="max-w-3xl">
        <AdminBackButton
          onClick={() => {
            setIsFormOpen(false);
            setEditingAccount(undefined);
          }}
          label="Back to Accounts Table"
        />
        <AccountForm
          initialData={editingAccount}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setIsFormOpen(false);
            setEditingAccount(undefined);
          }}
          isLoading={isSaving}
        />
      </AdminPageShell>
    );
  }

  return (
    <AdminPageShell>
      <AdminPageHeader
        title="Accounts Management"
        action={
          <Button
            type="button"
            onClick={() => {
              setEditingAccount(undefined);
              setIsFormOpen(true);
            }}
          >
            Create Account
          </Button>
        }
      />

      <AdminCard>
        {isLoading ? (
          <div className="py-20 text-center text-slate-500">
            Loading data...
          </div>
        ) : (
          <DataTable columns={columns} data={data} />
        )}
      </AdminCard>

      {deleteDialog}
    </AdminPageShell>
  );
}
