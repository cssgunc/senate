// src/app/committees/[id]/not-found.tsx
import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function CommitteeNotFound() {
  return (
    <div className="container mx-auto py-20 text-center space-y-6 flex flex-col items-center justify-center">
      <h2 className="text-4xl font-bold">Committee Not Found</h2>
      <p className="text-xl text-muted-foreground">
        We couldn&apos;t find the committee you&apos;re looking for. It may have been dissolved or the ID is incorrect.
      </p>
      <Button asChild>
        <Link href="/committees">Return to All Committees</Link>
      </Button>
    </div>
  );
}
