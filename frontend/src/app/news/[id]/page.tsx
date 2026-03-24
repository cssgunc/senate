import { ApiError, getNewsById } from "@/lib/api";
import { format } from "date-fns";
import Image from "next/image";
import { notFound } from "next/navigation";

export const dynamic = "force-dynamic";

export default async function NewsDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  let article;

  try {
    article = await getNewsById(id);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      notFound();
    }
    throw error;
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">{article.title}</h1>
      <div className="text-sm text-gray-600 mb-4">
        <p>By {article.author_name || "Unknown Author"}</p>
        <p>
          Published: {format(new Date(article.date_published), "MMMM d, yyyy")}
        </p>
        {article.date_last_edited && (
          <p>
            Last Edited:{" "}
            {format(new Date(article.date_last_edited), "MMMM d, yyyy")}
          </p>
        )}
      </div>
      {article.image_url && (
        <div className="relative w-full h-80 mb-4">
          <Image
            src={article.image_url}
            alt={article.title}
            fill
            className="object-cover rounded-md"
          />
        </div>
      )}
      <div className="prose max-w-none whitespace-pre-line">
        <p>{article.body}</p>
      </div>
    </div>
  );
}
