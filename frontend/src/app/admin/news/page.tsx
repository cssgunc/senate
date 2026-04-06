"use client";

import { useEffect, useState, useMemo } from "react";
import { getAdminNews, createNews, updateNews, deleteNews } from "@/lib/admin-api";
import { AdminNews, CreateNews, UpdateNews } from "@/types/admin";
import { DataTable } from "@/components/admin/DataTable";
import { NewsForm } from "@/components/admin/NewsForm";
import { ColumnDef } from "@tanstack/react-table";
import { format } from "date-fns";

type StatusFilter = "All" | "Published" | "Draft";

export default function AdminNewsPage() {
  const [data, setData] = useState<AdminNews[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("All");
  
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingNews, setEditingNews] = useState<AdminNews | undefined>(undefined);
  const [isSaving, setIsSaving] = useState(false);

  const fetchNews = async () => {
    setIsLoading(true);
    try {
      const res = await getAdminNews(1, 100);
      if (res && res.items) {
        setData(res.items);
      } else if (Array.isArray(res)) {
        setData(res);
      } else {
        setData([]); // fallback
      }
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
    if (!window.confirm("Are you sure you want to delete this article? This action cannot be undone.")) return;
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
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${isPublished ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
            {isPublished ? "Published" : "Draft"}
          </span>
        );
      }
    },
    {
      accessorKey: "admin",
      header: "Author",
      cell: ({ row }) => {
        const admin = row.original.admin;
        return admin ? `${admin.first_name} ${admin.last_name}` : "Unknown";
      }
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
      }
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const news = row.original;
        return (
          <div className="flex gap-4">
            <button
              onClick={() => handleEdit(news)}
              className="text-blue-600 hover:text-blue-900 font-medium"
            >
              Edit
            </button>
            <button
              onClick={() => handleDelete(news.id)}
              className="text-red-600 hover:text-red-900 font-medium"
            >
              Delete
            </button>
          </div>
        );
      }
    }
  ];

  if (isFormOpen) {
    return (
      <div className="max-w-4xl mx-auto space-y-4">
        <button
           onClick={() => {
             setIsFormOpen(false);
             setEditingNews(undefined);
           }}
           className="text-blue-600 hover:underline mb-4 inline-block font-medium"
        >
          &larr; Back to News Table
        </button>
        <NewsForm 
          initialData={editingNews} 
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setIsFormOpen(false);
            setEditingNews(undefined);
          }}
          isLoading={isSaving}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">News Management</h1>
        <button
          onClick={() => {
            setEditingNews(undefined);
            setIsFormOpen(true);
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700 transition"
        >
          Create Article
        </button>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <div className="mb-6 flex items-center gap-3">
          <label className="text-sm font-medium text-gray-700">Filter by Status:</label>
          <select 
            className="border border-gray-300 rounded-md py-1.5 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as StatusFilter)}
          >
            <option value="All">All</option>
            <option value="Published">Published</option>
            <option value="Draft">Draft</option>
          </select>
        </div>

        {isLoading ? (
          <div className="text-center py-20 text-gray-500">Loading news...</div>
        ) : (
          <DataTable columns={columns} data={filteredData} />
        )}
      </div>
    </div>
  );
}
