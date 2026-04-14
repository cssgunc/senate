import Link from "next/link";

type FinanceHearingButtonProps = {
  href?: string;
};

export default function FinanceHearingButton({
  href = "/funding/apply#finance-hearing-dates",
}: FinanceHearingButtonProps) {
  return (
    <Link
      href={href}
      className="block rounded-lg border border-slate-300 bg-white p-5 transition hover:bg-slate-50"
      aria-label="View available finance hearing dates"
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-medium text-slate-700">Funding Season</p>
          <h2 className="text-xl font-semibold text-slate-900">
            Schedule Your Finance Hearing
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            See open hearing dates and reserve a spot before they fill.
          </p>
        </div>
        <span className="inline-flex items-center justify-center rounded-md border border-slate-300 px-3 py-1.5 text-sm font-medium text-slate-800">
          View Dates
        </span>
      </div>
    </Link>
  );
}
