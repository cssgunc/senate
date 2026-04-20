"use client";

import type {
  AdminDistrict,
  CreateDistrict,
  UpdateDistrict,
} from "@/types/admin";
import { useState } from "react";
import { RichTextEditor } from "./RichTextEditor";

interface DistrictFormProps {
  initialData?: AdminDistrict;
  onSubmit: (data: CreateDistrict | UpdateDistrict) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function DistrictForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}: DistrictFormProps) {
  const [districtName, setDistrictName] = useState(
    initialData?.district_name ?? "",
  );
  const [description, setDescription] = useState(
    initialData?.description ?? "",
  );

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      district_name: districtName,
      description: description || null,
    });
  };

  return (
    <div className="bg-white p-6 rounded-lg border shadow-sm max-w-2xl w-full">
      <h2 className="text-2xl font-bold mb-6">
        {initialData ? "Edit District" : "Add District"}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            District Name
          </label>
          <input
            required
            type="text"
            className="w-full p-2 border rounded border-gray-300"
            value={districtName}
            onChange={(e) => setDistrictName(e.target.value)}
            placeholder="e.g. At-Large"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description (Optional)
          </label>
          <RichTextEditor value={description} onChange={setDescription} />
        </div>

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
                ? "Update District"
                : "Add District"}
          </button>
        </div>
      </form>
    </div>
  );
}
