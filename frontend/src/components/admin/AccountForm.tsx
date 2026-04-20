"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useState } from "react";
import type { Account, CreateAccount } from "@/types/admin";

interface AccountFormProps {
  initialData?: Account;
  onSubmit: (data: CreateAccount) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function AccountForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}: AccountFormProps) {
  const [firstName, setFirstName] = useState(initialData?.first_name ?? "");
  const [lastName, setLastName] = useState(initialData?.last_name ?? "");
  const [email, setEmail] = useState(initialData?.email ?? "");
  const [pid, setPid] = useState(initialData?.pid ?? "");
  const [role, setRole] = useState<"admin" | "staff">(
    initialData?.role ?? "staff",
  );
  const [pidError, setPidError] = useState("");

  const handlePidChange = (value: string) => {
    setPid(value);
    if (value && !/^\d{9}$/.test(value)) {
      setPidError("PID must be exactly 9 digits");
    } else {
      setPidError("");
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!/^\d{9}$/.test(pid)) {
      setPidError("PID must be exactly 9 digits");
      return;
    }
    onSubmit({ first_name: firstName, last_name: lastName, email, pid, role });
  };

  return (
    <div className="bg-white p-6 rounded-lg border shadow-sm max-w-2xl w-full">
      <h2 className="text-2xl font-bold mb-6">
        {initialData ? "Edit Account" : "Create Account"}
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

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            PID
          </label>
          <p className="text-xs text-gray-500 mb-1">9-digit UNC PID number.</p>
          <input
            required
            type="text"
            maxLength={9}
            className={`w-full p-2 border rounded ${pidError ? "border-red-500" : "border-gray-300"}`}
            value={pid}
            onChange={(e) => handlePidChange(e.target.value)}
            placeholder="123456789"
          />
          {pidError && (
            <p className="text-xs text-red-600 mt-1">{pidError}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Role
          </label>
          <Select
            value={role}
            onValueChange={(val) => setRole(val as "admin" | "staff")}
          >
            <SelectTrigger className="w-full">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="staff">Staff</SelectItem>
              <SelectItem value="admin">Admin</SelectItem>
            </SelectContent>
          </Select>
          <p className="text-xs text-gray-500 mt-1">
            Admin accounts can manage all content and other accounts. Staff
            accounts can manage content but not accounts.
          </p>
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
                ? "Update Account"
                : "Create Account"}
          </button>
        </div>
      </form>
    </div>
  );
}
