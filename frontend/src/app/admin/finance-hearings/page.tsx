"use client";

import {
  AdminCard,
  AdminPageHeader,
  AdminPageShell,
} from "@/components/admin/AdminPageShell";
import { RichTextEditor } from "@/components/admin/RichTextEditor";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  createFinanceHearingDate,
  deleteFinanceHearingDate,
  updateFinanceHearingConfig,
  updateFinanceHearingDate,
} from "@/lib/admin-api";
import { getFinanceHearings } from "@/lib/api";
import type { FinanceHearingDate } from "@/types";
import { useEffect, useMemo, useState } from "react";

type DateFormState = {
  id: number | null;
  hearing_date: string;
  hearing_time: string;
  location: string;
  description: string;
  is_full: boolean;
};

const EMPTY_DATE_FORM: DateFormState = {
  id: null,
  hearing_date: "",
  hearing_time: "",
  location: "",
  description: "",
  is_full: false,
};

function toTimeInputValue(time: string): string {
  return time.length >= 5 ? time.slice(0, 5) : time;
}

function errorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Request failed";
}

export default function AdminFinanceHearingsPage() {
  const [isLoading, setIsLoading] = useState(true);
  const [isSavingConfig, setIsSavingConfig] = useState(false);
  const [isSavingDate, setIsSavingDate] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [isActive, setIsActive] = useState(false);
  const [seasonStart, setSeasonStart] = useState("");
  const [seasonEnd, setSeasonEnd] = useState("");
  const [dates, setDates] = useState<FinanceHearingDate[]>([]);
  const [dateForm, setDateForm] = useState<DateFormState>(EMPTY_DATE_FORM);

  async function loadData() {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getFinanceHearings();
      setIsActive(data.is_active);
      setSeasonStart(data.season_start ?? "");
      setSeasonEnd(data.season_end ?? "");
      setDates(data.dates);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void loadData();
  }, []);

  const sortedDates = useMemo(
    () =>
      [...dates].sort((a, b) => {
        const aKey = `${a.hearing_date} ${a.hearing_time}`;
        const bKey = `${b.hearing_date} ${b.hearing_time}`;
        return aKey.localeCompare(bKey);
      }),
    [dates],
  );

  async function onSaveConfig() {
    setIsSavingConfig(true);
    setError(null);
    try {
      const updated = await updateFinanceHearingConfig({
        is_active: isActive,
        season_start: seasonStart || null,
        season_end: seasonEnd || null,
      });
      setIsActive(updated.is_active);
      setSeasonStart(updated.season_start ?? "");
      setSeasonEnd(updated.season_end ?? "");
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setIsSavingConfig(false);
    }
  }

  async function onSubmitDate(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!dateForm.hearing_date || !dateForm.hearing_time) {
      setError("Hearing date and time are required.");
      return;
    }

    setIsSavingDate(true);
    setError(null);
    try {
      const payload = {
        hearing_date: dateForm.hearing_date,
        hearing_time: dateForm.hearing_time,
        location: dateForm.location || null,
        description: dateForm.description || null,
      };

      if (dateForm.id === null) {
        const created = await createFinanceHearingDate(payload);
        setDates((current) => [...current, created]);
      } else {
        const updated = await updateFinanceHearingDate(dateForm.id, {
          ...payload,
          is_full: dateForm.is_full,
        });
        setDates((current) =>
          current.map((item) => (item.id === updated.id ? updated : item)),
        );
      }

      setDateForm(EMPTY_DATE_FORM);
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setIsSavingDate(false);
    }
  }

  function onEditDate(item: FinanceHearingDate) {
    setDateForm({
      id: item.id,
      hearing_date: item.hearing_date,
      hearing_time: toTimeInputValue(item.hearing_time),
      location: item.location ?? "",
      description: item.description ?? "",
      is_full: item.is_full,
    });
  }

  async function onDeleteDate(id: number) {
    if (!window.confirm("Delete this hearing date?")) return;

    setError(null);
    try {
      await deleteFinanceHearingDate(id);
      setDates((current) => current.filter((item) => item.id !== id));
      if (dateForm.id === id) {
        setDateForm(EMPTY_DATE_FORM);
      }
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  async function onToggleIsFull(item: FinanceHearingDate) {
    setError(null);
    try {
      const updated = await updateFinanceHearingDate(item.id, {
        hearing_date: item.hearing_date,
        hearing_time: toTimeInputValue(item.hearing_time),
        location: item.location,
        description: item.description,
        is_full: !item.is_full,
      });
      setDates((current) =>
        current.map((date) => (date.id === item.id ? updated : date)),
      );
    } catch (err) {
      setError(errorMessage(err));
    }
  }

  if (isLoading) {
    return <p className="text-sm text-slate-600">Loading data...</p>;
  }

  return (
    <AdminPageShell className="space-y-8">
      <AdminPageHeader
        title="Finance Hearings"
        description="Manage hearing season availability and date slots."
      />

      {error ? (
        <p className="rounded-md border border-rose-200 bg-rose-50 px-3 py-2 text-sm text-rose-700">
          {error}
        </p>
      ) : null}

      <AdminCard className="p-4">
        <h2 className="text-lg font-semibold text-slate-900">Season Config</h2>
        <div className="mt-4 grid gap-4 md:grid-cols-3">
          <div className="flex items-center gap-2">
            <Checkbox
              id="hearing-active"
              checked={isActive}
              onCheckedChange={(checked) => setIsActive(Boolean(checked))}
            />
            <Label htmlFor="hearing-active">Hearing season active</Label>
          </div>

          <div className="space-y-2">
            <Label htmlFor="season-start">Season start</Label>
            <Input
              id="season-start"
              type="date"
              value={seasonStart}
              onChange={(event) => setSeasonStart(event.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="season-end">Season end</Label>
            <Input
              id="season-end"
              type="date"
              value={seasonEnd}
              onChange={(event) => setSeasonEnd(event.target.value)}
            />
          </div>
        </div>

        <Button
          onClick={onSaveConfig}
          disabled={isSavingConfig}
          className="mt-4"
        >
          {isSavingConfig ? "Saving..." : "Save Config"}
        </Button>
      </AdminCard>

      <AdminCard className="p-4">
        <h2 className="text-lg font-semibold text-slate-900">
          {dateForm.id === null ? "Add Hearing Date" : "Edit Hearing Date"}
        </h2>

        <form
          className="mt-4 grid gap-4 md:grid-cols-2"
          onSubmit={onSubmitDate}
        >
          <div className="space-y-2">
            <Label htmlFor="hearing-date">Date</Label>
            <Input
              id="hearing-date"
              type="date"
              value={dateForm.hearing_date}
              onChange={(event) =>
                setDateForm((current) => ({
                  ...current,
                  hearing_date: event.target.value,
                }))
              }
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="hearing-time">Time</Label>
            <Input
              id="hearing-time"
              type="time"
              value={dateForm.hearing_time}
              onChange={(event) =>
                setDateForm((current) => ({
                  ...current,
                  hearing_time: event.target.value,
                }))
              }
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="hearing-location">Location</Label>
            <Input
              id="hearing-location"
              type="text"
              value={dateForm.location}
              onChange={(event) =>
                setDateForm((current) => ({
                  ...current,
                  location: event.target.value,
                }))
              }
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="hearing-description">Description</Label>
            <RichTextEditor
              value={dateForm.description}
              onChange={(value) =>
                setDateForm((current) => ({
                  ...current,
                  description: value,
                }))
              }
            />
          </div>

          {dateForm.id !== null ? (
            <div className="flex items-center gap-2">
              <Checkbox
                id="hearing-full"
                checked={dateForm.is_full}
                onCheckedChange={(checked) =>
                  setDateForm((current) => ({
                    ...current,
                    is_full: Boolean(checked),
                  }))
                }
              />
              <Label htmlFor="hearing-full">Mark this hearing as full</Label>
            </div>
          ) : null}

          <div className="flex gap-2 md:col-span-2">
            <Button type="submit" disabled={isSavingDate}>
              {isSavingDate
                ? "Saving..."
                : dateForm.id === null
                  ? "Add Date"
                  : "Save Date"}
            </Button>
            {dateForm.id !== null ? (
              <Button
                type="button"
                variant="destructive"
                onClick={() => setDateForm(EMPTY_DATE_FORM)}
              >
                Cancel Edit
              </Button>
            ) : null}
          </div>
        </form>
      </AdminCard>

      <AdminCard className="p-4">
        <h2 className="text-lg font-semibold text-slate-900">Hearing Dates</h2>
        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-sm">
            <thead className="bg-slate-50">
              <tr>
                <th className="px-3 py-2 text-left font-medium text-slate-600">
                  Date
                </th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">
                  Time
                </th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">
                  Location
                </th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">
                  Full
                </th>
                <th className="px-3 py-2 text-left font-medium text-slate-600">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {sortedDates.length === 0 ? (
                <tr>
                  <td
                    colSpan={5}
                    className="px-3 py-6 text-center text-slate-500"
                  >
                    No hearing dates created yet.
                  </td>
                </tr>
              ) : (
                sortedDates.map((item) => (
                  <tr key={item.id}>
                    <td className="px-3 py-2 text-slate-800">
                      {item.hearing_date}
                    </td>
                    <td className="px-3 py-2 text-slate-800">
                      {toTimeInputValue(item.hearing_time)}
                    </td>
                    <td className="px-3 py-2 text-slate-700">
                      {item.location || "-"}
                    </td>
                    <td className="px-3 py-2">
                      <button
                        type="button"
                        onClick={() => void onToggleIsFull(item)}
                        className={`rounded-full px-3 py-1 text-xs font-medium ${
                          item.is_full
                            ? "bg-amber-100 text-amber-800"
                            : "bg-emerald-100 text-emerald-700"
                        }`}
                      >
                        {item.is_full ? "Full" : "Open"}
                      </button>
                    </td>
                    <td className="px-3 py-2">
                      <div className="flex gap-2">
                        <button
                          type="button"
                          onClick={() => onEditDate(item)}
                          className="rounded border border-slate-300 px-2 py-1 text-xs font-medium text-slate-700"
                        >
                          Edit
                        </button>
                        <button
                          type="button"
                          onClick={() => void onDeleteDate(item.id)}
                          className="rounded border border-rose-300 px-2 py-1 text-xs font-medium text-rose-700"
                        >
                          Delete
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </AdminCard>
    </AdminPageShell>
  );
}
