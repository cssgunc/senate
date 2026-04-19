"use client";

export const dynamic = "force-dynamic";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ApiError, getLegislation } from "@/lib/api";
import type { Legislation } from "@/types";
import type { PaginatedResponse } from "@/types/api";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense, useCallback, useEffect, useRef, useState } from "react";

const STATUS_OPTIONS = ["Introduced", "In Committee", "Passed", "Failed"];
const TYPE_OPTIONS = ["Bill", "Resolution", "Nomination"];
const ALL_FILTER_VALUE = "all";

function LegislationSearchContent() {
  const router = useRouter();
  const searchParams = useSearchParams();

  // Form state
  const [search, setSearch] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [status, setStatus] = useState("");
  const [type, setType] = useState("");
  const [session, setSession] = useState("");
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(20);

  // Results state
  const [data, setData] = useState<PaginatedResponse<Legislation> | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const requestIdRef = useRef(0);

  // Initialize form state from URL params
  useEffect(() => {
    const searchParam = searchParams.get("search") || "";
    const statusParam = searchParams.get("status") || "";
    const typeParam = searchParams.get("type") || "";
    const sessionParam = searchParams.get("session") || "";
    const pageParam = parseInt(searchParams.get("page") || "1", 10);
    const limitParam = parseInt(searchParams.get("limit") || "20", 10);
    const safePage = Number.isNaN(pageParam) ? 1 : pageParam;
    const safeLimit = Number.isNaN(limitParam) ? 20 : limitParam;

    setSearch(searchParam);
    setDebouncedSearch(searchParam);
    setStatus(statusParam);
    setType(typeParam);
    setSession(sessionParam);
    setPage(Math.max(1, safePage));
    setLimit(Math.max(1, safeLimit));
  }, [searchParams]);

  // Debounce the text search before syncing URL / querying API.
  useEffect(() => {
    const timeout = setTimeout(() => {
      setDebouncedSearch(search);
    }, 300);

    return () => clearTimeout(timeout);
  }, [search]);

  // Fetch legislation when params change
  useEffect(() => {
    const fetchLegislation = async () => {
      const requestId = ++requestIdRef.current;
      setIsLoading(true);
      setError(null);

      const parsedSession = session ? parseInt(session, 10) : undefined;

      try {
        const result = await getLegislation({
          search: debouncedSearch || undefined,
          status: status || undefined,
          type: type || undefined,
          session:
            parsedSession !== undefined && !Number.isNaN(parsedSession)
              ? parsedSession
              : undefined,
          page,
          limit,
        });
        if (requestId === requestIdRef.current) {
          setData(result);
        }
      } catch (err) {
        if (requestId !== requestIdRef.current) {
          return;
        }
        if (err instanceof ApiError) {
          setError(`Failed to fetch legislation: ${err.message}`);
        } else {
          setError("An unexpected error occurred");
        }
      } finally {
        if (requestId === requestIdRef.current) {
          setIsLoading(false);
        }
      }
    };

    fetchLegislation();
  }, [debouncedSearch, status, type, session, page, limit]);

  // Update URL when filters change
  const updateSearchParams = useCallback(
    (updates: Record<string, string>) => {
      const params = new URLSearchParams(searchParams);

      Object.entries(updates).forEach(([key, value]) => {
        if (value) {
          params.set(key, value);
        } else {
          params.delete(key);
        }
      });

      // Reset to page 1 when filters change
      params.set("page", "1");
      router.replace(`?${params.toString()}`);
    },
    [searchParams, router],
  );

  // Keep URL search param synchronized, but only after debounce settles.
  useEffect(() => {
    const urlSearch = searchParams.get("search") || "";
    if (urlSearch === debouncedSearch) {
      return;
    }

    updateSearchParams({ search: debouncedSearch });
  }, [debouncedSearch, searchParams, updateSearchParams]);

  // Handle search input
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearch(value);
  };

  // Handle filter dropdown changes
  const handleStatusChange = (value: string) => {
    const normalizedValue = value === ALL_FILTER_VALUE ? "" : value;
    setStatus(normalizedValue);
    updateSearchParams({ status: normalizedValue });
  };

  const handleTypeChange = (value: string) => {
    const normalizedValue = value === ALL_FILTER_VALUE ? "" : value;
    setType(normalizedValue);
    updateSearchParams({ type: normalizedValue });
  };

  const handleSessionChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSession(value);
    updateSearchParams({ session: value });
  };

  // Handle pagination
  const handlePreviousPage = () => {
    if (page > 1) {
      const newPage = page - 1;
      setPage(newPage);
      const params = new URLSearchParams(searchParams);
      params.set("page", String(newPage));
      router.push(`?${params.toString()}`);
    }
  };

  const handleNextPage = () => {
    if (data && page * limit < data.total) {
      const newPage = page + 1;
      setPage(newPage);
      const params = new URLSearchParams(searchParams);
      params.set("page", String(newPage));
      router.push(`?${params.toString()}`);
    }
  };

  const hasNextPage = data ? page * limit < data.total : false;

  return (
    <div className="container mx-auto py-8 space-y-6">
      <div>
        <h1 className="text-4xl font-bold">Legislation Search</h1>
        <p className="text-lg text-muted-foreground mt-2">
          Search and filter Senate legislation
        </p>
      </div>

      {/* Search and Filter Card */}
      <Card>
        <CardHeader>
          <CardTitle>Search & Filter</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Search Input */}
          <div>
            <label className="block text-sm font-medium mb-2">
              Search (Title, Bill Number, Summary)
            </label>
            <Input
              placeholder="Search legislation..."
              value={search}
              onChange={handleSearchChange}
              className="w-full"
            />
          </div>

          {/* Filters Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Status Filter */}
            <div>
              <label className="block text-sm font-medium mb-2">Status</label>
              <Select
                value={status || ALL_FILTER_VALUE}
                onValueChange={handleStatusChange}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="All Statuses" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={ALL_FILTER_VALUE}>All Statuses</SelectItem>
                  {STATUS_OPTIONS.map((opt) => (
                    <SelectItem key={opt} value={opt}>
                      {opt}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Type Filter */}
            <div>
              <label className="block text-sm font-medium mb-2">Type</label>
              <Select
                value={type || ALL_FILTER_VALUE}
                onValueChange={handleTypeChange}
              >
                <SelectTrigger className="w-full">
                  <SelectValue placeholder="All Types" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value={ALL_FILTER_VALUE}>All Types</SelectItem>
                  {TYPE_OPTIONS.map((opt) => (
                    <SelectItem key={opt} value={opt}>
                      {opt}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Session Filter */}
            <div>
              <label className="block text-sm font-medium mb-2">Session</label>
              <Input
                type="number"
                placeholder="Session number"
                value={session}
                onChange={handleSessionChange}
                min="1"
                className="w-full"
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Results Section */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="pt-6">
            <p className="text-red-800">{error}</p>
          </CardContent>
        </Card>
      )}

      {isLoading ? (
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">
              Loading legislation...
            </p>
          </CardContent>
        </Card>
      ) : data && data.items.length > 0 ? (
        <>
          {/* Results Count */}
          <div className="text-sm text-muted-foreground">
            Showing {(page - 1) * limit + 1} to{" "}
            {Math.min(page * limit, data.total)} of {data.total} results
          </div>

          {/* Table */}
          <Card>
            <CardContent className="p-0">
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Bill Number</TableHead>
                      <TableHead>Title</TableHead>
                      <TableHead>Sponsor</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Date Introduced</TableHead>
                      <TableHead className="text-right">Action</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.items.map((legislation) => (
                      <TableRow key={legislation.id}>
                        <TableCell className="font-medium">
                          {legislation.bill_number}
                        </TableCell>
                        <TableCell className="max-w-sm truncate">
                          {legislation.title}
                        </TableCell>
                        <TableCell>{legislation.sponsor_name}</TableCell>
                        <TableCell>
                          <span
                            className={`px-2 py-1 rounded-full text-xs font-medium ${
                              legislation.status === "Passed"
                                ? "bg-green-100 text-green-800"
                                : legislation.status === "Failed"
                                  ? "bg-red-100 text-red-800"
                                  : legislation.status === "In Committee"
                                    ? "bg-yellow-100 text-yellow-800"
                                    : "bg-blue-100 text-blue-800"
                            }`}
                          >
                            {legislation.status}
                          </span>
                        </TableCell>
                        <TableCell>
                          {new Date(
                            `${legislation.date_introduced}T00:00:00Z`,
                          ).toLocaleDateString("en-US", {
                            month: "short",
                            day: "numeric",
                            year: "numeric",
                            timeZone: "UTC",
                          })}
                        </TableCell>
                        <TableCell className="text-right">
                          <Button
                            asChild
                            className="text-right border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground text-foreground px-3 py-1 space-x-0 h-8 rounded-md text-xs"
                          >
                            <Link href={`/legislation/${legislation.id}`}>
                              View
                            </Link>
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>

          {/* Pagination Controls */}
          <div className="flex justify-between items-center gap-4">
            <Button
              onClick={handlePreviousPage}
              disabled={page === 1}
              className={
                page === 1
                  ? "hover:bg-accent hover:text-accent-foreground bg-transparent text-foreground"
                  : "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground text-foreground"
              }
            >
              Previous
            </Button>

            <span className="text-sm font-medium">Page {page}</span>

            <Button
              onClick={handleNextPage}
              disabled={!hasNextPage}
              className={
                !hasNextPage
                  ? "hover:bg-accent hover:text-accent-foreground bg-transparent text-foreground"
                  : "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground text-foreground"
              }
            >
              Next
            </Button>
          </div>
        </>
      ) : (
        <Card>
          <CardContent className="pt-6">
            <p className="text-center text-muted-foreground">
              No legislation found matching your filters.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

export default function LegislationPage() {
  return (
    <Suspense
      fallback={
        <div className="container mx-auto py-8">
          <p className="text-center text-muted-foreground">Loading...</p>
        </div>
      }
    >
      <LegislationSearchContent />
    </Suspense>
  );
}
