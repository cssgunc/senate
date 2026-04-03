import Link from "next/link";

export default function PreviousLeadershipPage() {
  return (
    <div className="max-w-3xl mx-auto px-6 py-12">
      <h1 className="text-3xl font-bold mb-4">Previous Senate Leadership</h1>
      <p className="text-gray-700 mb-6">
        Historical leadership records are not available yet. This page will show
        archived sessions once the backend exposes that data.
      </p>
      <Link
        href="/senators/leadership"
        className="inline-flex items-center rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-900 hover:bg-gray-50"
      >
        View current leadership
      </Link>
    </div>
  );
}
