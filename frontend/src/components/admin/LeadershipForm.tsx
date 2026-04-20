"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { getSenators } from "@/lib/api";
import { Senator } from "@/types";
import {
  AdminLeadership,
  CreateLeadership,
  UpdateLeadership,
} from "@/types/admin";
import { useEffect, useState } from "react";
import { ImageUpload } from "./ImageUpload";

interface LeadershipFormProps {
  initialData?: AdminLeadership;
  onSubmit: (data: CreateLeadership | UpdateLeadership) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function LeadershipForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}: LeadershipFormProps) {
  const [title, setTitle] = useState(initialData?.title || "");
  const [firstName, setFirstName] = useState(initialData?.first_name || "");
  const [lastName, setLastName] = useState(initialData?.last_name || "");
  const [email, setEmail] = useState(initialData?.email || "");
  const [sessionNumber, setSessionNumber] = useState(
    initialData?.session_number?.toString() || "1",
  );
  const [isActive, setIsActive] = useState(initialData?.is_current ?? true);
  const [senatorId, setSenatorId] = useState<number | null>(
    initialData?.senator_id ?? null,
  );
  const [headShotUrl, setHeadShotUrl] = useState(initialData?.photo_url || "");

  const [senators, setSenators] = useState<Senator[]>([]);
  const [senatorsLoading, setSenatorsLoading] = useState(true);

  useEffect(() => {
    const fetchSenators = async () => {
      try {
        const data = await getSenators();
        setSenators(data);
      } catch (error) {
        console.error("Failed to fetch senators:", error);
      } finally {
        setSenatorsLoading(false);
      }
    };
    fetchSenators();
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const formData = {
      title,
      first_name: firstName,
      last_name: lastName,
      email,
      session_number: parseInt(sessionNumber),
      is_active: isActive,
      senator_id: senatorId,
      ...(headShotUrl && { headshot_url: headShotUrl }),
    };

    onSubmit(formData);
  };

  return (
    <div className="bg-white p-6 rounded-lg border shadow-sm max-w-2xl w-full">
      <h2 className="text-2xl font-bold mb-6">
        {initialData ? "Edit Leadership" : "Add Leadership"}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Title Field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Title <span className="text-red-500">*</span>
          </label>
          <input
            required
            type="text"
            className="w-full p-2 border rounded border-gray-300"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="E.g., President, Vice President"
          />
        </div>

        {/* First Name Field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            First Name <span className="text-red-500">*</span>
          </label>
          <input
            required
            type="text"
            className="w-full p-2 border rounded border-gray-300"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
            placeholder="First name"
          />
        </div>

        {/* Last Name Field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Last Name <span className="text-red-500">*</span>
          </label>
          <input
            required
            type="text"
            className="w-full p-2 border rounded border-gray-300"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
            placeholder="Last name"
          />
        </div>

        {/* Email Field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Email <span className="text-red-500">*</span>
          </label>
          <input
            required
            type="email"
            className="w-full p-2 border rounded border-gray-300"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="email@example.com"
          />
        </div>

        {/* Senator Dropdown Field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Link to Senator (Optional)
          </label>
          <Select
            value={senatorId?.toString() || "none"}
            onValueChange={(val) =>
              setSenatorId(val === "none" ? null : parseInt(val))
            }
            disabled={senatorsLoading}
          >
            <SelectTrigger className="w-full">
              <SelectValue placeholder="No Senator" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="none">— No Senator —</SelectItem>
              {senators.map((senator) => (
                <SelectItem key={senator.id} value={String(senator.id)}>
                  {senator.first_name} {senator.last_name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <p className="text-xs text-gray-500 mt-1">
            Optional. Link this leadership entry to a senator record.
          </p>
        </div>

        {/* Session Number Field */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Session Number <span className="text-red-500">*</span>
          </label>
          <input
            required
            type="number"
            min="1"
            className="w-full p-2 border rounded border-gray-300"
            value={sessionNumber}
            onChange={(e) => setSessionNumber(e.target.value)}
            placeholder="1"
          />
        </div>

        <ImageUpload
          label="Photo (Optional)"
          value={headShotUrl}
          onChange={setHeadShotUrl}
          disabled={isLoading}
        />

        {/* Active Status Checkbox */}
        <div className="flex items-center">
          <input
            type="checkbox"
            id="isActive"
            className="w-4 h-4 text-blue-600 rounded"
            checked={isActive}
            onChange={(e) => setIsActive(e.target.checked)}
          />
          <label htmlFor="isActive" className="ml-2 text-sm text-gray-700">
            Active
          </label>
        </div>

        {/* Submit Buttons */}
        <div className="flex gap-3 justify-end">
          <button
            type="button"
            onClick={onCancel}
            className="px-4 py-2 text-gray-700 bg-gray-200 rounded hover:bg-gray-300"
            disabled={isLoading}
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-4 py-2 text-white bg-blue-600 rounded hover:bg-blue-700 disabled:bg-gray-400"
            disabled={isLoading}
          >
            {isLoading ? "Saving..." : "Save"}
          </button>
        </div>
      </form>
    </div>
  );
}
