"use client";

import type { TargetUptime, UptimeIncident, UptimeSummary } from "@/types/admin";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const TARGET_COLORS: Record<string, string> = {
  backend: "#2563eb",
  frontend: "#16a34a",
};

const TARGET_LABELS: Record<string, string> = {
  backend: "Backend",
  frontend: "Frontend",
};

function StatTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className="mt-1 text-2xl font-semibold text-slate-900">{value}</p>
    </div>
  );
}

// Bucket timestamps arrive as UTC instants (see UptimeBucketDTO); format
// them without an explicit timeZone so they render in the viewer's local time.
function formatBucketLabel(value: string, hourly: boolean): string {
  const date = new Date(value);
  return hourly
    ? date.toLocaleTimeString("en-US", { hour: "numeric" })
    : date.toLocaleDateString("en-US", { month: "short", day: "numeric" });
}

function formatDuration(seconds: number | null): string {
  if (seconds === null) return "ongoing";
  if (seconds < 60) return `${Math.round(seconds)}s`;
  if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
  return `${(seconds / 3600).toFixed(1)}h`;
}

// Each target reports its own bucket rows independently; merge them into one
// row per bucket timestamp so recharts can plot every target's line against
// a shared X axis.
function mergeBuckets(targets: TargetUptime[]): Record<string, string | number>[] {
  const byBucket = new Map<string, Record<string, string | number>>();
  for (const target of targets) {
    for (const row of target.buckets) {
      const existing = byBucket.get(row.bucket) ?? { bucket: row.bucket };
      existing[target.target] = row.uptime_pct;
      byBucket.set(row.bucket, existing);
    }
  }
  return Array.from(byBucket.values()).sort((a, b) => String(a.bucket).localeCompare(String(b.bucket)));
}

function UptimeTooltip({
  active,
  payload,
  label,
  hourly,
}: {
  active?: boolean;
  payload?: { dataKey?: string | number; value?: number | string }[];
  label?: string | number;
  hourly: boolean;
}) {
  if (!active || !payload || payload.length === 0) return null;

  return (
    <div className="rounded-md border border-slate-200 bg-white px-3 py-2 text-xs shadow-md">
      <p className="font-semibold text-slate-700">{formatBucketLabel(String(label), hourly)}</p>
      {payload.map((entry) => {
        const key = String(entry.dataKey ?? "");
        const value = typeof entry.value === "number" ? entry.value : Number(entry.value ?? 0);
        return (
          <p key={key} className="mt-0.5 text-slate-600">
            {TARGET_LABELS[key] ?? key}: {value.toFixed(1)}%
          </p>
        );
      })}
    </div>
  );
}

export function UptimeChart({ summary }: { summary: UptimeSummary }) {
  const hourly = summary.range_days <= 1;
  const chartData = mergeBuckets(summary.targets);

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <StatTile label="Overall Uptime" value={`${summary.overall_uptime_pct.toFixed(2)}%`} />
        {summary.targets.map((target) => (
          <StatTile
            key={target.target}
            label={`${TARGET_LABELS[target.target] ?? target.target} Uptime`}
            value={`${target.uptime_pct.toFixed(2)}%`}
          />
        ))}
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-700">Uptime over time</h3>
        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
              <XAxis
                dataKey="bucket"
                tickFormatter={(value: string) => formatBucketLabel(value, hourly)}
                tick={{ fontSize: 12, fill: "#64748b" }}
              />
              <YAxis
                domain={[0, 100]}
                tickFormatter={(value: number) => `${value}%`}
                tick={{ fontSize: 12, fill: "#64748b" }}
              />
              <Tooltip content={<UptimeTooltip hourly={hourly} />} />
              <Legend formatter={(value: string) => TARGET_LABELS[value] ?? value} />
              {summary.targets.map((target) => (
                <Line
                  key={target.target}
                  type="monotone"
                  dataKey={target.target}
                  name={target.target}
                  stroke={TARGET_COLORS[target.target] ?? "#64748b"}
                  strokeWidth={2}
                  dot={false}
                  connectNulls
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div>
        <h3 className="mb-2 text-sm font-semibold text-slate-700">Recent incidents</h3>
        {summary.incidents.length === 0 ? (
          <p className="py-6 text-center text-sm text-slate-500">No incidents in this range.</p>
        ) : (
          <div className="overflow-x-auto rounded-lg border border-slate-200">
            <table className="w-full min-w-max text-left text-sm">
              <thead className="border-b border-slate-200 bg-slate-50">
                <tr>
                  <th className="px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Target
                  </th>
                  <th className="px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Started
                  </th>
                  <th className="px-4 py-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
                    Duration
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {summary.incidents.map((incident: UptimeIncident, index: number) => (
                  <tr
                    key={`${incident.target}-${incident.started_at}-${index}`}
                    className="hover:bg-slate-50/70"
                  >
                    <td className="px-4 py-2 text-slate-700">
                      {TARGET_LABELS[incident.target] ?? incident.target}
                    </td>
                    <td className="px-4 py-2 text-slate-700">
                      {new Date(incident.started_at).toLocaleString()}
                    </td>
                    <td className="px-4 py-2 text-slate-700">
                      {formatDuration(incident.duration_seconds)}
                      {incident.ended_at === null && <span className="ml-1 text-rose-600">(ongoing)</span>}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
