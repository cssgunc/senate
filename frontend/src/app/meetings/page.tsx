import CalendarWidget from "@/components/calendar/CalendarWidget";
import { getEvents } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function MeetingsPage() {
  const events = await getEvents().catch(() => []);

  return (
    <section className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-12">
        <CalendarWidget events={events} compact={false} />
      </div>
    </section>
  );
}
