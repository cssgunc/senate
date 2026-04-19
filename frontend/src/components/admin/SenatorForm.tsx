"use client";

import { getDistricts } from "@/lib/api";
import type { District, Senator } from "@/types";
import type { CreateSenator, UpdateSenator } from "@/types/admin";
import { useEffect, useState } from "react";
import { ImageUpload } from "./ImageUpload";

interface SenatorFormProps {
  initialData?: Senator;
  onSubmit: (data: CreateSenator | UpdateSenator) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function SenatorForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}: SenatorFormProps) {
  const [districts, setDistricts] = useState<District[]>([]);
  const [districtsLoading, setDistrictsLoading] = useState(true);
  const [firstName, setFirstName] = useState(initialData?.first_name ?? "");
  const [lastName, setLastName] = useState(initialData?.last_name ?? "");
  const [email, setEmail] = useState(initialData?.email ?? "");
  const [districtId, setDistrictId] = useState(
    initialData?.district_id?.toString() ?? "",
  );
  const [sessionNumber, setSessionNumber] = useState(
    initialData?.session_number?.toString() ?? "",
  );
  const [headshotUrl, setHeadshotUrl] = useState(initialData?.headshot_url ?? "");
  const [isActive, setIsActive] = useState(initialData?.is_active ?? true);

  useEffect(() => {
    const loadDistricts = async () => {
      try {
        const data = await getDistricts();
        setDistricts(data);
      } catch (error) {
        console.error("Failed to fetch districts:", error);
      } finally {
        setDistrictsLoading(false);
      }
    };

    loadDistricts();
  }, []);

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();

    const basePayload = {
      first_name: firstName.trim(),
      last_name: lastName.trim(),
      email: email.trim(),
      district_id: Number(districtId),
      session_number: Number(sessionNumber),
      headshot_url: headshotUrl || null,
    };

    if (initialData) {
      onSubmit({
        ...basePayload,
        is_active: isActive,
      });
      return;
    }

    onSubmit(basePayload);
  };

  return (
    <div className="bg-white p-6 rounded-lg border shadow-sm max-w-2xl w-full">
      <h2 className="text-2xl font-bold mb-6">
        {initialData ? "Edit Senator" : "Add Senator"}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              First Name
            </label>
            <input
              required
              type="text"
              className="w-full p-2 border rounded border-gray-300"
              value={firstName}
              onChange={(event) => setFirstName(event.target.value)}
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
              onChange={(event) => setLastName(event.target.value)}
            />
          </div>
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
            onChange={(event) => setEmail(event.target.value)}
          />
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              District
            </label>
            <select
              required
              className="w-full p-2 border rounded border-gray-300 bg-white"
              value={districtId}
              onChange={(event) => setDistrictId(event.target.value)}
              disabled={districtsLoading}
            >
              <option value="">
                {districtsLoading
                  ? "Loading districts..."
                  : "Select a district"}
              </option>
              {districts.map((district) => (
                <option key={district.id} value={district.id}>
                  {district.district_name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Session Number
            </label>
            <input
              required
              type="number"
              min="1"
              className="w-full p-2 border rounded border-gray-300"
              value={sessionNumber}
              onChange={(event) => setSessionNumber(event.target.value)}
            />
          </div>
        </div>

        <ImageUpload
          label="Headshot (Optional)"
          value={headshotUrl}
          onChange={setHeadshotUrl}
          disabled={isLoading}
        />

        {initialData ? (
          <div className="flex items-center gap-2">
            <input
              type="checkbox"
              id="senator-active"
              className="w-4 h-4"
              checked={isActive}
              onChange={(event) => setIsActive(event.target.checked)}
            />
            <label
              htmlFor="senator-active"
              className="text-sm font-medium text-gray-700"
            >
              Active
            </label>
          </div>
        ) : null}

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
            disabled={isLoading || districtsLoading}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-60"
          >
            {isLoading
              ? "Saving..."
              : initialData
                ? "Update Senator"
                : "Add Senator"}
          </button>
        </div>
      </form>
    </div>
  );
}
