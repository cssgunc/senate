"use client";

import type { AnalyticsSummary, DailyPageViewCount, NavigationFlow } from "@/types/admin";
import dynamic from "next/dynamic";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

// Code-split from the initial analytics bundle: the flow diagram fetches and
// computes independently of the summary stats above it (see
// app/admin/analytics/page.tsx), so it shouldn't block their first paint.
const NavigationFlowChart = dynamic(() => import("./NavigationFlowChart"), {
  ssr: false,
  loading: () => (
    <div className="rounded-lg border border-slate-200 p-2 py-20 text-center text-sm text-slate-500">
      Loading flow…
    </div>
  ),
});

function StatTile({ label, value }: { label: string; value: number | null }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        {label}
      </p>
      <p className="mt-1 text-2xl font-semibold text-slate-900">
        {value === null ? "—" : value.toLocaleString()}
      </p>
    </div>
  );
}

function TopList({
  title,
  rows,
}: {
  title: string;
  rows: { label: string; count: number }[];
}) {
  return (
    <div>
      <h3 className="mb-2 text-sm font-semibold text-slate-700">{title}</h3>
      {rows.length === 0 ? (
        <p className="py-6 text-center text-sm text-slate-500">No data yet.</p>
      ) : (
        <div className="overflow-x-auto rounded-lg border border-slate-200">
          <table className="w-full min-w-max text-left text-sm">
            <thead className="border-b border-slate-200 bg-slate-50">
              <tr>
                <th className="px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  {title}
                </th>
                <th className="px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Views
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((row) => (
                <tr key={row.label} className="hover:bg-slate-50/70">
                  <td className="px-4 py-2 text-slate-700">{row.label}</td>
                  <td className="px-4 py-2 text-slate-700">{row.count.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// Bucket timestamps arrive as UTC instants (see DailyPageViewCountDTO); format
// them without an explicit timeZone so they render in the viewer's local time.
function formatBucketLabel(value: string, hourly: boolean): string {
  const date = new Date(value);
  return hourly
    ? date.toLocaleTimeString("en-US", { hour: "numeric" })
    : date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function AnalyticsTooltip({
  active,
  payload,
  hourly,
  data,
}: {
  active?: boolean;
  payload?: { payload: DailyPageViewCount }[];
  hourly: boolean;
  data: DailyPageViewCount[];
}) {
  if (!active || !payload || payload.length === 0) return null;

  const row = payload[0].payload;
  const index = data.findIndex((d) => d.day === row.day);
  const previous = index > 0 ? data[index - 1] : null;
  const change =
    previous && previous.count > 0
      ? ((row.count - previous.count) / previous.count) * 100
      : null;

  return (
    <div className="rounded-md border border-slate-200 bg-white px-3 py-2 text-xs shadow-md">
      <p className="font-semibold text-slate-700">{formatBucketLabel(row.day, hourly)}</p>
      <p className="mt-1 text-slate-600">
        {row.count.toLocaleString()} pageview{row.count === 1 ? "" : "s"}
      </p>
      {change !== null && (
        <p className={change >= 0 ? "mt-0.5 text-emerald-600" : "mt-0.5 text-rose-600"}>
          {change >= 0 ? "+" : ""}
          {change.toFixed(1)}% vs. previous {hourly ? "hour" : "day"}
        </p>
      )}
    </div>
  );
}

export function AnalyticsCharts({
  summary,
  activeUsers,
  navigationFlow,
  isNavigationFlowLoading,
}: {
  summary: AnalyticsSummary;
  activeUsers: number | null;
  navigationFlow: NavigationFlow | null;
  isNavigationFlowLoading?: boolean;
}) {
  const hourly = summary.range_days <= 1;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatTile label="Pageviews" value={summary.total_pageviews} />
        <StatTile label="Unique Visitors" value={summary.unique_visitors} />
        <StatTile label="Active Now" value={activeUsers} />
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-700">Pageviews over time</h3>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={summary.daily_pageviews}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="day"
                tickFormatter={(value: string) => formatBucketLabel(value, hourly)}
                tick={{ fontSize: 12, fill: "#64748b" }}
              />
              <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: "#64748b" }} />
              <Tooltip content={<AnalyticsTooltip hourly={hourly} data={summary.daily_pageviews} />} />
              <Line
                type="monotone"
                dataKey="count"
                name="Pageviews"
                stroke="#2563eb"
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <TopList
          title="Top Pages"
          rows={summary.top_paths.map((row) => ({ label: row.path, count: row.count }))}
        />
        <TopList
          title="Top Referrers"
          rows={summary.top_referrers.map((row) => ({
            label: row.referrer_host,
            count: row.count,
          }))}
        />
      </div>

      <NavigationFlowChart data={navigationFlow} isLoading={isNavigationFlowLoading} />
    </div>
  );
}
