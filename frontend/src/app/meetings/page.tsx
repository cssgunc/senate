import CalendarWidget from "@/components/calendar/CalendarWidget";
import EmptyState from "@/components/ui/EmptyState";
import ErrorMessage from "@/components/ui/ErrorMessage";
import { getEvents } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function MeetingsPage() {
  let events: Awaited<ReturnType<typeof getEvents>> = [];
  let hasError = false;

  try {
    events = await getEvents();
  } catch {
    hasError = true;
  }

  if (hasError) {
    return (
      <section className="min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 py-12">
          <ErrorMessage message="Unable to load meetings. Please try again." />
        </div>
      </section>
    );
  }

  return (
    <section className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-12">
        {events.length === 0 ? (
          <EmptyState
            message="No meetings available right now."
            description="Check back soon for upcoming meeting dates and details."
          />
        ) : (
          <CalendarWidget events={events} compact={false} />
        )}
      </div>
    </section>
  );
}
