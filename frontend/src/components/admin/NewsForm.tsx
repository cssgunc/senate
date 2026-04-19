"use client";

import { useState } from "react";
import { RichTextEditor } from "./RichTextEditor";
import { CreateNews, UpdateNews } from "@/types/admin";
import { AdminNews } from "@/types/admin";

interface NewsFormProps {
  // If we pass an existing article in, the form starts in "Edit Mode"
  initialData?: AdminNews;
  // What to do when the form is submitted
  onSubmit: (data: CreateNews | UpdateNews) => void;
  // What to do if the user clicks "Cancel"
  onCancel: () => void;
  // Is the form currently saving to the backend?
  isLoading?: boolean;
}

export function NewsForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}: NewsFormProps) {
  // We create state for every field on the form. 
  // If initialData exists, we load it. Otherwise, we start blank.
  const [title, setTitle] = useState(initialData?.title || "");
  const [summary, setSummary] = useState(initialData?.summary || "");
  const [body, setBody] = useState(initialData?.body || "");
  const [imageUrl, setImageUrl] = useState(initialData?.image_url || "");
  
  // Note: Your initialData might have 'status' string instead of 'is_published' boolean, 
  // so we check if it's currently published, otherwise start as false.
  const [isPublished, setIsPublished] = useState(
    initialData?.is_published ?? false
  );

  const handleSubmit = (e: React.FormEvent) => {
    // Prevent the web page from refreshing when we hit submit
    e.preventDefault();

    // Package all our state up into an object to send to the parent
    const formData = {
      title,
      summary,
      body,
      image_url: imageUrl || null,
      is_published: isPublished,
    };

    // Fire the save function!
    onSubmit(formData);
  };

  return (
    <div className="bg-white p-6 rounded-lg border shadow-sm max-w-4xl w-full">
      <h2 className="text-2xl font-bold mb-6">
        {initialData ? "Edit Article" : "Create New Article"}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title Field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Article Title
          </label>
          <input
            required
            type="text"
            className="w-full p-2 border rounded border-gray-300"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="E.g., CSSG Spring Updates"
          />
        </div>

        {/* Summary Field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Short Summary
          </label>
          <p className="text-xs text-gray-500 mb-2">
            A quick 1-2 sentence description that shows up on the news cards.
          </p>
          <textarea
            required
            className="w-full p-2 border rounded border-gray-300"
            rows={3}
            value={summary}
            onChange={(e) => setSummary(e.target.value)}
            placeholder="A quick overview of what happened..."
          />
        </div>

        {/* Image URL Field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Cover Image URL (Optional)
          </label>
          <input
            type="url"
            className="w-full p-2 border rounded border-gray-300"
            value={imageUrl}
            onChange={(e) => setImageUrl(e.target.value)}
            placeholder="https://example.com/image.png"
          />
        </div>

        {/* Rich Text Body Field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Article Content
          </label>
          {/* BAM! We plug in the Rich Text Component we just built */}
          <RichTextEditor value={body} onChange={setBody} />
        </div>

        {/* Publish Toggle */}
        <div className="flex items-center gap-2">
          <input
            type="checkbox"
            id="published"
            className="w-4 h-4"
            checked={isPublished}
            onChange={(e) => setIsPublished(e.target.checked)}
          />
          <label htmlFor="published" className="text-sm font-medium text-gray-700">
            Publish immediately? (Uncheck to save as draft)
          </label>
        </div>

        {/* Buttons */}
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
            {isLoading ? "Saving..." : initialData ? "Update Article" : "Create Article"}
          </button>
        </div>
      </form>
    </div>
  );
}
