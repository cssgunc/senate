"use client";

import type { CarouselSlide } from "@/types";
import type { CreateCarouselSlide } from "@/types/admin";
import { useState } from "react";

interface CarouselSlideFormProps {
  initialData?: CarouselSlide;
  onSubmit: (data: CreateCarouselSlide) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function CarouselSlideForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading,
}: CarouselSlideFormProps) {
  const [formData, setFormData] = useState<CreateCarouselSlide>({
    image_url: initialData?.image_url || "",
    overlay_text: initialData?.overlay_text || "",
    link_url: initialData?.link_url || "",
    display_order: initialData?.display_order || 0,
    is_active: initialData?.is_active ?? true,
  });

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>,
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
    if (!formData.image_url) {
      alert("Please provide an image URL.");
      return;
    }
    onSubmit(formData);
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <h2 className="text-xl font-bold mb-6">
        {initialData ? "Edit Slide" : "Create Slide"}
      </h2>
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2 md:col-span-2">
            <label className="block text-sm font-medium text-gray-700">
              Image URL *
            </label>
            <input
              type="text"
              name="image_url"
              required
              value={formData.image_url}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="https://example.com/image.jpg"
            />
            {formData.image_url && (
              <div className="mt-2 text-sm text-gray-500">
                <p className="mb-2">Preview:</p>
                <div className="relative h-48 w-full rounded bg-gray-100 border overflow-hidden">
                  <img
                    src={formData.image_url}
                    alt="Preview"
                    className="w-full h-full object-cover"
                    onError={(e) => {
                      (e.target as HTMLImageElement).src =
                        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100%25' height='100%25'%3E%3Crect width='100%25' height='100%25' fill='%23f3f4f6'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' font-family='sans-serif' font-size='14px' fill='%239ca3af'%3EInvalid Image URL%3C/text%3E%3C/svg%3E";
                    }}
                  />
                </div>
              </div>
            )}
          </div>

          <div className="space-y-2 md:col-span-2">
            <label className="block text-sm font-medium text-gray-700">
              Overlay Text
            </label>
            <input
              type="text"
              name="overlay_text"
              value={formData.overlay_text || ""}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. Welcome to the UNC Senate"
            />
          </div>

          <div className="space-y-2 md:col-span-2">
            <label className="block text-sm font-medium text-gray-700">
              Link URL
            </label>
            <input
              type="text"
              name="link_url"
              value={formData.link_url || ""}
              onChange={handleChange}
              className="w-full border border-gray-300 rounded-md py-2 px-3 focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="e.g. /news/welcome"
            />
          </div>

          <div className="space-y-2 md:col-span-2">
            <label className="flex items-center gap-2 cursor-pointer mt-4">
              <input
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleChange}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
              />
              <span className="text-sm font-medium text-gray-700">
                Active (display on homepage)
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
            {isLoading ? "Saving..." : initialData ? "Update Slide" : "Create Slide"}
          </button>
        </div>
      </form>
    </div>
  );
}