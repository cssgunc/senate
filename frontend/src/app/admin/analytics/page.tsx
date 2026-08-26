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
import { getActiveUsers, getAnalyticsSummary, getNavigationFlow } from "@/lib/admin-api";
import type { AnalyticsSummary, NavigationFlow } from "@/types/admin";
import { useEffect, useState } from "react";

const RANGE_OPTIONS = [
  { label: "Last 24 hours", value: 1 },
  { label: "Last 7 days", value: 7 },
  { label: "Last 30 days", value: 30 },
];

const ACTIVE_USERS_POLL_MS = 30_000;

export default function AdminAnalyticsPage() {
  const [days, setDays] = useState(7);
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [navigationFlow, setNavigationFlow] = useState<NavigationFlow | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeUsers, setActiveUsers] = useState<number | null>(null);

  useEffect(() => {
    let isMounted = true;

    async function fetchData() {
      setIsLoading(true);
      setError(null);
      try {
        const [summaryData, flowData] = await Promise.all([
          getAnalyticsSummary(days),
          getNavigationFlow(days),
        ]);
        if (isMounted) {
          setSummary(summaryData);
          setNavigationFlow(flowData);
        }
      } catch (err) {
        console.error("Failed to fetch analytics data:", err);
        if (isMounted) setError("Failed to load analytics data.");
      } finally {
        if (isMounted) setIsLoading(false);
      }
    }

    fetchData();

    return () => {
      isMounted = false;
    };
  }, [days]);

  useEffect(() => {
    let isMounted = true;

    async function fetchActiveUsers() {
      try {
        const data = await getActiveUsers();
        if (isMounted) setActiveUsers(data.active_users);
      } catch (err) {
        console.error("Failed to fetch active users:", err);
      }
    }

    fetchActiveUsers();
    const interval = setInterval(fetchActiveUsers, ACTIVE_USERS_POLL_MS);

    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <AdminPageShell>
      <AdminPageHeader
        title="Analytics"
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
          <AnalyticsCharts summary={summary} activeUsers={activeUsers} navigationFlow={navigationFlow} />
        ) : null}
      </AdminCard>
    </AdminPageShell>
  );
}
