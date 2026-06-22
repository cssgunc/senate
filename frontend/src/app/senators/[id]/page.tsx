import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ApiError, getSenatorById } from "@/lib/api";
import Link from "next/link";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

function initials(name: string) {
  return name
    .split(" ")
    .map((s) => s[0]?.toUpperCase() ?? "")
    .slice(0, 2)
    .join("");
}

export default async function SenatorDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const resolvedParams = await params;
  let senator;

  try {
    senator = await getSenatorById(resolvedParams.id);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }

  const fullName = `${senator.first_name} ${senator.last_name}`;

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div className="flex items-center gap-6">
        {senator.headshot_url ? (
          // eslint-disable-next-line @next/next/no-img-element
          <img
            src={senator.headshot_url}
            alt={fullName}
            className="w-24 h-24 rounded-full object-cover"
          />
        ) : (
          <div className="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center text-2xl font-semibold text-gray-700">
            {initials(fullName)}
          </div>
        )}
        <div>
          <h1 className="text-4xl font-bold">{fullName}</h1>
          {senator.email && (
            <a
              href={`mailto:${senator.email}`}
              className="text-primary hover:underline"
            >
              {senator.email}
            </a>
          )}
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-xl">Details</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <p>
            <span className="font-semibold">District:</span>{" "}
            {senator.district_id}
          </p>
          <p>
            <span className="font-semibold">Session:</span>{" "}
            {senator.session_number}
          </p>
          <p>
            <span className="font-semibold">Status:</span>{" "}
            {senator.is_active ? "Active" : "Inactive"}
          </p>
        </CardContent>
      </Card>

      <div>
        <h2 className="text-2xl font-bold mb-4">Committee Assignments</h2>
        <div className="border rounded-md">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Committee</TableHead>
                <TableHead>Role</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {senator.committees.map((c) => (
                <TableRow key={c.committee_id}>
                  <TableCell className="font-medium">
                    <Link
                      href={`/committees/${c.committee_id}`}
                      className="text-primary hover:underline"
                    >
                      {c.committee_name}
                    </Link>
                  </TableCell>
                  <TableCell>{c.role}</TableCell>
                </TableRow>
              ))}
              {senator.committees.length === 0 && (
                <TableRow>
                  <TableCell
                    colSpan={2}
                    className="text-center text-muted-foreground py-4"
                  >
                    No committee assignments.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </div>
    </div>
  );
}
