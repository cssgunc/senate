import { redirect } from "next/navigation";

export const dynamic = "force-dynamic";

export default function LegislationPage() {
  redirect("/legislation/search");
}
