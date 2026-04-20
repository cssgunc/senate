import Link from "next/link";

type ContactCTAProps = {
  href?: string;
};

export default function ContactCTA({
  href = "/senators/contact",
}: ContactCTAProps) {
  return (
    <Link
      href={href}
      className="group block rounded-lg border border-slate-300 bg-white p-5 transition hover:bg-slate-50"
      aria-label="Contact your senator"
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-medium text-slate-700">Get Involved</p>
          <h2 className="text-xl font-semibold text-slate-900">
            Contact Your Senator
          </h2>
          <p className="mt-1 text-sm text-slate-700">
            Find your district representative and send your questions or
            concerns.
          </p>
        </div>
        <span className="inline-flex shrink-0 items-center justify-center rounded-md bg-slate-900 px-4 py-1.5 text-sm font-medium text-white transition group-hover:bg-slate-700">
          Find Contact Info
        </span>
      </div>
    </Link>
  );
}
