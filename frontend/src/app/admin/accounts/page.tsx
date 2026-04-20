"use client";

import { AccountForm } from "@/components/admin/AccountForm";
import { DataTable } from "@/components/admin/DataTable";
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
  getMe,
  listAdminAccounts,
  updateAccount,
} from "@/lib/admin-api";
import type { Account, CreateAccount } from "@/types/admin";
import type { ColumnDef } from "@tanstack/react-table";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

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

  const handleDelete = async (accountId: number) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this account? This action cannot be undone.",
      )
    )
      return;
    try {
      await deleteAccount(accountId);
      await fetchAccounts();
    } catch (error) {
      console.error("Failed to delete account:", error);
      alert("Failed to delete account");
    }
  };

  const handleFormSubmit = async (formData: CreateAccount) => {
    setIsSaving(true);
    try {
      if (editingAccount) {
        await updateAccount(editingAccount.id, formData);
      } else {
        await createAccount(formData);
      }
      setIsFormOpen(false);
      setEditingAccount(undefined);
      fetchAccounts();
    } catch (error) {
      console.error("Failed to save account:", error);
      alert("Failed to save account. The email or PID may already be in use.");
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
      accessorKey: "pid",
      header: "PID",
      cell: ({ row }) => (
        <span className="font-mono text-sm">{row.getValue("pid")}</span>
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
                onClick={() => handleDelete(account.id)}
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
    </AdminPageShell>
  );
}
