"use client";

import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useRouter, useSearchParams } from "next/navigation";
import { useCallback, useState, useTransition } from "react";

const CURRENT_YEAR = new Date().getFullYear();
const YEARS = Array.from({ length: CURRENT_YEAR - 2018 }, (_, i) => CURRENT_YEAR - i);

export default function NewsSearchBar({
  initialSearch = "",
  initialYear = "",
}: {
  initialSearch?: string;
  initialYear?: string;
}) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [isPending, startTransition] = useTransition();
  const [search, setSearch] = useState(initialSearch);
  const [year, setYear] = useState(initialYear);

  const navigate = useCallback(
    (nextSearch: string, nextYear: string) => {
      const params = new URLSearchParams(searchParams.toString());
      params.set("page", "1");
      if (nextSearch) params.set("search", nextSearch); else params.delete("search");
      if (nextYear) params.set("year", nextYear); else params.delete("year");
      startTransition(() => router.push(`/news?${params.toString()}`));
    },
    [router, searchParams],
  );

  return (
    <div className={`mb-8 transition-opacity duration-150 ${isPending ? "opacity-50" : "opacity-100"}`}>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 shadow-sm">
        {/* Search input */}
        <div className="relative flex-1">
          <svg
            className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 pointer-events-none"
            xmlns="http://www.w3.org/2000/svg"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-4.35-4.35M17 11A6 6 0 1 1 5 11a6 6 0 0 1 12 0z" />
          </svg>
          <input
            type="search"
            placeholder="Search articles…"
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              navigate(e.target.value, year);
            }}
            className="w-full pl-9 pr-3 py-2 rounded-full border border-slate-200 bg-white text-sm text-slate-900 placeholder:text-slate-400 shadow-sm focus:outline-none focus:ring-2 focus:ring-slate-900 focus:border-transparent transition-shadow"
          />
        </div>

        {/* Divider */}
        <div className="hidden sm:block h-5 w-px bg-slate-200" />

        {/* Year filter */}
        <div className="flex items-center gap-2">
          <span className="text-xs font-semibold uppercase tracking-wide text-slate-500 whitespace-nowrap">
            Year
          </span>
          <Select
            value={year || "all"}
            onValueChange={(val) => {
              const next = val === "all" ? "" : val;
              setYear(next);
              navigate(search, next);
            }}
          >
            <SelectTrigger className="w-32 rounded-full border-slate-200 bg-white shadow-sm focus:ring-slate-900 text-sm">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All years</SelectItem>
              {YEARS.map((y) => (
                <SelectItem key={y} value={String(y)}>{y}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>
    </div>
  );
}
