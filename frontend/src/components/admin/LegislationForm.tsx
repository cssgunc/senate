"use client";

import { useEffect, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { getSenators } from "@/lib/api";
import type { Legislation, Senator } from "@/types";
import type { CreateLegislation } from "@/types/admin";
import { RichTextEditor } from "./RichTextEditor";

interface LegislationFormProps {
  initialData?: Legislation & { sponsor_id?: number | null };
  onSubmit: (data: CreateLegislation) => Promise<void> | void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function LegislationForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}: LegislationFormProps) {
  const [title, setTitle] = useState(initialData?.title || "");
  const [billNumber, setBillNumber] = useState(initialData?.bill_number || "");
  const [sessionNumber, setSessionNumber] = useState<number>(
    initialData?.session_number || 1,
  );
  const [sponsorId, setSponsorId] = useState<number | null>(
    initialData?.sponsor_id ?? null,
  );
  const [sponsorName, setSponsorName] = useState(
    initialData?.sponsor_name || "",
  );
  const [summary, setSummary] = useState(initialData?.summary || "");
  const [fullText, setFullText] = useState(initialData?.full_text || "");
  const [status, setStatus] = useState(initialData?.status || "Introduced");
  const [type, setType] = useState(initialData?.type || "Bill");

  const formatInitialDate = (dateString?: string) => {
    if (!dateString) return "";
    return new Date(dateString).toISOString().split("T")[0];
  };
  const [dateIntroduced, setDateIntroduced] = useState(
    formatInitialDate(initialData?.date_introduced),
  );

  const [senators, setSenators] = useState<Senator[]>([]);

  useEffect(() => {
    getSenators().then(setSenators).catch(console.error);
  }, []);

  useEffect(() => {
    if (
      sponsorId !== null ||
      !initialData?.sponsor_name ||
      senators.length === 0
    ) {
      return;
    }

    const matchedSponsor = senators.find(
      (senator) =>
        `${senator.first_name} ${senator.last_name}` ===
        initialData.sponsor_name,
    );

    if (matchedSponsor) {
      setSponsorId(matchedSponsor.id);
    }
  }, [initialData?.sponsor_name, senators, sponsorId]);

  const handleSponsorChange = (value: string) => {
    const selectedId = value ? Number(value) : null;
    setSponsorId(selectedId);

    if (selectedId) {
      const selected = senators.find((s) => s.id === selectedId);
      if (selected) {
        setSponsorName(`${selected.first_name} ${selected.last_name}`);
      }
    } else {
      setSponsorName("");
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      title: title.trim(),
      bill_number: billNumber.trim(),
      session_number: sessionNumber,
      sponsor_id: sponsorId,
      sponsor_name: sponsorName.trim(),
      summary: summary.trim(),
      full_text: fullText.trim(),
      status,
      type,
      date_introduced: new Date(dateIntroduced).toISOString(),
    });
  };

  return (
    <div className="space-y-5 rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="text-2xl font-semibold text-slate-900">
        {initialData ? "Edit Legislation" : "Create New Legislation"}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="bill-number">Bill Number</Label>
            <Input
              id="bill-number"
              required
              type="text"
              value={billNumber}
              onChange={(e) => setBillNumber(e.target.value)}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="title">Title</Label>
            <Input
              id="title"
              required
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
            />
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="session-number">Session Number</Label>
            <Input
              id="session-number"
              required
              type="number"
              value={sessionNumber}
              onChange={(e) => setSessionNumber(Number(e.target.value))}
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="date-introduced">Date Introduced</Label>
            <Input
              id="date-introduced"
              required
              type="date"
              value={dateIntroduced}
              onChange={(e) => setDateIntroduced(e.target.value)}
            />
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="sponsor-select">Sponsor</Label>
            <Select
              value={sponsorId ? String(sponsorId) : ""}
              onValueChange={handleSponsorChange}
            >
              <SelectTrigger id="sponsor-select">
                <SelectValue placeholder="Select a senator" />
              </SelectTrigger>
              <SelectContent>
                {senators.map((s) => (
                  <SelectItem key={s.id} value={String(s.id)}>
                    {s.first_name} {s.last_name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="sponsor-name">Sponsor Name</Label>
            <Input
              id="sponsor-name"
              readOnly
              type="text"
              className="bg-slate-50"
              value={sponsorName}
            />
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <div className="space-y-2">
            <Label htmlFor="status">Status</Label>
            <Select value={status} onValueChange={setStatus}>
              <SelectTrigger id="status">
                <SelectValue placeholder="Select status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Introduced">Introduced</SelectItem>
                <SelectItem value="In Committee">In Committee</SelectItem>
                <SelectItem value="Passed">Passed</SelectItem>
                <SelectItem value="Failed">Failed</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="type">Type</Label>
            <Select value={type} onValueChange={setType}>
              <SelectTrigger id="type">
                <SelectValue placeholder="Select type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Bill">Bill</SelectItem>
                <SelectItem value="Resolution">Resolution</SelectItem>
                <SelectItem value="Nomination">Nomination</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="space-y-2">
          <Label htmlFor="summary">Summary</Label>
          <RichTextEditor value={summary} onChange={setSummary} />
        </div>

        <div className="space-y-2">
          <Label htmlFor="full-text">Full Text</Label>
          <RichTextEditor value={fullText} onChange={setFullText} />
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <Button
            type="button"
            variant="outline"
            onClick={onCancel}
            disabled={isLoading}
          >
            Cancel
          </Button>
          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Saving..." : "Save Legislation"}
          </Button>
        </div>
      </form>
    </div>
  );
}
