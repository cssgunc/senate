import Link from "next/link";

export default function NewsNotFound() {
  return (
    <div className="container mx-auto px-4 py-16 text-center">
      <h1 className="text-3xl font-bold mb-3">Article Not Found</h1>
      <p className="text-gray-600 mb-6">
        The article you are looking for may have been removed or is not
        available yet.
      </p>
      <Link
        href="/news"
        className="inline-block px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
      >
        Back to All News
      </Link>
    </div>
  );
}
