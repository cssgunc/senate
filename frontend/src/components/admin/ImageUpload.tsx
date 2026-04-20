"use client";

import { uploadAdminImage } from "@/lib/mock/admin-api";
import { useEffect, useId, useRef, useState } from "react";

const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024;
const ACCEPTED_MIME_TYPES = new Set(["image/jpeg", "image/png", "image/webp"]);

interface ImageUploadProps {
  label: string;
  value: string;
  onChange: (url: string) => void;
  required?: boolean;
  disabled?: boolean;
}

function resolveImageSrc(url: string): string {
  if (!url) return "";
  if (/^https?:\/\//i.test(url) || url.startsWith("data:")) return url;
  if (!url.startsWith("/")) return url;

  const apiBase = process.env.NEXT_PUBLIC_API_URL;
  if (!apiBase) return url;

  try {
    const origin = new URL(apiBase).origin;
    return `${origin}${url}`;
  } catch {
    return url;
  }
}

function toFriendlyError(message: string): string {
  const normalized = message.toLowerCase();
  if (normalized.includes("too large") || normalized.includes("413")) {
    return "File too large. Max 5MB, JPEG/PNG/WebP.";
  }
  if (normalized.includes("unsupported") || normalized.includes("file type")) {
    return "Unsupported file type. Please upload JPEG, PNG, or WebP.";
  }
  return message;
}

export function ImageUpload({
  label,
  value,
  onChange,
  required = false,
  disabled = false,
}: ImageUploadProps) {
  const inputId = useId();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [localPreviewUrl, setLocalPreviewUrl] = useState<string | null>(null);

  const resolvedValue = resolveImageSrc(value);
  const previewUrl = localPreviewUrl ?? resolvedValue;

  useEffect(() => {
    return () => {
      if (localPreviewUrl) {
        URL.revokeObjectURL(localPreviewUrl);
      }
    };
  }, [localPreviewUrl]);

  const uploadFile = async (file: File) => {
    if (!ACCEPTED_MIME_TYPES.has(file.type)) {
      setError("Unsupported file type. Please upload JPEG, PNG, or WebP.");
      return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      setError("File too large. Max 5MB, JPEG/PNG/WebP.");
      return;
    }

    const objectUrl = URL.createObjectURL(file);
    if (localPreviewUrl) {
      URL.revokeObjectURL(localPreviewUrl);
    }
    setLocalPreviewUrl(objectUrl);
    setError(null);
    setIsUploading(true);
    setUploadProgress(0);

    try {
      const response = await uploadAdminImage(file, (percent) => {
        setUploadProgress(percent);
      });
      onChange(response.url);
    } catch (uploadError) {
      const message =
        uploadError instanceof Error ? uploadError.message : "Upload failed.";
      setError(toFriendlyError(message));
    } finally {
      setIsUploading(false);
    }
  };

  const onFileInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    void uploadFile(file);
    event.target.value = "";
  };

  const onDrop = (event: React.DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setIsDragging(false);
    if (disabled || isUploading) return;
    const file = event.dataTransfer.files?.[0];
    if (!file) return;
    void uploadFile(file);
  };

  return (
    <div>
      <label
        htmlFor={inputId}
        className="block text-sm font-medium text-gray-700 mb-1"
      >
        {label} {required ? <span className="text-red-500">*</span> : null}
      </label>

      <div
        onDragOver={(event) => {
          event.preventDefault();
          if (!disabled && !isUploading) setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={onDrop}
        className={`rounded-lg border-2 border-dashed p-4 transition-colors ${
          isDragging
            ? "border-blue-500 bg-blue-50"
            : "border-gray-300 bg-gray-50"
        } ${disabled ? "opacity-60" : ""}`}
      >
        <input
          id={inputId}
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          onChange={onFileInputChange}
          className="hidden"
          disabled={disabled || isUploading}
        />

        <div className="flex flex-col gap-3">
          <p className="text-sm text-gray-600">
            Drag and drop an image here, or use the picker.
          </p>
          <button
            type="button"
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled || isUploading}
            className="w-fit px-3 py-1.5 text-sm bg-white border border-gray-300 rounded hover:bg-gray-100 disabled:opacity-60"
          >
            {isUploading ? "Uploading..." : "Choose Image"}
          </button>
          <p className="text-xs text-gray-500">Max 5MB, JPEG/PNG/WebP</p>

          {isUploading ? (
            <div className="space-y-1">
              <div className="h-2 w-full bg-gray-200 rounded overflow-hidden">
                <div
                  className="h-full bg-blue-600 transition-all"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
              <p className="text-xs text-gray-600">
                Uploading {uploadProgress}%
              </p>
            </div>
          ) : null}

          {error ? <p className="text-sm text-red-600">{error}</p> : null}
        </div>
      </div>

      {previewUrl ? (
        <div className="mt-3">
          <p className="text-sm text-gray-600 mb-2">Preview</p>
          <div className="relative h-48 w-full rounded border bg-gray-100 overflow-hidden">
            <img
              src={previewUrl}
              alt="Uploaded preview"
              className="w-full h-full object-cover"
            />
          </div>
          {value ? (
            <p className="mt-2 text-xs text-gray-500 break-all">
              Stored URL: {value}
            </p>
          ) : null}
        </div>
      ) : null}
    </div>
  );
}
