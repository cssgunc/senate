import { Card } from "@/components/ui/card";
import { getNews } from "@/lib/api";
import { IMAGE_PATHS } from "@/lib/imagePaths";
import type { News } from "@/types";
import { format } from "date-fns";
import Image from "next/image";
import Link from "next/link";

export default async function RecentNews() {
  let newsData;
  try {
    newsData = await getNews(1, 3);
  } catch {
    return (
      <div className="recent-news">
        <h2 className="text-2xl font-bold mb-4">Recent News</h2>
        <p className="text-sm text-gray-500">
          Unable to load recent news. Please check back soon.
        </p>
      </div>
    );
  }

  return (
    <div className="recent-news">
      <h2 className="text-2xl font-bold mb-4">Recent News</h2>
      {newsData.items.length === 0 ? (
        <p className="text-sm text-gray-500">No news articles yet.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {newsData.items.map((article: News, index) => {
            const fallbackImage =
              IMAGE_PATHS.newsFallbacks[
                index % IMAGE_PATHS.newsFallbacks.length
              ] || IMAGE_PATHS.newsFallback;

            return (
              <Link href={`/news/${article.id}`} key={article.id}>
                <Card className="p-4 h-full transition-shadow hover:shadow-lg flex flex-col">
                  <div className="relative w-full h-48 mb-4">
                    <Image
                      src={article.image_url || fallbackImage}
                      alt={article.title}
                      fill
                      className="object-cover rounded-md"
                    />
                  </div>
                  <h3 className="text-lg font-bold mb-2">{article.title}</h3>
                  <p className="text-sm text-gray-600 mb-2 line-clamp-3">
                    {article.summary}
                  </p>
                  <p className="text-xs text-gray-500 mt-auto">
                    {format(new Date(article.date_published), "MMMM d, yyyy")}
                  </p>
                </Card>
              </Link>
            );
          })}
        </div>
      )}
      <div className="mt-8 text-center">
        <Link
          href="/news"
          className="inline-flex items-center rounded-md bg-slate-900 px-5 py-2 text-sm font-medium text-white transition hover:bg-slate-700"
        >
          View All News
        </Link>
      </div>
    </div>
  );
}
