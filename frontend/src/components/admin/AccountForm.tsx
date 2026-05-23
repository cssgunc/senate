"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useState } from "react";
import type { Account, CreateAccount, UpdateAccount } from "@/types/admin";

interface AccountFormProps {
  initialData?: Account;
  onSubmit: (data: CreateAccount | UpdateAccount) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

const MIN_PASSWORD_LENGTH = 12;
const ONYEN_PATTERN = /^[A-Za-z0-9._-]{2,64}$/;

export function AccountForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}: AccountFormProps) {
  const [firstName, setFirstName] = useState(initialData?.first_name ?? "");
  const [lastName, setLastName] = useState(initialData?.last_name ?? "");
  const [email, setEmail] = useState(initialData?.email ?? "");
  const [onyen, setOnyen] = useState(initialData?.onyen ?? "");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"admin" | "staff">(
    initialData?.role ?? "staff",
  );
  const [onyenError, setOnyenError] = useState("");
  const [passwordError, setPasswordError] = useState("");

  const isEditing = Boolean(initialData);

  const handleOnyenChange = (value: string) => {
    setOnyen(value);
    if (value && !ONYEN_PATTERN.test(value.trim())) {
      setOnyenError("Use 2-64 letters, numbers, dots, underscores, or hyphens.");
    } else {
      setOnyenError("");
    }
  };

  const validatePassword = (value: string) => {
    if ((!isEditing || value) && value.length < MIN_PASSWORD_LENGTH) {
      return `Password must be at least ${MIN_PASSWORD_LENGTH} characters.`;
    }
    return "";
  };

  const handlePasswordChange = (value: string) => {
    setPassword(value);
    setPasswordError(validatePassword(value));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    const trimmedOnyen = onyen.trim().toLowerCase();
    if (!ONYEN_PATTERN.test(trimmedOnyen)) {
      setOnyenError("Use 2-64 letters, numbers, dots, underscores, or hyphens.");
      return;
    }

    const nextPasswordError = validatePassword(password);
    if (nextPasswordError) {
      setPasswordError(nextPasswordError);
      return;
    }

    const payload = {
      first_name: firstName,
      last_name: lastName,
      email,
      onyen: trimmedOnyen,
      role,
      ...(password ? { password } : {}),
    };

    onSubmit(payload as CreateAccount | UpdateAccount);
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
            Onyen
          </label>
          <input
            required
            type="text"
            autoComplete="username"
            className={`w-full p-2 border rounded ${onyenError ? "border-red-500" : "border-gray-300"}`}
            value={onyen}
            onChange={(e) => handleOnyenChange(e.target.value)}
            placeholder="onyen"
          />
          {onyenError && (
            <p className="text-xs text-red-600 mt-1">{onyenError}</p>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Password
          </label>
          <input
            required={!isEditing}
            type="password"
            autoComplete={isEditing ? "new-password" : "new-password"}
            className={`w-full p-2 border rounded ${passwordError ? "border-red-500" : "border-gray-300"}`}
            value={password}
            onChange={(e) => handlePasswordChange(e.target.value)}
            placeholder={isEditing ? "Leave blank to keep current password" : "12+ characters"}
          />
          {passwordError && (
            <p className="text-xs text-red-600 mt-1">{passwordError}</p>
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
