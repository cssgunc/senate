"use client";

import type { CalendarEvent } from "@/types";
import type { CreateCalendarEvent } from "@/types/admin";
import { useState } from "react";

interface CalendarEventFormProps {
  initialData?: CalendarEvent;
  onSubmit: (data: CreateCalendarEvent) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function CalendarEventForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading,
}: CalendarEventFormProps) {
  const [formData, setFormData] = useState<CreateCalendarEvent>({
    title: initialData?.title || "",
    description: initialData?.description || "",
    start_datetime: initialData?.start_datetime
      ? initialData.start_datetime.slice(0, 16)
      : "",
    end_datetime: initialData?.end_datetime
      ? initialData.end_datetime.slice(0, 16)
      : "",
    location: initialData?.location || "",
    event_type: initialData?.event_type || "Senate Meeting",
    is_published: initialData?.is_published ?? false,
  });

  const handleChange = (
    e: React.ChangeEvent<
      HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement
    >,
  ) => {
    const { name, value, type } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]:
        type === "checkbox" ? (e.target as HTMLInputElement).checked : value,
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.title || !formData.start_datetime || !formData.end_datetime) {
      alert("Please fill in all required fields.");
      return;
    }
    onSubmit({
      ...formData,
      // Formatting datetime-local value to ISO string format for backend
      start_datetime: new Date(formData.start_datetime).toISOString(),
      end_datetime: new Date(formData.end_datetime).toISOString(),
    });
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h2 className="text-xl font-bold mb-6">
        {initialData ? "Edit Event" : "Create Event"}
      </h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2 md:col-span-2">
            <label className="block text-sm font-medium text-gray-700">
              Title *
            </label>
            <input
              type="text"
              name="title"
              required
              value={formData.title}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. Full Senate Meeting"
            />
          </div>

          <div className="space-y-2 md:col-span-2">
            <label className="block text-sm font-medium text-gray-700">
              Description
            </label>
            <textarea
              name="description"
              value={formData.description || ""}
              onChange={handleChange}
              rows={4}
              className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Event details..."
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Start Date & Time *
            </label>
            <input
              type="datetime-local"
              name="start_datetime"
              required
              value={formData.start_datetime}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              End Date & Time *
            </label>
            <input
              type="datetime-local"
              name="end_datetime"
              required
              value={formData.end_datetime}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Location
            </label>
            <input
              type="text"
              name="location"
              value={formData.location || ""}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. Union 3408 or Zoom Link"
            />
          </div>

          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Event Type
            </label>
            <select
              name="event_type"
              value={formData.event_type}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="Senate Meeting">Senate Meeting</option>
              <option value="Committee Hearing">Committee Hearing</option>
              <option value="Finance Hearing">Finance Hearing</option>
              <option value="Other">Other</option>
            </select>
          </div>

          <div className="space-y-2 md:col-span-2">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                name="is_published"
                checked={formData.is_published}
                onChange={handleChange}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700">
                Published (visible on website)
              </span>
            </label>
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-6 border-t border-gray-100">
          <button
            type="button"
            onClick={onCancel}
            disabled={isLoading}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {isLoading ? "Saving..." : initialData ? "Update Event" : "Create Event"}
          </button>
        </div>
      </form>
    </div>
  );
}