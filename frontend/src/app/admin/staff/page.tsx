"use client";

import {
  AdminBackButton,
  AdminCard,
  AdminPageHeader,
  AdminPageShell,
} from "@/components/admin/AdminPageShell";
import { DataTable } from "@/components/admin/DataTable";
import { StaffForm } from "@/components/admin/StaffForm";
import { Button } from "@/components/ui/button";
import {
  createStaff,
  deleteStaff,
  listAdminStaff,
  updateStaff,
} from "@/lib/admin-api";
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
      <AdminPageShell className="max-w-3xl">
        <AdminBackButton
          onClick={() => {
            setIsFormOpen(false);
            setEditingStaff(undefined);
          }}
          label="Back to Staff Table"
        />
        <StaffForm
          initialData={editingStaff}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setIsFormOpen(false);
            setEditingStaff(undefined);
          }}
          isLoading={isSaving}
        />
      </AdminPageShell>
    );
  }

  return (
    <AdminPageShell>
      <AdminPageHeader
        title="Staff Management"
        action={
          <Button
            type="button"
            onClick={() => {
              setEditingStaff(undefined);
              setIsFormOpen(true);
            }}
          >
            Add Staff Member
          </Button>
        }
      />

      <AdminCard>
        {isLoading ? (
          <div className="py-20 text-center text-slate-500">
            Loading staff...
          </div>
        ) : (
          <DataTable columns={columns} data={data} />
        )}
      </AdminCard>
    </AdminPageShell>
  );
}
