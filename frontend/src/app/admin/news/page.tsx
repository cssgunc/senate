"use client";

import {
  AdminBackButton,
  AdminCard,
  AdminPageHeader,
  AdminPageShell,
} from "@/components/admin/AdminPageShell";
import { DataTable } from "@/components/admin/DataTable";
import { NewsForm } from "@/components/admin/NewsForm";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  createNews,
  deleteNews,
  getAdminNews,
  updateNews,
} from "@/lib/admin-api";
import { AdminNews, CreateNews, UpdateNews } from "@/types/admin";
import { ColumnDef } from "@tanstack/react-table";
import { format } from "date-fns";
import { useEffect, useMemo, useState } from "react";

type StatusFilter = "All" | "Published" | "Draft";
const ADMIN_NEWS_PAGE_SIZE = 100;

export default function AdminNewsPage() {
  const [data, setData] = useState<AdminNews[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("All");

  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingNews, setEditingNews] = useState<AdminNews | undefined>(
    undefined,
  );
  const [isSaving, setIsSaving] = useState(false);

  const fetchNews = async () => {
    setIsLoading(true);
    try {
      const firstPage = await getAdminNews(1, ADMIN_NEWS_PAGE_SIZE);
      if (Array.isArray(firstPage)) {
        setData(firstPage);
        return;
      }

      const allItems = [...firstPage.items];
      const totalPages = Math.ceil(firstPage.total / firstPage.limit);

      for (let page = 2; page <= totalPages; page += 1) {
        const response = await getAdminNews(page, ADMIN_NEWS_PAGE_SIZE);
        if (Array.isArray(response)) {
          allItems.push(...response);
        } else {
          allItems.push(...response.items);
        }
      }

      setData(allItems);
    } catch (error) {
      console.error("Failed to fetch news:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchNews();
  }, []);

  const handleEdit = (news: AdminNews) => {
    setEditingNews(news);
    setIsFormOpen(true);
  };

  const handleDelete = async (newsId: number) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this article? This action cannot be undone.",
      )
    )
      return;
    try {
      await deleteNews(newsId);
      await fetchNews();
    } catch (error) {
      console.error("Failed to delete article:", error);
      alert("Failed to delete article");
    }
  };

  const handleFormSubmit = async (formData: CreateNews | UpdateNews) => {
    setIsSaving(true);
    try {
      if (editingNews) {
        await updateNews(editingNews.id, formData as UpdateNews);
      } else {
        await createNews(formData as CreateNews);
      }
      setIsFormOpen(false);
      setEditingNews(undefined);
      fetchNews();
    } catch (error) {
      console.error("Failed to save article:", error);
      alert("Failed to save article");
    } finally {
      setIsSaving(false);
    }
  };

  const filteredData = useMemo(() => {
    if (statusFilter === "All") return data;
    const isPub = statusFilter === "Published";
    return data.filter((item) => item.is_published === isPub);
  }, [data, statusFilter]);

  const columns: ColumnDef<AdminNews>[] = [
    {
      accessorKey: "title",
      header: "Title",
    },
    {
      accessorKey: "is_published",
      header: "Status",
      cell: ({ row }) => {
        const isPublished = row.getValue("is_published") as boolean;
        return (
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium ${isPublished ? "bg-green-100 text-green-800" : "bg-slate-100 text-slate-700"}`}
          >
            {isPublished ? "Published" : "Draft"}
          </span>
        );
      },
    },
    {
      accessorKey: "admin",
      header: "Author",
      cell: ({ row }) => {
        const admin = row.original.admin;
        return admin ? `${admin.first_name} ${admin.last_name}` : "Unknown";
      },
    },
    {
      accessorKey: "date_published",
      header: "Date Published",
      cell: ({ row }) => {
        const date = row.getValue("date_published") as string;
        try {
          return format(new Date(date), "MMM d, yyyy");
        } catch {
          return date;
        }
      },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const news = row.original;
        return (
          <div className="flex gap-3">
            <button
              onClick={() => handleEdit(news)}
              className="text-sm font-medium text-blue-700 hover:text-blue-800"
            >
              Edit
            </button>
            <button
              onClick={() => handleDelete(news.id)}
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
            setEditingNews(undefined);
          }}
          label="Back to News Table"
        />
        <NewsForm
          initialData={editingNews}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setIsFormOpen(false);
            setEditingNews(undefined);
          }}
          isLoading={isSaving}
        />
      </AdminPageShell>
    );
  }

  return (
    <AdminPageShell>
      <AdminPageHeader
        title="News Management"
        action={
          <Button
            type="button"
            onClick={() => {
              setEditingNews(undefined);
              setIsFormOpen(true);
            }}
          >
            Create Article
          </Button>
        }
      />

      <AdminCard>
        <div className="mb-6 flex items-center gap-3">
          <label className="text-sm font-medium text-slate-700">
            Filter by Status:
          </label>
          <Select
            value={statusFilter}
            onValueChange={(val) => setStatusFilter(val as StatusFilter)}
          >
            <SelectTrigger className="w-36">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="All">All</SelectItem>
              <SelectItem value="Published">Published</SelectItem>
              <SelectItem value="Draft">Draft</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {isLoading ? (
          <div className="py-20 text-center text-slate-500">
            Loading data...
          </div>
        ) : (
          <DataTable columns={columns} data={filteredData} />
        )}
      </AdminCard>
    </AdminPageShell>
  );
}
