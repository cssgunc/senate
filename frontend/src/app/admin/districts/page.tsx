"use client";

import { DataTable } from "@/components/admin/DataTable";
import { DistrictForm } from "@/components/admin/DistrictForm";
import {
  createDistrict,
  deleteDistrict,
  listAdminDistricts,
  updateDistrict,
} from "@/lib/mock/admin-api";
import type {
  AdminDistrict,
  CreateDistrict,
  UpdateDistrict,
} from "@/types/admin";
import type { ColumnDef } from "@tanstack/react-table";
import { useEffect, useState } from "react";

export default function AdminDistrictsPage() {
  const [data, setData] = useState<AdminDistrict[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingDistrict, setEditingDistrict] = useState<
    AdminDistrict | undefined
  >(undefined);
  const [isSaving, setIsSaving] = useState(false);

  const fetchDistricts = async () => {
    setIsLoading(true);
    try {
      const districts = await listAdminDistricts();
      setData(districts);
    } catch (error) {
      console.error("Failed to fetch districts:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDistricts();
  }, []);

  const handleEdit = (district: AdminDistrict) => {
    setEditingDistrict(district);
    setIsFormOpen(true);
  };

  const handleDelete = async (districtId: number) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this district? This will fail if senators are still assigned to it.",
      )
    )
      return;
    try {
      await deleteDistrict(districtId);
      await fetchDistricts();
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      if (message.includes("409")) {
        alert(
          "Cannot delete this district — senators are still assigned to it. Reassign or delete them first.",
        );
      } else {
        alert("Failed to delete district");
      }
      console.error("Failed to delete district:", error);
    }
  };

  const handleFormSubmit = async (
    formData: CreateDistrict | UpdateDistrict,
  ) => {
    setIsSaving(true);
    try {
      if (editingDistrict) {
        await updateDistrict(editingDistrict.id, formData as UpdateDistrict);
      } else {
        await createDistrict(formData as CreateDistrict);
      }
      setIsFormOpen(false);
      setEditingDistrict(undefined);
      fetchDistricts();
    } catch (error) {
      console.error("Failed to save district:", error);
      alert("Failed to save district");
    } finally {
      setIsSaving(false);
    }
  };

  const columns: ColumnDef<AdminDistrict>[] = [
    {
      accessorKey: "district_name",
      header: "District Name",
    },
    {
      accessorKey: "description",
      header: "Description",
      cell: ({ row }) => {
        const desc = row.getValue("description") as string | null;
        return desc ? (
          <span className="text-gray-700">{desc}</span>
        ) : (
          <span className="text-gray-400 italic">No description</span>
        );
      },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const district = row.original;
        return (
          <div className="flex gap-4">
            <button
              onClick={() => handleEdit(district)}
              className="text-blue-600 hover:text-blue-900 font-medium"
            >
              Edit
            </button>
            <button
              onClick={() => handleDelete(district.id)}
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
            setEditingDistrict(undefined);
          }}
          className="text-blue-600 hover:underline mb-4 inline-block font-medium"
        >
          &larr; Back to Districts Table
        </button>
        <DistrictForm
          initialData={editingDistrict}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setIsFormOpen(false);
            setEditingDistrict(undefined);
          }}
          isLoading={isSaving}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Districts Management</h1>
        <button
          onClick={() => {
            setEditingDistrict(undefined);
            setIsFormOpen(true);
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700 transition"
        >
          Add District
        </button>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        {isLoading ? (
          <div className="text-center py-20 text-gray-500">
            Loading districts...
          </div>
        ) : (
          <DataTable columns={columns} data={data} />
        )}
      </div>
    </div>
  );
}
