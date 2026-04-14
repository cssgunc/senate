"use client";

import { CalendarEventForm } from "@/components/admin/CalendarEventForm";
import { DataTable } from "@/components/admin/DataTable";
import { CalendarEvent } from "@/types";
import { CreateCalendarEvent } from "@/types/admin";
import {
  createCalendarEvent,
  deleteCalendarEvent,
  getAdminEvents,
  updateCalendarEvent,
} from "@/lib/admin-api";
import { ColumnDef } from "@tanstack/react-table";
import { format } from "date-fns";
import { useEffect, useState } from "react";

export default function AdminEventsPage() {
  const [data, setData] = useState<CalendarEvent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [editingEvent, setEditingEvent] = useState<CalendarEvent | undefined>(
    undefined,
  );
  const [isSaving, setIsSaving] = useState(false);

  const fetchEvents = async () => {
    setIsLoading(true);
    try {
      const response = await getAdminEvents();
      setData(Array.isArray(response) ? response : []);
    } catch (error) {
      console.error("Failed to fetch events:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, []);

  const handleEdit = (event: CalendarEvent) => {
    setEditingEvent(event);
    setIsFormOpen(true);
  };

  const handleDelete = async (eventId: number) => {
    if (
      !window.confirm(
        "Are you sure you want to delete this event? This action cannot be undone.",
      )
    )
      return;
    try {
      await deleteCalendarEvent(eventId);
      fetchEvents();
    } catch (error) {
      console.error("Failed to delete event:", error);
      alert("Failed to delete event");
    }
  };

  const handleFormSubmit = async (formData: CreateCalendarEvent) => {
    setIsSaving(true);
    try {
      if (editingEvent) {
        await updateCalendarEvent(editingEvent.id, formData);
      } else {
        await createCalendarEvent(formData);
      }
      setIsFormOpen(false);
      setEditingEvent(undefined);
      fetchEvents();
    } catch (error) {
      console.error("Failed to save event:", error);
      alert("Failed to save event");
    } finally {
      setIsSaving(false);
    }
  };

  const columns: ColumnDef<CalendarEvent>[] = [
    {
      accessorKey: "title",
      header: "Title",
    },
    {
      accessorKey: "start_datetime",
      header: "Date/Time",
      cell: ({ row }) => {
        const start = new Date(row.original.start_datetime);
        const end = new Date(row.original.end_datetime);
        try {
          return `${format(start, "MMM d, yyyy h:mm a")} - ${format(
            end,
            "h:mm a",
          )}`;
        } catch {
          return row.original.start_datetime;
        }
      },
    },
    {
      accessorKey: "location",
      header: "Location",
      cell: ({ row }) => row.getValue("location") || "TBA",
    },
    {
      accessorKey: "event_type",
      header: "Type",
    },
    {
      accessorKey: "is_published",
      header: "Status",
      cell: ({ row }) => {
        const isPublished = row.getValue("is_published") as boolean;
        return (
          <span
            className={`px-2 py-1 rounded-full text-xs font-medium ${
              isPublished
                ? "bg-green-100 text-green-800"
                : "bg-yellow-100 text-yellow-800"
            }`}
          >
            {isPublished ? "Published" : "Draft"}
          </span>
        );
      },
    },
    {
      id: "actions",
      header: "Actions",
      cell: ({ row }) => {
        const event = row.original;
        return (
          <div className="flex gap-4">
            <button
              onClick={() => handleEdit(event)}
              className="text-blue-600 hover:text-blue-900 font-medium"
            >
              Edit
            </button>
            <button
              onClick={() => handleDelete(event.id)}
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
      <div className="max-w-4xl mx-auto space-y-4">
        <button
          onClick={() => {
            setIsFormOpen(false);
            setEditingEvent(undefined);
          }}
          className="text-blue-600 hover:underline mb-4 inline-block font-medium"
        >
          &larr; Back to Events Table
        </button>
        <CalendarEventForm
          initialData={editingEvent}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setIsFormOpen(false);
            setEditingEvent(undefined);
          }}
          isLoading={isSaving}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Events Management</h1>
        <button
          onClick={() => {
            setEditingEvent(undefined);
            setIsFormOpen(true);
          }}
          className="bg-blue-600 text-white px-4 py-2 rounded shadow hover:bg-blue-700 transition"
        >
          Create Event
        </button>
      </div>

      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        {isLoading ? (
          <div className="text-center py-20 text-gray-500">Loading events...</div>
        ) : (
          <DataTable columns={columns} data={data} />
        )}
      </div>
    </div>
  );
}
