"use client";

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
            className="text-blue-600 hover:text-blue-900 font-medium"
          >
            Edit
          </button>
        );
      },
    },
  ];

  if (editingPage) {
    return (
      <div className="max-w-4xl mx-auto space-y-4">
        <button
          onClick={() => setEditingPage(undefined)}
          className="text-blue-600 hover:underline mb-4 inline-block font-medium"
        >
          &larr; Back to Pages Table
        </button>
        <StaticPageForm
          initialData={editingPage}
          onSubmit={handleFormSubmit}
          onCancel={() => setEditingPage(undefined)}
          isLoading={isSaving}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold">Static Pages</h1>
          <p className="text-sm text-gray-500 mt-1">
            These pages are pre-configured. You can edit their content but not
            add or remove them.
          </p>
        </div>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        {isLoading ? (
          <div className="text-center py-20 text-gray-500">
            Loading pages...
          </div>
        ) : (
          <DataTable columns={columns} data={data} />
        )}
      </div>
    </div>
  );
}
