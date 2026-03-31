import { getLegislationById } from "@/lib/api";
import type { Legislation, LegislationAction } from "@/types";
import { format } from "date-fns";
import { notFound } from "next/navigation";

const STATUS_STYLES: Record<string, string> = {
  Passed: "bg-green-100 text-green-800",
  Failed: "bg-red-100 text-red-800",
  "In Committee": "bg-yellow-100 text-yellow-800",
  Introduced: "bg-gray-100 text-gray-700",
};

function StatusBadge({ status }: { status: string }) {
  const styles = STATUS_STYLES[status] ?? "bg-gray-100 text-gray-700";
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-sm font-medium ${styles}`}>
      {status}
    </span>
  );
}

function ActionTimeline({ actions }: { actions: LegislationAction[] }) {
  if (actions.length === 0) return null;

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Action History</h2>
      <ol className="relative border-l border-gray-200 space-y-6 pl-6">
        {actions.map((action) => (
          <li key={action.id} className="relative">
            <span className="absolute -left-[1.4rem] top-1 flex h-4 w-4 items-center justify-center rounded-full bg-blue-100 ring-2 ring-white">
              <span className="h-2 w-2 rounded-full bg-blue-500" />
            </span>
            <p className="text-xs text-gray-500 mb-0.5">
              {format(new Date(action.action_date), "MMMM d, yyyy")} &middot;{" "}
              {action.action_type}
            </p>
            <p className="text-sm text-gray-800">{action.description}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}

export default async function LegislationDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  let legislation: Legislation;
  try {
    legislation = await getLegislationById(id);
  } catch {
    notFound();
  }

  return (
    <div className="container mx-auto p-4 max-w-3xl">
      <div className="flex flex-wrap items-center gap-2 mb-2">
        <span className="text-sm text-gray-500 font-mono">
          {legislation.bill_number}
        </span>
        <span className="text-gray-300">&bull;</span>
        <span className="text-sm text-gray-500">{legislation.type}</span>
        <span className="text-gray-300">&bull;</span>
        <StatusBadge status={legislation.status} />
      </div>

      <h1 className="text-3xl font-bold mb-4">{legislation.title}</h1>

      <div className="text-sm text-gray-600 mb-6 space-y-1">
        <p>
          <span className="font-medium">Sponsor:</span>{" "}
          {legislation.sponsor_name}
        </p>
        <p>
          <span className="font-medium">Date Introduced:</span>{" "}
          {format(new Date(legislation.date_introduced), "MMMM d, yyyy")}
        </p>
        <p>
          <span className="font-medium">Last Action:</span>{" "}
          {format(new Date(legislation.date_last_action), "MMMM d, yyyy")}
        </p>
        <p>
          <span className="font-medium">Session:</span>{" "}
          {legislation.session_number}
        </p>
      </div>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Summary</h2>
        <p className="text-gray-700 leading-relaxed">{legislation.summary}</p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Full Text</h2>
        <div className="prose max-w-none whitespace-pre-line text-gray-700 leading-relaxed">
          {legislation.full_text}
        </div>
      </section>

      {legislation.actions && legislation.actions.length > 0 && (
        <ActionTimeline actions={legislation.actions} />
      )}
    </div>
  );
}
