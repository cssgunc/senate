"use client";

import { DataTable } from "@/components/admin/DataTable";
import { SenatorForm } from "@/components/admin/SenatorForm";
import {
  createSenator,
  deleteSenator,
  getAdminSenators,
  updateSenator,
} from "@/lib/admin-api";
import { getDistricts } from "@/lib/api";
import type { District, Senator } from "@/types";
import type { CreateSenator, UpdateSenator } from "@/types/admin";
import type { ColumnDef } from "@tanstack/react-table";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";

const ADMIN_SENATORS_PAGE_SIZE = 100;

type ActiveFilter = "all" | "active" | "inactive";

export default function AdminSenatorsPage() {
  const [data, setData] = useState<Senator[]>([]);
  const [districts, setDistricts] = useState<District[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingSenator, setEditingSenator] = useState<Senator | undefined>(
    undefined,
  );
  const [isSaving, setIsSaving] = useState(false);
  const [activeFilter, setActiveFilter] = useState<ActiveFilter>("all");
  const [sessionFilter, setSessionFilter] = useState("");
  const latestFetchRequestId = useRef(0);

  const loadDistricts = async () => {
    try {
      const response = await getDistricts();
      setDistricts(response);
    } catch (error) {
      console.error("Failed to fetch districts:", error);
    }
  };

  const fetchSenators = useCallback(async () => {
    const requestId = ++latestFetchRequestId.current;
    setIsLoading(true);
    try {
      const parsedSession = sessionFilter.trim()
        ? Number(sessionFilter.trim())
        : undefined;
      const session =
        parsedSession !== undefined && Number.isFinite(parsedSession)
          ? parsedSession
          : undefined;
      const isActive =
        activeFilter === "active"
          ? true
          : activeFilter === "inactive"
            ? false
            : undefined;

      const firstPage = await getAdminSenators(
        1,
        ADMIN_SENATORS_PAGE_SIZE,
        isActive,
        session,
      );

      if (Array.isArray(firstPage)) {
        if (requestId === latestFetchRequestId.current) {
          setData(firstPage);
        }
        return;
      }

      const allItems = [...firstPage.items];
      const totalPages = Math.ceil(firstPage.total / firstPage.limit);
      for (let page = 2; page <= totalPages; page += 1) {
        if (requestId !== latestFetchRequestId.current) {
          return;
        }

        const response = await getAdminSenators(
          page,
          ADMIN_SENATORS_PAGE_SIZE,
          isActive,
          session,
        );
        if (Array.isArray(response)) {
          allItems.push(...response);
        } else {
          allItems.push(...response.items);
        }
      }

      if (requestId === latestFetchRequestId.current) {
        setData(allItems);
      }
    } catch (error) {
      if (requestId === latestFetchRequestId.current) {
        console.error("Failed to fetch senators:", error);
      }
    } finally {
      if (requestId === latestFetchRequestId.current) {
        setIsLoading(false);
      }
    }
  }, [activeFilter, sessionFilter]);

  useEffect(() => {
    void loadDistricts();
  }, []);

  useEffect(() => {
    void fetchSenators();
  }, [fetchSenators]);

  const districtById = useMemo(() => {
    return new Map(districts.map((district) => [district.id, district]));
  }, [districts]);

  const handleEdit = (senator: Senator) => {
    setEditingSenator(senator);
    setIsFormOpen(true);
  };

  const handleDelete = async (senatorId: number) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this senator? This action cannot be undone.",
      )
    ) {
      return;
    }

    try {
      await deleteSenator(senatorId);
      await fetchSenators();
    } catch (error) {
      const message = error instanceof Error ? error.message : String(error);
      if (message.includes("409")) {
        alert(
          "Cannot delete this senator because linked leadership entries still exist.",
        );
      } else {
        alert("Failed to delete senator");
      }
      console.error("Failed to delete senator:", error);
    }
  };

  const handleFormSubmit = async (formData: CreateSenator | UpdateSenator) => {
    setIsSaving(true);
    try {
      if (editingSenator) {
        await updateSenator(editingSenator.id, formData as UpdateSenator);
      } else {
        await createSenator(formData as CreateSenator);
      }
      setIsFormOpen(false);
      setEditingSenator(undefined);
      await fetchSenators();
    } catch (error) {
      console.error("Failed to save senator:", error);
      alert("Failed to save senator");
    } finally {
      setIsSaving(false);
    }
  };

  const columns: ColumnDef<Senator>[] = [
    {
      id: "name",
      header: "Name",
      cell: ({ row }) => `${row.original.first_name} ${row.original.last_name}`,
    },
    {
      accessorKey: "email",
      header: "Email",
    },
    {
      accessorKey: "district_id",
      header: "District",
      cell: ({ row }) => {
        const district = districtById.get(row.original.district_id);
        return (
          district?.district_name ?? `District ${row.original.district_id}`
        );
      },
    },
    {
      accessorKey: "session_number",
      header: "Session",
    },
    {
      accessorKey: "is_active",
      header: "Active",
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
        const senator = row.original;
        return (
          <div className="flex gap-4">
            <button
              onClick={() => handleEdit(senator)}
              className="text-blue-600 hover:text-blue-900 font-medium"
            >
              Edit
            </button>
            <button
              onClick={() => handleDelete(senator.id)}
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
            setEditingSenator(undefined);
          }}
          className="text-blue-600 hover:underline mb-4 inline-block font-medium"
        >
          &larr; Back to Senators Table
        </button>
        <SenatorForm
          initialData={editingSenator}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setIsFormOpen(false);
            setEditingSenator(undefined);
          }}
          isLoading={isSaving}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Senators Management</h1>
          <p className="text-sm text-gray-500 mt-1">
            Manage the active roster, session assignments, and contact details.
          </p>
        </div>
        <button
          onClick={() => {
            setEditingSenator(undefined);
            setIsFormOpen(true);
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700 transition"
        >
          Add Senator
        </button>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200 space-y-4">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              className="w-full border border-gray-300 rounded-md py-2 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
              value={activeFilter}
              onChange={(event) =>
                setActiveFilter(event.target.value as ActiveFilter)
              }
            >
              <option value="all">All</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Session Number
            </label>
            <input
              type="number"
              min="1"
              className="w-full border border-gray-300 rounded-md py-2 px-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              value={sessionFilter}
              onChange={(event) => setSessionFilter(event.target.value)}
              placeholder="All sessions"
            />
          </div>

          <div className="flex items-end">
            <button
              type="button"
              onClick={() => {
                setActiveFilter("all");
                setSessionFilter("");
              }}
              className="w-full md:w-auto border border-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-50"
            >
              Reset Filters
            </button>
          </div>
        </div>

        {isLoading ? (
          <div className="text-center py-20 text-gray-500">
            Loading senators...
          </div>
        ) : (
          <DataTable columns={columns} data={data} />
        )}
      </div>
    </div>
  );
}
