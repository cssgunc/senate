import CalendarWidget from "@/components/calendar/CalendarWidget";
import Carousel from "@/components/home/Carousel";
import RecentNews from "@/components/home/RecentNews";
import { getCarousel, getEvents } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function Home() {
  const slides = await getCarousel().catch(() => []);
  const events = await getEvents().catch(() => []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Carousel slides={slides} />
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-12">
          <div className="lg:col-span-2">
            <RecentNews />
          </div>
          <div>
            <CalendarWidget events={events} compact={true} />
          </div>
        </div>
      </div>
    </div>
  );
}
