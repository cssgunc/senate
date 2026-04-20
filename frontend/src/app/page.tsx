import CalendarWidget from "@/components/calendar/CalendarWidget";
import Carousel from "@/components/home/Carousel";
import ContactCTA from "@/components/home/ContactCTA";
import FinanceHearingButton from "@/components/home/FinanceHearingButton";
import RecentNews from "@/components/home/RecentNews";
import EmptyState from "@/components/ui/EmptyState";
import ErrorMessage from "@/components/ui/ErrorMessage";
import { getCarousel, getEvents, getFinanceHearings } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function Home() {
  let slides: Awaited<ReturnType<typeof getCarousel>> = [];
  let events: Awaited<ReturnType<typeof getEvents>> = [];
  let financeHearings: Awaited<ReturnType<typeof getFinanceHearings>> | null =
    null;
  let carouselError = false;
  let eventsError = false;
  let financeError = false;

  try {
    slides = await getCarousel();
  } catch {
    carouselError = true;
  }

  try {
    events = await getEvents();
  } catch {
    eventsError = true;
  }

  try {
    financeHearings = await getFinanceHearings();
  } catch {
    financeError = true;
  }

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
            <RecentNews />
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
              <CalendarWidget events={events} compact={true} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
