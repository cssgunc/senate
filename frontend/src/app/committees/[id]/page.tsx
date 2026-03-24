// src/app/committees/[id]/page.tsx
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { ApiError, getCommitteeById } from "@/lib/api";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function CommitteeDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  // Await params for Next.js 15+
  const resolvedParams = await params;
  let committee;

  try {
    committee = await getCommitteeById(resolvedParams.id);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }

  return (
    <div className="container mx-auto py-8 space-y-8">
      <div>
        <h1 className="text-4xl font-bold">{committee.name}</h1>
        <p className="mt-4 text-lg text-muted-foreground">
          {committee.description}
        </p>
      </div>

      {/* Chair distinct visual highlighted card */}
      <Card className="bg-primary/5 border-primary/20">
        <CardHeader>
          <CardTitle className="text-xl">Committee Chair</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="font-semibold text-lg">{committee.chair_name}</p>
          <a
            href={`mailto:${committee.chair_email}`}
            className="text-primary hover:underline"
          >
            {committee.chair_email}
          </a>
        </CardContent>
      </Card>

      {/* Member Roster Table */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Member Roster</h2>
        <div className="border rounded-md">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Email</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {committee.members.map((member) => (
                <TableRow key={member.id}>
                  <TableCell className="font-medium">
                    {member.first_name} {member.last_name}
                  </TableCell>
                  <TableCell>
                    {member.committees[0]?.role ?? "Member"}
                  </TableCell>
                  <TableCell>
                    <a
                      href={`mailto:${member.email}`}
                      className="text-primary hover:underline"
                    >
                      {member.email}
                    </a>
                  </TableCell>
                </TableRow>
              ))}
              {committee.members.length === 0 && (
                <TableRow>
                  <TableCell
                    colSpan={3}
                    className="text-center text-muted-foreground py-4"
                  >
                    No active members found.
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
