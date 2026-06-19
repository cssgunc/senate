import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function SenatorNotFound() {
  return (
    <div className="container mx-auto py-20 text-center space-y-6 flex flex-col items-center justify-center">
      <h2 className="text-4xl font-bold">Senator Not Found</h2>
      <p className="text-xl text-muted-foreground">
        We couldn&apos;t find the senator you&apos;re looking for. They may no
        longer be active or the ID is incorrect.
      </p>
      <Button asChild>
        <Link href="/senators/roster">Return to Senator Roster</Link>
      </Button>
    </div>
  );
}
