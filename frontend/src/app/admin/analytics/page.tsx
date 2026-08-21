"use client";

import { AdminCard, AdminPageHeader, AdminPageShell } from "@/components/admin/AdminPageShell";
import { AnalyticsCharts } from "@/components/admin/AnalyticsCharts";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { getAnalyticsSummary } from "@/lib/admin-api";
import type { AnalyticsSummary } from "@/types/admin";
import { useEffect, useState } from "react";

const RANGE_OPTIONS = [
  { label: "Last 24 hours", value: 1 },
  { label: "Last 7 days", value: 7 },
  { label: "Last 30 days", value: 30 },
];

export default function AdminAnalyticsPage() {
  const [days, setDays] = useState(7);
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchSummary() {
      setIsLoading(true);
      setError(null);
      try {
        const data = await getAnalyticsSummary(days);
        if (isMounted) setSummary(data);
      } catch (err) {
        console.error("Failed to fetch analytics summary:", err);
        if (isMounted) setError("Failed to load analytics data.");
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }

    fetchSummary();

    return () => {
      isMounted = false;
    };
  }, [days]);

  return (
    <AdminPageShell>
      <AdminPageHeader
        title="Analytics"
        description="Server-side pageview stats collected via the site's proxy — no third-party scripts, cookies, or PII."
        action={
          <Select
            value={String(days)}
            onValueChange={(value) => setDays(Number(value))}
          >
            <SelectTrigger className="w-44">
              <SelectValue placeholder="Select range" />
            </SelectTrigger>
            <SelectContent>
              {RANGE_OPTIONS.map((option) => (
                <SelectItem key={option.value} value={String(option.value)}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        }
      />

      <AdminCard>
        {isLoading ? (
          <div className="py-20 text-center text-slate-500">Loading data...</div>
        ) : error ? (
          <div className="py-20 text-center text-rose-600">{error}</div>
        ) : summary ? (
          <AnalyticsCharts summary={summary} />
        ) : null}
      </AdminCard>
    </AdminPageShell>
  );
}
