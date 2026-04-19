"use client";

import { useState } from "react";
import { RichTextEditor } from "./RichTextEditor";
import type { StaticPage } from "@/types";
import type { UpdateStaticPage } from "@/types/admin";

interface StaticPageFormProps {
  initialData: StaticPage;
  onSubmit: (data: UpdateStaticPage) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function StaticPageForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}: StaticPageFormProps) {
  const [title, setTitle] = useState(initialData.title);
  const [body, setBody] = useState(initialData.body);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ title, body });
  };

  return (
    <div className="bg-white p-6 rounded-lg border shadow-sm max-w-4xl w-full">
      <h2 className="text-2xl font-bold mb-1">Edit Page</h2>
      <p className="text-sm text-gray-500 mb-6">
        Slug:{" "}
        <span className="font-mono bg-gray-100 px-1 rounded">
          {initialData.page_slug}
        </span>
      </p>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Page Title
          </label>
          <input
            required
            type="text"
            className="w-full p-2 border rounded border-gray-300"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Page Content
          </label>
          <RichTextEditor value={body} onChange={setBody} />
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
            {isLoading ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </form>
    </div>
  );
}
