import { getRecentLegislation } from "@/lib/api";

export const dynamic = "force-dynamic";
import type { Legislation } from "@/types";
import { format } from "date-fns";
import Link from "next/link";

const STATUS_STYLES: Record<string, string> = {
  Passed: "bg-green-100 text-green-800",
  Failed: "bg-red-100 text-red-800",
  "In Committee": "bg-yellow-100 text-yellow-800",
  Introduced: "bg-gray-100 text-gray-700",
};

function StatusBadge({ status }: { status: string }) {
  const styles = STATUS_STYLES[status] ?? "bg-gray-100 text-gray-700";
  return (
    <span
      className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${styles}`}
    >
      {status}
    </span>
  );
}

export default async function RecentLegislationPage() {
  const legislation: Legislation[] = await getRecentLegislation(20);

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-6">Recent Legislation</h1>

      {legislation.length === 0 ? (
        <p className="text-gray-500">No recent legislation found.</p>
      ) : (
        <ul className="divide-y divide-gray-200">
          {legislation.map((item) => (
            <li key={item.id}>
              <Link
                href={`/legislation/${item.id}`}
                className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 py-4 hover:bg-gray-50 px-2 rounded-md transition-colors"
              >
                <div className="flex flex-col gap-1">
                  <span className="font-medium text-gray-900">{item.title}</span>
                  <span className="text-sm text-gray-500 font-mono">
                    {item.bill_number}
                  </span>
                </div>
                <div className="flex items-center gap-3 sm:flex-shrink-0">
                  <StatusBadge status={item.status} />
                  <span className="text-sm text-gray-400 whitespace-nowrap">
                    {format(new Date(item.date_introduced), "MMM d, yyyy")}
                  </span>
                </div>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
