"use client";

import { DataTable } from "@/components/admin/DataTable";
import { LeadershipForm } from "@/components/admin/LeadershipForm";
import {
  createLeadership,
  deleteLeadership,
  getAdminLeadership,
  updateLeadership,
} from "@/lib/mock/admin-api";
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
                : "bg-gray-100 text-gray-700"
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
          <div className="flex gap-4">
            <button
              onClick={() => handleEdit(leadership)}
              className="text-blue-600 hover:text-blue-900 font-medium"
            >
              Edit
            </button>
            <button
              onClick={() => handleDelete(leadership.id)}
              className="text-red-600 hover:text-red-900 font-medium"
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
      <div className="max-w-4xl mx-auto space-y-4">
        <button
          onClick={() => {
            setIsFormOpen(false);
            setEditingLeadership(undefined);
          }}
          className="text-blue-600 hover:underline mb-4 inline-block font-medium"
        >
          &larr; Back to Leadership Table
        </button>
        <LeadershipForm
          initialData={editingLeadership}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setIsFormOpen(false);
            setEditingLeadership(undefined);
          }}
          isLoading={isSaving}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Leadership Management</h1>
        <button
          onClick={() => {
            setEditingLeadership(undefined);
            setIsFormOpen(true);
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700 transition"
        >
          Add Leadership
        </button>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        {isLoading ? (
          <div className="text-center py-20 text-gray-500">
            Loading leadership entries...
          </div>
        ) : (
          <DataTable columns={columns} data={data} />
        )}
      </div>
    </div>
  );
}
