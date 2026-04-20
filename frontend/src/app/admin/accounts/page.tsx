"use client";

import { DataTable } from "@/components/admin/DataTable";
import { AccountForm } from "@/components/admin/AccountForm";
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
      cell: ({ row }) =>
        `${row.original.first_name} ${row.original.last_name}`,
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
          <div className="flex gap-4">
            <button
              onClick={() => handleEdit(account)}
              className="text-blue-600 hover:text-blue-900 font-medium"
            >
              Edit
            </button>
            {!isSelf && (
              <button
                onClick={() => handleDelete(account.id)}
                className="text-red-600 hover:text-red-900 font-medium"
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
      <div className="max-w-2xl mx-auto space-y-4">
        <button
          onClick={() => {
            setIsFormOpen(false);
            setEditingAccount(undefined);
          }}
          className="text-blue-600 hover:underline mb-4 inline-block font-medium"
        >
          &larr; Back to Accounts Table
        </button>
        <AccountForm
          initialData={editingAccount}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setIsFormOpen(false);
            setEditingAccount(undefined);
          }}
          isLoading={isSaving}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Accounts Management</h1>
        <button
          onClick={() => {
            setEditingAccount(undefined);
            setIsFormOpen(true);
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700 transition"
        >
          Create Account
        </button>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        {isLoading ? (
          <div className="text-center py-20 text-gray-500">
            Loading accounts...
          </div>
        ) : (
          <DataTable columns={columns} data={data} />
        )}
      </div>
    </div>
  );
}
