import EmptyState from "@/components/ui/EmptyState";
import ErrorMessage from "@/components/ui/ErrorMessage";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { getCommittees } from "@/lib/api";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function CommitteesPage() {
  let committees;
  try {
    committees = await getCommittees();
  } catch {
    return (
      <div className="container mx-auto py-8">
        <h1 className="text-4xl font-bold mb-8">Committees</h1>
        <ErrorMessage message="Unable to load committees. Please try again." />
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-4xl font-bold mb-8">Committees</h1>
      {committees.length === 0 ? (
        <EmptyState
          message="No committees found."
          description="Committee information will appear here once available."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {committees.map((committee) => (
            <Card key={committee.id}>
              <CardHeader>
                <CardTitle>{committee.name}</CardTitle>
                <CardDescription className="line-clamp-2">
                  {committee.description}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm font-medium text-muted-foreground">
                  Chair: {committee.chair_name}
                </p>
              </CardContent>
              <CardFooter>
                <Button asChild>
                  <Link href={`/committees/${committee.id}`}>Learn More</Link>
                </Button>
              </CardFooter>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
