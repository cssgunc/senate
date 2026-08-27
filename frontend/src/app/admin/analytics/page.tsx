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
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeUsers, setActiveUsers] = useState<number | null>(null);

  const [navigationFlow, setNavigationFlow] = useState<NavigationFlow | null>(null);
  const [isFlowLoading, setIsFlowLoading] = useState(true);

  // Kept separate from the navigation-flow fetch below: the flow query scans
  // and sorts every pageview in range, so it can lag well behind the summary
  // stats. Gating the whole page on both left visitors staring at a blank
  // spinner for the slower of the two; the summary and line chart should
  // render as soon as they're ready.
  useEffect(() => {
    let isMounted = true;

    async function fetchSummary() {
      setIsLoading(true);
      setError(null);
      try {
        const summaryData = await getAnalyticsSummary(days);
        if (isMounted) setSummary(summaryData);
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

  useEffect(() => {
    let isMounted = true;

    async function fetchNavigationFlow() {
      setIsFlowLoading(true);
      try {
        const flowData = await getNavigationFlow(days);
        if (isMounted) setNavigationFlow(flowData);
      } catch (err) {
        console.error("Failed to fetch navigation flow:", err);
      } finally {
        if (isMounted) setIsFlowLoading(false);
      }
    }

    fetchNavigationFlow();

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
          <AnalyticsCharts
            summary={summary}
            activeUsers={activeUsers}
            navigationFlow={navigationFlow}
            isNavigationFlowLoading={isFlowLoading}
          />
        ) : null}
      </AdminCard>
    </AdminPageShell>
  );
}
