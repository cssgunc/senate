import { getNewsById } from "@/lib/api";
import { format } from "date-fns";
import { notFound } from "next/navigation";

export default async function NewsDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const article = await getNewsById(id);

  if (!article) {
    notFound();
  }

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">{article.title}</h1>
      <div className="text-sm text-gray-600 mb-4">
        <p>By {article.author || "Unknown Author"}</p>
        <p>
          Published: {format(new Date(article.date_published), "MMMM d, yyyy")}
        </p>
        {article.date_edited && (
          <p>
            Last Edited: {format(new Date(article.date_edited), "MMMM d, yyyy")}
          </p>
        )}
      </div>
      {article.image_url && (
        <div className="relative w-full h-64 mb-4">
          <img
            src={article.image_url}
            alt={article.title}
            className="object-cover w-full h-full rounded-md"
          />
        </div>
      )}
      <div className="prose max-w-none">
        <p>{article.body}</p>
      </div>
    </div>
  );
}
