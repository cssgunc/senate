type Committee = {
  name: string;
  role: string;
};

type Senator = {
  id: number;
  full_name: string;
  district: string;
  email: string;
  headshot_url: string | null;
  committees: Committee[];
};

("use client");

import { useRouter } from "next/router";
import { useEffect, useState } from "react";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../../components/ui/table";

import { getSenators } from "../../lib/api";

export default function RosterPage() {
  const router = useRouter();

  const [senators, setSenators] = useState<Senator[]>([]);
  const [filtered, setFiltered] = useState<Senator[]>([]);
  const [search, setSearch] = useState("");

  const [sortField, setSortField] = useState<keyof Senator>("full_name");
  const [sortAsc, setSortAsc] = useState(true);

  useEffect(() => {
    async function fetchData() {
      const data = await getSenators();
      setSenators(data);
      setFiltered(data);
    }

    fetchData();
  }, []);

  useEffect(() => {
    const result = senators.filter((s) =>
      s.full_name.toLowerCase().includes(search.toLowerCase()),
    );
    setFiltered(result);
  }, [search, senators]);

  useEffect(() => {
    let sorted = [...filtered].sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];

      const normalize = (val: unknown) => {
        if (val == null) return "";
        if (Array.isArray(val)) {
          return val
            .map((item) =>
              typeof item === "object" && item !== null
                ? JSON.stringify(item)
                : String(item),
            )
            .join(", ");
        }
        return String(val);
      };

      const aStr = normalize(aVal).toLowerCase();
      const bStr = normalize(bVal).toLowerCase();

      const cmp = aStr.localeCompare(bStr);
      return sortAsc ? cmp : -cmp;
    });

    setFiltered(sorted);
  }, [sortField, sortAsc, filtered]);

  function formatCommittees(committees: Committee[]) {
    if (!committees) return "";

    return committees.map((c) => `${c.name} (${c.role})`).join(", ");
  }

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Senator Roster</h1>

      {/* SEARCH INPUT */}
      <input
        type="text"
        placeholder="Search senators..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="border p-2 mb-4 w-full"
      />

      {/* TABLE */}
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Photo</TableHead>

              <TableHead
                className="cursor-pointer"
                onClick={() => {
                  setSortField("full_name");
                  setSortAsc(!sortAsc);
                }}
              >
                Name
              </TableHead>

              <TableHead
                className="cursor-pointer"
                onClick={() => {
                  setSortField("district");
                  setSortAsc(!sortAsc);
                }}
              >
                District
              </TableHead>

              <TableHead>Committees</TableHead>
              <TableHead>Email</TableHead>
            </TableRow>
          </TableHeader>

          <TableBody>
            {filtered.map((senator) => (
              <TableRow
                key={senator.id}
                className="cursor-pointer"
                onClick={() => router.push(`/senators/${senator.id}`)}
              >
                {/* HEADSHOT */}
                <TableCell>
                  {senator.headshot_url ? (
                    <img
                      src={senator.headshot_url}
                      alt={senator.full_name}
                      className="w-8 h-8 rounded-full"
                    />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-gray-300 flex items-center justify-center text-xs">
                      {senator.full_name
                        .split(" ")
                        .map((n) => n[0])
                        .join("")}
                    </div>
                  )}
                </TableCell>

                {/* NAME */}
                <TableCell>{senator.full_name}</TableCell>

                {/* DISTRICT */}
                <TableCell>{senator.district}</TableCell>

                {/* COMMITTEES */}
                <TableCell>{formatCommittees(senator.committees)}</TableCell>

                {/* EMAIL */}
                <TableCell>{senator.email}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
