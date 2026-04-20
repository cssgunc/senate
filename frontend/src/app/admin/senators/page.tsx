"use client";

import {
  AdminBackButton,
  AdminCard,
  AdminPageHeader,
  AdminPageShell,
} from "@/components/admin/AdminPageShell";
import { DataTable } from "@/components/admin/DataTable";
import { SenatorForm } from "@/components/admin/SenatorForm";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
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
            className={`px-2 py-1 rounded-full text-xs font-medium ${isActive ? "bg-green-100 text-green-800" : "bg-slate-100 text-slate-700"}`}
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
          <div className="flex gap-3">
            <button
              onClick={() => handleEdit(senator)}
              className="text-sm font-medium text-blue-700 hover:text-blue-800"
            >
              Edit
            </button>
            <button
              onClick={() => handleDelete(senator.id)}
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
      <AdminPageShell className="max-w-3xl">
        <AdminBackButton
          onClick={() => {
            setIsFormOpen(false);
            setEditingSenator(undefined);
          }}
          label="Back to Senators Table"
        />
        <SenatorForm
          initialData={editingSenator}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setIsFormOpen(false);
            setEditingSenator(undefined);
          }}
          isLoading={isSaving}
        />
      </AdminPageShell>
    );
  }

  return (
    <AdminPageShell>
      <AdminPageHeader
        title="Senators Management"
        description="Manage the active roster, session assignments, and contact details."
        action={
          <Button
            type="button"
            onClick={() => {
              setEditingSenator(undefined);
              setIsFormOpen(true);
            }}
          >
            Add Senator
          </Button>
        }
      />

      <AdminCard className="space-y-4">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">
              Status
            </label>
            <Select
              value={activeFilter}
              onValueChange={(val) => setActiveFilter(val as ActiveFilter)}
            >
              <SelectTrigger className="w-full">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All</SelectItem>
                <SelectItem value="active">Active</SelectItem>
                <SelectItem value="inactive">Inactive</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-700">
              Session Number
            </label>
            <Input
              type="number"
              min="1"
              value={sessionFilter}
              onChange={(event) => setSessionFilter(event.target.value)}
              placeholder="All sessions"
            />
          </div>

          <div className="flex items-end">
            <Button
              type="button"
              variant="outline"
              onClick={() => {
                setActiveFilter("all");
                setSessionFilter("");
              }}
            >
              Reset Filters
            </Button>
          </div>
        </div>

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
