"use client";

import { useState, useEffect } from "react";
import { CreateLegislation } from "@/types/admin";
import { Senator } from "@/types";
import { getSenators } from "@/lib/api";

interface LegislationFormProps {
  initialData?: any; // You can type this to Legislation if you prefer
  onSubmit: (data: CreateLegislation) => void;
  onCancel: () => void;
  isLoading?: boolean;
}

export function LegislationForm({
  initialData,
  onSubmit,
  onCancel,
  isLoading = false,
}: LegislationFormProps) {
  // Field States
  const [title, setTitle] = useState(initialData?.title || "");
  const [billNumber, setBillNumber] = useState(initialData?.bill_number || "");
  const [sessionNumber, setSessionNumber] = useState<number>(initialData?.session_number || 1);
  const [sponsorId, setSponsorId] = useState<number | null>(initialData?.sponsor_id || null);
  const [sponsorName, setSponsorName] = useState(initialData?.sponsor_name || "");
  const [summary, setSummary] = useState(initialData?.summary || "");
  const [fullText, setFullText] = useState(initialData?.full_text || "");
  const [status, setStatus] = useState(initialData?.status || "Introduced");
  const [type, setType] = useState(initialData?.type || "Bill");
  
  // Need to format dates nicely for the HTML input (YYYY-MM-DD)
  const formatInitialDate = (dateString?: string) => {
    if (!dateString) return "";
    return new Date(dateString).toISOString().split('T')[0];
  };
  const [dateIntroduced, setDateIntroduced] = useState(formatInitialDate(initialData?.date_introduced));

  // Auto-complete Senator logic
  const [senators, setSenators] = useState<Senator[]>([]);

  useEffect(() => {
    // Fetch senators precisely so we can populate the dropdown
    getSenators().then(setSenators).catch(console.error);
  }, []);

  const handleSponsorChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selectedId = e.target.value ? Number(e.target.value) : null;
    setSponsorId(selectedId);
    
    // Auto-fill sponsor name based on the ID we just picked
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
      title,
      bill_number: billNumber,
      session_number: sessionNumber,
      sponsor_id: sponsorId,
      sponsor_name: sponsorName,
      summary,
      full_text: fullText,
      status,
      type,
      date_introduced: new Date(dateIntroduced).toISOString(),
    });
  };

  return (
    <div className="bg-white p-6 rounded-lg border shadow-sm max-w-4xl w-full mx-auto">
      <h2 className="text-2xl font-bold mb-6">
        {initialData ? "Edit Legislation" : "Create New Legislation"}
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Bill Number</label>
            <input required type="text" className="w-full p-2 border rounded" value={billNumber} onChange={e => setBillNumber(e.target.value)} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Title</label>
            <input required type="text" className="w-full p-2 border rounded" value={title} onChange={e => setTitle(e.target.value)} />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Session Number</label>
            <input required type="number" className="w-full p-2 border rounded" value={sessionNumber} onChange={e => setSessionNumber(Number(e.target.value))} />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Date Introduced</label>
            <input required type="date" className="w-full p-2 border rounded" value={dateIntroduced} onChange={e => setDateIntroduced(e.target.value)} />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Sponsor</label>
            <select className="w-full p-2 border rounded" value={sponsorId || ""} onChange={handleSponsorChange}>
              <option value="">Select a Senator...</option>
              {senators.map(s => (
                <option key={s.id} value={s.id}>{s.first_name} {s.last_name}</option>
              ))}
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Sponsor Name (Auto-filled)</label>
            <input readOnly type="text" className="w-full p-2 border rounded bg-gray-50" value={sponsorName} />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Status</label>
            <select className="w-full p-2 border rounded" value={status} onChange={e => setStatus(e.target.value)}>
              <option value="Introduced">Introduced</option>
              <option value="In Committee">In Committee</option>
              <option value="Passed">Passed</option>
              <option value="Failed">Failed</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Type</label>
            <select className="w-full p-2 border rounded" value={type} onChange={e => setType(e.target.value)}>
              <option value="Bill">Bill</option>
              <option value="Resolution">Resolution</option>
              <option value="Nomination">Nomination</option>
            </select>
          </div>
        </div>

        <div>
           <label className="block text-sm font-medium mb-1">Summary</label>
           <textarea required className="w-full p-2 border rounded" value={summary} onChange={e => setSummary(e.target.value)} rows={3} />
        </div>

        <div>
           <label className="block text-sm font-medium mb-1">Full Text</label>
           <textarea required className="w-full p-2 border rounded" value={fullText} onChange={e => setFullText(e.target.value)} rows={8} />
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <button type="button" onClick={onCancel} disabled={isLoading} className="px-4 py-2 border rounded hover:bg-gray-50">Cancel</button>
          <button type="submit" disabled={isLoading} className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            {isLoading ? "Saving..." : "Save Legislation"}
          </button>
        </div>
      </form>
    </div>
  );
}
