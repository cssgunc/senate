"use client";

import {
  AdminBackButton,
  AdminCard,
  AdminPageHeader,
  AdminPageShell,
} from "@/components/admin/AdminPageShell";
import { DataTable } from "@/components/admin/DataTable";
import { LeadershipForm } from "@/components/admin/LeadershipForm";
import { Button } from "@/components/ui/button";
import {
  createLeadership,
  deleteLeadership,
  getAdminLeadership,
  updateLeadership,
} from "@/lib/admin-api";
import {
  AdminLeadership,
  CreateLeadership,
  UpdateLeadership,
} from "@/types/admin";
import { ColumnDef, Row } from "@tanstack/react-table";
import { useEffect, useState } from "react";

const ADMIN_LEADERSHIP_PAGE_SIZE = 100;

export default function AdminLeadershipPage() {
  const [data, setData] = useState<AdminLeadership[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingLeadership, setEditingLeadership] = useState<
    AdminLeadership | undefined
  >(undefined);
  const [isSaving, setIsSaving] = useState(false);

  const fetchLeadership = async () => {
    setIsLoading(true);

    try {
      const firstPage = await getAdminLeadership(1, ADMIN_LEADERSHIP_PAGE_SIZE);
      if (Array.isArray(firstPage)) {
        setData(firstPage);
        return;
      }

      const allItems = [...firstPage.items];
      const totalPages = Math.ceil(firstPage.total / firstPage.limit);
      for (let page = 2; page <= totalPages; page += 1) {
        const response = await getAdminLeadership(
          page,
          ADMIN_LEADERSHIP_PAGE_SIZE,
        );
        if (Array.isArray(response)) {
          allItems.push(...response);
        } else {
          allItems.push(...response.items);
        }
      }
      setData(allItems);
    } catch (error) {
      console.error("Failed to fetch leadership entries:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchLeadership();
  }, []);

  const handleEdit = (leadership: AdminLeadership) => {
    setEditingLeadership(leadership);
    setIsFormOpen(true);
  };

  const handleDelete = async (leadershipId: number) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this leadership entry? This action cannot be undone.",
      )
    ) {
      return;
    }

    try {
      await deleteLeadership(leadershipId);
      await fetchLeadership();
    } catch (error) {
      console.error("Failed to delete leadership entry:", error);
      alert("Failed to delete leadership entry");
    }
  };

  const handleFormSubmit = async (
    formData: CreateLeadership | UpdateLeadership,
  ) => {
    setIsSaving(true);
    try {
      if (editingLeadership) {
        await updateLeadership(
          editingLeadership.id,
          formData as UpdateLeadership,
        );
      } else {
        await createLeadership(formData as CreateLeadership);
      }
      setIsFormOpen(false);
      setEditingLeadership(undefined);
      await fetchLeadership();
    } catch (error) {
      console.error("Failed to save leadership entry:", error);
      alert("Failed to save leadership entry");
    } finally {
      setIsSaving(false);
    }
  };

  const columns: ColumnDef<AdminLeadership, any>[] = [
    {
      accessorKey: "title",
      header: "Title",
    },
    {
      id: "name",
      header: "Name",
      cell: ({ row }: { row: Row<AdminLeadership> }) => {
        const leadership = row.original;
        return `${leadership.first_name} ${leadership.last_name}`;
      },
    },
    {
      accessorKey: "email",
      header: "Email",
    },
    {
      accessorKey: "session_number",
      header: "Session",
    },
    {
      accessorKey: "is_current",
      header: "Active",
      cell: ({ row }: { row: Row<AdminLeadership> }) => {
        const isCurrent = row.getValue("is_current") as boolean;
        return (
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium ${
              isCurrent
                ? "bg-green-100 text-green-800"
                : "bg-slate-100 text-slate-700"
            }`}
          >
            {isCurrent ? "Active" : "Inactive"}
          </span>
        );
      },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }: { row: Row<AdminLeadership> }) => {
        const leadership = row.original;
        return (
          <div className="flex gap-3">
            <button
              onClick={() => handleEdit(leadership)}
              className="text-sm font-medium text-blue-700 hover:text-blue-800"
            >
              Edit
            </button>
            <button
              onClick={() => handleDelete(leadership.id)}
              className="text-sm font-medium text-rose-700 hover:text-rose-800"
            >
              Delete
            </button>
          </div>
        );
      },
    },
  ];

  if (isFormOpen) {
    return (
      <AdminPageShell className="max-w-4xl">
        <AdminBackButton
          onClick={() => {
            setIsFormOpen(false);
            setEditingLeadership(undefined);
          }}
          label="Back to Leadership Table"
        />
        <LeadershipForm
          initialData={editingLeadership}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setIsFormOpen(false);
            setEditingLeadership(undefined);
          }}
          isLoading={isSaving}
        />
      </AdminPageShell>
    );
  }

  return (
    <AdminPageShell>
      <AdminPageHeader
        title="Leadership Management"
        action={
          <Button
            type="button"
            onClick={() => {
              setEditingLeadership(undefined);
              setIsFormOpen(true);
            }}
          >
            Add Leadership
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
