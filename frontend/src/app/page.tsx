import CalendarWidget from "@/components/calendar/CalendarWidget";
import Carousel from "@/components/home/Carousel";
import ContactCTA from "@/components/home/ContactCTA";
import FinanceHearingButton from "@/components/home/FinanceHearingButton";
import RecentNews from "@/components/home/RecentNews";
import EmptyState from "@/components/ui/EmptyState";
import ErrorMessage from "@/components/ui/ErrorMessage";
import {
  ApiError,
  getCarousel,
  getEvents,
  getFinanceHearings,
  getNews,
} from "@/lib/api";
import { financeHearingsToCalendarEvents } from "@/lib/calendar";

export default async function Home() {
  const [slidesResult, eventsResult, financeHearingsResult, newsResult] =
    await Promise.allSettled([
      getCarousel(),
      getEvents(),
      getFinanceHearings(),
      getNews(1, 3),
    ]);

  const slides = slidesResult.status === "fulfilled" ? slidesResult.value : [];
  const carouselError = slidesResult.status === "rejected";

  const events = eventsResult.status === "fulfilled" ? eventsResult.value : [];
  const eventsError = eventsResult.status === "rejected";

  let financeHearings: Awaited<ReturnType<typeof getFinanceHearings>> | null =
    null;
  let financeError = false;
  if (financeHearingsResult.status === "fulfilled") {
    financeHearings = financeHearingsResult.value;
  } else {
    const err = financeHearingsResult.reason;
    if (err instanceof ApiError && err.status === 404) {
      // no config row exists yet — valid empty state
    } else {
      financeError = true;
    }
  }

  const newsData = newsResult.status === "fulfilled" ? newsResult.value : null;
  const newsError = newsResult.status === "rejected";

  const calendarEvents = [
    ...events,
    ...(financeHearings
      ? financeHearingsToCalendarEvents(financeHearings.dates)
      : []),
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {carouselError ? (
        <div className="container mx-auto px-4 pt-6">
          <ErrorMessage message="Unable to load homepage highlights. Please try again." />
        </div>
      ) : (
        <Carousel slides={slides} />
      )}
      <div className="container mx-auto px-4 py-12">
        <div className={`mb-10 grid gap-4 ${(financeError || financeHearings?.is_active) ? "grid-cols-1 sm:grid-cols-2" : "grid-cols-1"}`}>
          {financeError ? (
            <ErrorMessage message="Unable to load finance hearing information. Please try again." />
          ) : financeHearings?.is_active ? (
            <FinanceHearingButton />
          ) : null}
          <ContactCTA />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          <div className="lg:col-span-2">
            <RecentNews newsData={newsData} error={newsError} />
          </div>
          <div>
            {eventsError ? (
              <ErrorMessage message="Unable to load upcoming meetings. Please try again." />
            ) : events.length === 0 ? (
              <EmptyState
                message="No upcoming meetings right now."
                description="Check back soon for the latest calendar updates."
              />
            ) : (
              <CalendarWidget events={calendarEvents} compact={true} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
