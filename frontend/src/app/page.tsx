import Carousel from "@/components/home/Carousel";
import RecentNews from "@/components/home/RecentNews";
import { getCarousel } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function Home() {
  const slides = await getCarousel().catch(() => []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Carousel slides={slides} />
      <div className="container mx-auto px-4 py-12">
        <RecentNews />
      </div>
    </div>
  );
}
