"use client";

import { DataTable } from "@/components/admin/DataTable";
import { StaffForm } from "@/components/admin/StaffForm";
import {
  createStaff,
  deleteStaff,
  listAdminStaff,
  updateStaff,
} from "@/lib/mock/admin-api";
import type { AdminStaff, CreateStaff, UpdateStaff } from "@/types/admin";
import type { ColumnDef } from "@tanstack/react-table";
import { useEffect, useState } from "react";

export default function AdminStaffPage() {
  const [data, setData] = useState<AdminStaff[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingStaff, setEditingStaff] = useState<AdminStaff | undefined>(
    undefined,
  );
  const [isSaving, setIsSaving] = useState(false);

  const fetchStaff = async () => {
    setIsLoading(true);
    try {
      const staff = await listAdminStaff();
      setData(staff);
    } catch (error) {
      console.error("Failed to fetch staff:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchStaff();
  }, []);

  const handleEdit = (staff: AdminStaff) => {
    setEditingStaff(staff);
    setIsFormOpen(true);
  };

  const handleDelete = async (staffId: number) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this staff member? This action cannot be undone.",
      )
    )
      return;
    try {
      await deleteStaff(staffId);
      await fetchStaff();
    } catch (error) {
      console.error("Failed to delete staff:", error);
      alert("Failed to delete staff member");
    }
  };

  const handleFormSubmit = async (formData: CreateStaff | UpdateStaff) => {
    setIsSaving(true);
    try {
      if (editingStaff) {
        await updateStaff(editingStaff.id, formData as UpdateStaff);
      } else {
        await createStaff(formData as CreateStaff);
      }
      setIsFormOpen(false);
      setEditingStaff(undefined);
      fetchStaff();
    } catch (error) {
      console.error("Failed to save staff:", error);
      alert("Failed to save staff member");
    } finally {
      setIsSaving(false);
    }
  };

  const columns: ColumnDef<AdminStaff>[] = [
    {
      accessorKey: "display_order",
      header: "Order",
      cell: ({ row }) => (
        <span className="text-gray-500 text-sm">
          {row.getValue("display_order")}
        </span>
      ),
    },
    {
      id: "name",
      header: "Name",
      cell: ({ row }) => `${row.original.first_name} ${row.original.last_name}`,
    },
    {
      accessorKey: "title",
      header: "Title",
    },
    {
      accessorKey: "email",
      header: "Email",
    },
    {
      accessorKey: "is_active",
      header: "Status",
      cell: ({ row }) => {
        const isActive = row.getValue("is_active") as boolean;
        return (
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium ${isActive ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-600"}`}
          >
            {isActive ? "Active" : "Inactive"}
          </span>
        );
      },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const staff = row.original;
        return (
          <div className="flex gap-4">
            <button
              onClick={() => handleEdit(staff)}
              className="text-blue-600 hover:text-blue-900 font-medium"
            >
              Edit
            </button>
            <button
              onClick={() => handleDelete(staff.id)}
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
      <div className="max-w-2xl mx-auto space-y-4">
        <button
          onClick={() => {
            setIsFormOpen(false);
            setEditingStaff(undefined);
          }}
          className="text-blue-600 hover:underline mb-4 inline-block font-medium"
        >
          &larr; Back to Staff Table
        </button>
        <StaffForm
          initialData={editingStaff}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setIsFormOpen(false);
            setEditingStaff(undefined);
          }}
          isLoading={isSaving}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Staff Management</h1>
        <button
          onClick={() => {
            setEditingStaff(undefined);
            setIsFormOpen(true);
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700 transition"
        >
          Add Staff Member
        </button>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        {isLoading ? (
          <div className="text-center py-20 text-gray-500">
            Loading staff...
          </div>
        ) : (
          <DataTable columns={columns} data={data} />
        )}
      </div>
    </div>
  );
}
