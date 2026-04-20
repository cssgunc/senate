"use client";

import {
  AdminBackButton,
  AdminCard,
  AdminPageHeader,
  AdminPageShell,
} from "@/components/admin/AdminPageShell";
import { DataTable } from "@/components/admin/DataTable";
import { LegislationForm } from "@/components/admin/LegislationForm";
import { Button } from "@/components/ui/button";
import {
  createLegislation,
  deleteLegislation,
  updateLegislation,
} from "@/lib/admin-api";
import { getLegislation } from "@/lib/api";
import type { Legislation } from "@/types";
import type { CreateLegislation } from "@/types/admin";
import type { ColumnDef } from "@tanstack/react-table";
import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

export default function AdminLegislationPage() {
  const ADMIN_LEGISLATION_PAGE_SIZE = 100;
  const [data, setData] = useState<Legislation[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingLegislation, setEditingLegislation] = useState<
    Legislation | undefined
  >();
  const [isSaving, setIsSaving] = useState(false);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    try {
      const firstPage = await getLegislation({
        page: 1,
        limit: ADMIN_LEGISLATION_PAGE_SIZE,
      });

      const allItems = [...firstPage.items];
      const totalPages = Math.ceil(firstPage.total / firstPage.limit);

      for (let page = 2; page <= totalPages; page += 1) {
        const response = await getLegislation({
          page,
          limit: ADMIN_LEGISLATION_PAGE_SIZE,
        });
        allItems.push(...response.items);
      }

      setData(allItems);
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  }, [ADMIN_LEGISLATION_PAGE_SIZE]);

  useEffect(() => {
    void fetchData();
  }, [fetchData]);

  const handleDelete = async (id: number) => {
    if (!window.confirm("Delete this legislation?")) return;
    await deleteLegislation(id);
    await fetchData();
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
      await fetchData();
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
        <div className="flex gap-3">
          <Link
            href={`/admin/legislation/${row.original.id}`}
            className="text-sm font-medium text-slate-700 hover:text-slate-900"
          >
            Details
          </Link>
          <button
            onClick={() => {
              setEditingLegislation(row.original);
              setIsFormOpen(true);
            }}
            className="text-sm font-medium text-blue-700 hover:text-blue-800"
          >
            Edit
          </button>
          <button
            onClick={() => handleDelete(row.original.id)}
            className="text-sm font-medium text-rose-700 hover:text-rose-800"
          >
            Delete
          </button>
        </div>
      ),
    },
  ];

  if (isFormOpen) {
    return (
      <AdminPageShell className="max-w-4xl">
        <AdminBackButton
          onClick={() => setIsFormOpen(false)}
          label="Back to Legislation Table"
        />
        <LegislationForm
          initialData={editingLegislation}
          onSubmit={handleFormSubmit}
          onCancel={() => setIsFormOpen(false)}
          isLoading={isSaving}
        />
      </AdminPageShell>
    );
  }

  return (
    <AdminPageShell>
      <AdminPageHeader
        title="Legislation Management"
        description="Create, edit, and maintain legislation records and metadata."
        action={
          <Button
            type="button"
            onClick={() => {
              setEditingLegislation(undefined);
              setIsFormOpen(true);
            }}
          >
            Add Legislation
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
