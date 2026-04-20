"use client";

import { DataTable } from "@/components/admin/DataTable";
import { LegislationForm } from "@/components/admin/LegislationForm";
import {
  createLegislation,
  deleteLegislation,
  updateLegislation,
} from "@/lib/admin-api";
import { getLegislation } from "@/lib/api";
import { Legislation } from "@/types";
import { CreateLegislation } from "@/types/admin";
import { ColumnDef } from "@tanstack/react-table";
import Link from "next/link"; // For linking to details page
import { useEffect, useState } from "react";

export default function AdminLegislationPage() {
  const [data, setData] = useState<Legislation[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingLegislation, setEditingLegislation] = useState<
    Legislation | undefined
  >();
  const [isSaving, setIsSaving] = useState(false);

  // Re-usable fetcher
  const fetchData = async () => {
    setIsLoading(true);
    try {
      const response = await getLegislation();
      // Next line assumes standard pagination response from your API client
      if ("items" in response) {
        setData(response.items);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleDelete = async (id: number) => {
    if (!window.confirm("Delete this legislation?")) return;
    await deleteLegislation(id);
    fetchData();
  };

  const handleFormSubmit = async (formData: CreateLegislation) => {
    setIsSaving(true);
    try {
      if (editingLegislation) {
        await updateLegislation(editingLegislation.id, formData);
      } else {
        await createLegislation(formData);
      }
      setIsFormOpen(false);
      fetchData();
    } catch (err) {
      console.error(err);
      alert("Failed to save.");
    } finally {
      setIsSaving(false);
    }
  };

  // Define Table Columns
  const columns: ColumnDef<Legislation>[] = [
    { accessorKey: "bill_number", header: "Bill Number" },
    { accessorKey: "title", header: "Title" },
    { accessorKey: "status", header: "Status" },
    { accessorKey: "type", header: "Type" },
    { accessorKey: "session_number", header: "Session" },
    { accessorKey: "sponsor_name", header: "Sponsor" },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => (
        <div className="flex gap-4">
          <Link
            href={`/admin/legislation/${row.original.id}`}
            className="text-gray-600 hover:text-black"
          >
            View Details & Actions
          </Link>
          <button
            onClick={() => {
              setEditingLegislation(row.original);
              setIsFormOpen(true);
            }}
            className="text-blue-600 hover:underline"
          >
            Edit
          </button>
          <button
            onClick={() => handleDelete(row.original.id)}
            className="text-red-600 hover:underline"
          >
            Delete
          </button>
        </div>
      ),
    },
  ];

  if (isFormOpen) {
    return (
      <div className="space-y-4">
        <button onClick={() => setIsFormOpen(false)} className="text-blue-600">
          &larr; Back
        </button>
        <LegislationForm
          initialData={editingLegislation}
          onSubmit={handleFormSubmit}
          onCancel={() => setIsFormOpen(false)}
          isLoading={isSaving}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Legislation Management</h1>
        <button
          onClick={() => {
            setEditingLegislation(undefined);
            setIsFormOpen(true);
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded"
        >
          Add Legislation
        </button>
      </div>

      <div className="bg-white p-6 rounded shadow-sm border border-gray-200">
        {isLoading ? (
          <p>Loading...</p>
        ) : (
          <DataTable columns={columns} data={data} />
        )}
      </div>
    </div>
  );
}
