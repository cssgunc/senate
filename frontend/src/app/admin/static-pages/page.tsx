"use client";

import {
  AdminBackButton,
  AdminCard,
  AdminPageHeader,
  AdminPageShell,
} from "@/components/admin/AdminPageShell";
import { DataTable } from "@/components/admin/DataTable";
import { StaticPageForm } from "@/components/admin/StaticPageForm";
import { listStaticPages, updateStaticPage } from "@/lib/admin-api";
import type { StaticPage } from "@/types";
import type { UpdateStaticPage } from "@/types/admin";
import type { ColumnDef } from "@tanstack/react-table";
import { format } from "date-fns";
import { useEffect, useState } from "react";

export default function AdminStaticPagesPage() {
  const [data, setData] = useState<StaticPage[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingPage, setEditingPage] = useState<StaticPage | undefined>(
    undefined,
  );
  const [isSaving, setIsSaving] = useState(false);

  const fetchPages = async () => {
    setIsLoading(true);
    try {
      const pages = await listStaticPages();
      setData(pages);
    } catch (error) {
      console.error("Failed to fetch static pages:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPages();
  }, []);

  const handleFormSubmit = async (formData: UpdateStaticPage) => {
    if (!editingPage) return;
    setIsSaving(true);
    try {
      await updateStaticPage(editingPage.page_slug, formData);
      setEditingPage(undefined);
      fetchPages();
    } catch (error) {
      console.error("Failed to save page:", error);
      alert("Failed to save page");
    } finally {
      setIsSaving(false);
    }
  };

  const columns: ColumnDef<StaticPage>[] = [
    {
      accessorKey: "page_slug",
      header: "Slug",
      cell: ({ row }) => (
        <span className="font-mono text-sm bg-gray-100 px-1.5 py-0.5 rounded">
          {row.getValue("page_slug")}
        </span>
      ),
    },
    {
      accessorKey: "title",
      header: "Title",
    },
    {
      accessorKey: "updated_at",
      header: "Last Updated",
      cell: ({ row }) => {
        const date = row.getValue("updated_at") as string;
        try {
          return format(new Date(date), "MMM d, yyyy h:mm a");
        } catch {
          return date;
        }
      },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const page = row.original;
        return (
          <button
            onClick={() => setEditingPage(page)}
            className="text-sm font-medium text-blue-700 hover:text-blue-800"
          >
            Edit
          </button>
        );
      },
    },
  ];

  if (editingPage) {
    return (
      <AdminPageShell className="max-w-4xl">
        <AdminBackButton
          onClick={() => setEditingPage(undefined)}
          label="Back to Pages Table"
        />
        <StaticPageForm
          initialData={editingPage}
          onSubmit={handleFormSubmit}
          onCancel={() => setEditingPage(undefined)}
          isLoading={isSaving}
        />
      </AdminPageShell>
    );
  }

  return (
    <AdminPageShell>
      <AdminPageHeader
        title="Static Pages"
        description="These pages are pre-configured. You can edit content but cannot add or remove pages."
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
