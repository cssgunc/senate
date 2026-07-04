import CalendarWidget from "@/components/calendar/CalendarWidget";
import EmptyState from "@/components/ui/EmptyState";
import ErrorMessage from "@/components/ui/ErrorMessage";
import { getEvents, getFinanceHearings } from "@/lib/api";
import { financeHearingsToCalendarEvents } from "@/lib/calendar";

export const dynamic = "force-dynamic";

export default async function MeetingsPage() {
  let events: Awaited<ReturnType<typeof getEvents>> = [];
  let financeHearings: Awaited<ReturnType<typeof getFinanceHearings>> | null =
    null;
  let hasError = false;

  try {
    events = await getEvents();
  } catch {
    hasError = true;
  }

  try {
    financeHearings = await getFinanceHearings();
  } catch {
    // Finance hearings are optional — tolerate failure and fall back to
    // showing only regular events.
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

  const calendarEvents = [
    ...events,
    ...(financeHearings
      ? financeHearingsToCalendarEvents(financeHearings.dates)
      : []),
  ];

  return (
    <section className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-12">
        {calendarEvents.length === 0 ? (
          <EmptyState
            message="No meetings available right now."
            description="Check back soon for upcoming meeting dates and details."
          />
        ) : (
          <CalendarWidget events={calendarEvents} compact={false} />
        )}
      </div>
    </section>
  );
}
