"use client";

import type { AdminStaff, CreateStaff, UpdateStaff } from "@/types/admin";
import { useState } from "react";
import { ImageUpload } from "./ImageUpload";

interface StaffFormProps {
  initialData?: AdminStaff;
  onSubmit: (data: CreateStaff | UpdateStaff) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function StaffForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}: StaffFormProps) {
  const [firstName, setFirstName] = useState(initialData?.first_name ?? "");
  const [lastName, setLastName] = useState(initialData?.last_name ?? "");
  const [title, setTitle] = useState(initialData?.title ?? "");
  const [email, setEmail] = useState(initialData?.email ?? "");
  const [photoUrl, setPhotoUrl] = useState(initialData?.photo_url ?? "");
  const [displayOrder, setDisplayOrder] = useState(
    initialData?.display_order ?? 0,
  );
  const [isActive, setIsActive] = useState(initialData?.is_active ?? true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (initialData) {
      const data: UpdateStaff = {
        first_name: firstName,
        last_name: lastName,
        title,
        email,
        photo_url: photoUrl || null,
        display_order: displayOrder,
        is_active: isActive,
      };
      onSubmit(data);
    } else {
      const data: CreateStaff = {
        first_name: firstName,
        last_name: lastName,
        title,
        email,
        photo_url: photoUrl || null,
        display_order: displayOrder,
      };
      onSubmit(data);
    }
  };

  return (
    <div className="bg-white p-6 rounded-lg border shadow-sm max-w-2xl w-full">
      <h2 className="text-2xl font-bold mb-6">
        {initialData ? "Edit Staff Member" : "Add Staff Member"}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              First Name
            </label>
            <input
              required
              type="text"
              className="w-full p-2 border rounded border-gray-300"
              value={firstName}
              onChange={(e) => setFirstName(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Last Name
            </label>
            <input
              required
              type="text"
              className="w-full p-2 border rounded border-gray-300"
              value={lastName}
              onChange={(e) => setLastName(e.target.value)}
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Title
          </label>
          <input
            required
            type="text"
            className="w-full p-2 border rounded border-gray-300"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Chief of Staff"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email
          </label>
          <input
            required
            type="email"
            className="w-full p-2 border rounded border-gray-300"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <ImageUpload
          label="Photo (Optional)"
          value={photoUrl}
          onChange={setPhotoUrl}
          disabled={isLoading}
        />

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Display Order
          </label>
          <p className="text-xs text-gray-500 mb-1">
            Lower numbers appear first in the staff directory.
          </p>
          <input
            required
            type="number"
            className="w-full p-2 border rounded border-gray-300"
            value={displayOrder}
            onChange={(e) => setDisplayOrder(Number(e.target.value))}
          />
        </div>

        {initialData && (
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="is_active"
              className="w-4 h-4"
              checked={isActive}
              onChange={(e) => setIsActive(e.target.checked)}
            />
            <label
              htmlFor="is_active"
              className="text-sm font-medium text-gray-700"
            >
              Active (uncheck to hide from public directory)
            </label>
          </div>
        )}

        <div className="flex justify-end gap-3 border-t pt-4">
          <button
            type="button"
            onClick={onCancel}
            disabled={isLoading}
            className="px-4 py-2 border rounded text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            {isLoading
              ? "Saving..."
              : initialData
                ? "Update Staff"
                : "Add Staff"}
          </button>
        </div>
      </form>
    </div>
  );
}
