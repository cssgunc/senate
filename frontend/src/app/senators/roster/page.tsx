"use client";

import { fetchAPI } from "@/lib/api";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type CommitteeAssignmentDTO = {
  committee_name: string;
  role: string; // e.g. Member, Vice Chair
};

type SenatorDTO = {
  id: number;
  first_name: string;
  last_name: string;
  email: string | null;
  headshot_url: string | null;
  district_name?: string | null;
  committees?: CommitteeAssignmentDTO[];
};

function initials(name: string) {
  return name
    .split(" ")
    .map((s) => s[0]?.toUpperCase() ?? "")
    .slice(0, 2)
    .join("");
}

export default function SenatorRosterPage() {
  const [items, setItems] = useState<SenatorDTO[]>([]);
  const [query, setQuery] = useState("");
  const [sort, setSort] = useState<{
    key: "name" | "district";
    dir: "asc" | "desc";
  } | null>({ key: "name", dir: "asc" });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    const load = async () => {
      try {
        setLoading(true);
        const data = await fetchAPI<SenatorDTO[]>("/api/senators");
        if (!mounted) return;
        setItems(
          data.map((s) => ({
            ...s,
            district_name:
              (s as any).district_name ??
              (s as any).district ??
              s.district_name,
            committees: s.committees ?? (s as any).committee_assignments ?? [],
          })),
        );
      } catch (err) {
        // fallback to mock data if API not ready
        const mock: SenatorDTO[] = [
          {
            id: 1,
            first_name: "Alex",
            last_name: "Johnson",
            email: "alex.johnson@example.edu",
            headshot_url: null,
            district_name: "District 1",
            committees: [
              { committee_name: "Finance", role: "Member" },
              { committee_name: "Rules", role: "Vice Chair" },
            ],
          },
          {
            id: 2,
            first_name: "Sam",
            last_name: "Lee",
            email: "sam.lee@example.edu",
            headshot_url: null,
            district_name: "District 2",
            committees: [{ committee_name: "Health", role: "Chair" }],
          },
        ];
        setItems(mock);
        setError(null);
      } finally {
        setLoading(false);
      }
    };

    load();
    return () => {
      mounted = false;
    };
  }, []);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    let list = items.filter((s) => {
      if (!q) return true;
      const full = `${s.first_name} ${s.last_name}`.toLowerCase();
      return full.includes(q);
    });

    if (sort) {
      list = list.sort((a, b) => {
        if (sort.key === "name") {
          const na = `${a.first_name} ${a.last_name}`.toLowerCase();
          const nb = `${b.first_name} ${b.last_name}`.toLowerCase();
          return sort.dir === "asc"
            ? na.localeCompare(nb)
            : nb.localeCompare(na);
        }
        if (sort.key === "district") {
          const da = (a.district_name ?? "").toLowerCase();
          const db = (b.district_name ?? "").toLowerCase();
          return sort.dir === "asc"
            ? da.localeCompare(db)
            : db.localeCompare(da);
        }
        return 0;
      });
    }

    return list;
  }, [items, query, sort]);

  const toggleSort = (key: "name" | "district") => {
    if (!sort || sort.key !== key) {
      setSort({ key, dir: "asc" });
      return;
    }
    setSort({ key, dir: sort.dir === "asc" ? "desc" : "asc" });
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-4">Senator Roster</h1>

      <div className="mb-4 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <input
          placeholder="Search by name..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="w-full sm:w-1/3 border rounded px-3 py-2"
        />
        <div className="text-sm text-muted-foreground">
          {loading ? "Loading..." : `${filtered.length} results`}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full table-auto border-collapse">
          <thead>
            <tr className="text-left border-b">
              <th className="p-2">Headshot</th>
              <th
                className="p-2 cursor-pointer"
                onClick={() => toggleSort("name")}
              >
                Full name
              </th>
              <th
                className="p-2 cursor-pointer"
                onClick={() => toggleSort("district")}
              >
                District
              </th>
              <th className="p-2">Committees</th>
              <th className="p-2">Email</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((s) => (
              <tr key={s.id} className="border-b hover:bg-gray-50">
                <td className="p-2 align-middle">
                  {s.headshot_url ? (
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                      src={s.headshot_url}
                      alt={`${s.first_name} ${s.last_name}`}
                      className="w-10 h-10 rounded-full object-cover"
                    />
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-gray-200 flex items-center justify-center text-sm font-semibold text-gray-700">
                      {initials(`${s.first_name} ${s.last_name}`)}
                    </div>
                  )}
                </td>
                <td className="p-2 align-middle">
                  <Link
                    href={`/senators/${s.id}`}
                    className="text-blue-600 hover:underline"
                  >
                    {s.first_name} {s.last_name}
                  </Link>
                </td>
                <td className="p-2 align-middle">{s.district_name ?? "—"}</td>
                <td className="p-2 align-middle">
                  {s.committees && s.committees.length > 0
                    ? s.committees
                        .map((c) => `${c.committee_name} (${c.role})`)
                        .join(", ")
                    : "—"}
                </td>
                <td className="p-2 align-middle">{s.email ?? "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
