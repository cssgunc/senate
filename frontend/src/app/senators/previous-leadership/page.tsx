"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

interface LeadershipRecord {
  id: number;
  first_name: string;
  last_name: string;
  title: string;
  session_number: number;
  is_current: boolean;
}

interface GroupedBySession {
  [session: number]: LeadershipRecord[];
}

async function fetchAllLeadership(): Promise<LeadershipRecord[]> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const response = await fetch(`${apiUrl}/api/leadership/sessions/all`);
  if (!response.ok) {
    throw new Error("Failed to fetch leadership data");
  }
  return response.json();
}

function getSessionName(sessionNumber: number): string {
  const suffix =
    sessionNumber % 100 >= 11 && sessionNumber % 100 <= 13
      ? "th"
      : {
          1: "st",
          2: "nd",
          3: "rd",
        }[sessionNumber % 10] || "th";
  return `${sessionNumber}${suffix} Senate`;
}

export default function PreviousLeadershipPage() {
  const [leadership, setLeadership] = useState<GroupedBySession>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadData = async () => {
      try {
        setIsLoading(true);
        const data = await fetchAllLeadership();

        // Group by session number, maintaining order by descending session
        const grouped: GroupedBySession = {};
        data.forEach((leader) => {
          if (!grouped[leader.session_number]) {
            grouped[leader.session_number] = [];
          }
          grouped[leader.session_number].push(leader);
        });

        setLeadership(grouped);
        setError(null);
      } catch (err) {
        setError(
          err instanceof Error ? err.message : "Failed to load leadership data",
        );
        setLeadership({});
      } finally {
        setIsLoading(false);
      }
    };

    loadData();
  }, []);

  return (
    <div className="max-w-3xl mx-auto px-6 py-12">
      <h1 className="text-3xl font-bold mb-4">Previous Senate Leadership</h1>

      {isLoading && (
        <p className="text-gray-700 mb-6">Loading leadership records...</p>
      )}

      {error && (
        <div className="rounded-lg bg-red-50 p-4 mb-6">
          <p className="text-red-700">Error: {error}</p>
        </div>
      )}

      {!isLoading && Object.keys(leadership).length === 0 && !error && (
        <p className="text-gray-700 mb-6">
          No historical leadership records available yet.
        </p>
      )}

      {!isLoading && Object.keys(leadership).length > 0 && (
        <div className="space-y-8">
          {Object.entries(leadership)
            .sort(
              ([sessionA], [sessionB]) => Number(sessionB) - Number(sessionA),
            )
            .map(([session, leaders]) => (
              <div key={session}>
                <h2 className="text-xl font-bold mb-4 text-blue-700">
                  {getSessionName(Number(session))}
                </h2>
                <div className="space-y-3 pl-4 border-l-4 border-blue-200">
                  {leaders
                    .sort((a: LeadershipRecord, b: LeadershipRecord) =>
                      a.title.localeCompare(b.title),
                    )
                    .map((leader: LeadershipRecord) => (
                      <div key={leader.id} className="pb-2">
                        <p className="font-semibold text-gray-900">
                          {leader.first_name} {leader.last_name}
                        </p>
                        <p className="text-sm text-gray-600">{leader.title}</p>
                      </div>
                    ))}
                </div>
              </div>
            ))}
        </div>
      )}

      <div className="mt-8 pt-6 border-t border-gray-200">
        <Link
          href="/senators/leadership"
          className="inline-flex items-center rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-900 hover:bg-gray-50"
        >
          View current leadership
        </Link>
      </div>
    </div>
  );
}
