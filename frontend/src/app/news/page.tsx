import { Card } from "@/components/ui/card";
import { getNews } from "@/lib/api";
import type { News } from "@/types";
import { format } from "date-fns";
import Image from "next/image";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function NewsPage({
  searchParams,
}: {
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}) {
  const resolvedSearchParams = await searchParams;
  const pageParam = resolvedSearchParams.page;
  const page = parseInt(
    Array.isArray(pageParam) ? pageParam[0] : pageParam || "1",
    10,
  );
  const safePage = Number.isFinite(page) && page > 0 ? page : 1;
  const pageSize = 10;
  const newsData = await getNews(safePage, pageSize);
  const hasNextPage = safePage * pageSize < newsData.total;

  return (
    <div className="container mx-auto p-4">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {newsData.items.map((article: News) => (
          <Link href={`/news/${article.id}`} key={article.id}>
            <Card className="p-4 h-full transition-shadow hover:shadow-lg flex flex-col">
              <div className="relative w-full h-48 mb-4">
                <Image
                  src={article.image_url || "/UNClogo.png"}
                  alt={article.title}
                  fill
                  className="object-cover rounded-md"
                />
              </div>
              <h2 className="text-lg font-bold mb-2">{article.title}</h2>
              <p className="text-sm text-gray-600 mb-2 line-clamp-3">
                {article.summary}
              </p>
              <p className="text-xs text-gray-500 mt-auto">
                {format(new Date(article.date_published), "MMMM d, yyyy")}
              </p>
            </Card>
          </Link>
        ))}
      </div>

      <div className="flex justify-between items-center mt-8">
        {safePage > 1 ? (
          <Link
            href={`/news?page=${safePage - 1}`}
            className="px-4 py-2 bg-gray-100 rounded-md hover:bg-gray-200"
          >
            Previous
          </Link>
        ) : (
          <div className="px-4 py-2 bg-gray-50 text-gray-400 rounded-md cursor-not-allowed">
            Previous
          </div>
        )}

        <span className="font-medium">Page {safePage}</span>

        {hasNextPage ? (
          <Link
            href={`/news?page=${safePage + 1}`}
            className="px-4 py-2 bg-gray-100 rounded-md hover:bg-gray-200"
          >
            Next
          </Link>
        ) : (
          <div className="px-4 py-2 bg-gray-50 text-gray-400 rounded-md cursor-not-allowed">
            Next
          </div>
        )}
      </div>
    </div>
  );
}
