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
      className="group block rounded-lg border border-slate-300 bg-white p-5 transition hover:bg-slate-50"
      aria-label="Learn how to apply for organization funding"
    >
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-medium text-slate-700">Funding</p>
          <h2 className="text-xl font-semibold text-slate-900">
            Apply for Organization Funding
          </h2>
          <p className="mt-1 text-sm text-slate-600">
            See how to apply and what the finance hearing process involves.
          </p>
        </div>
        <span className="inline-flex shrink-0 items-center justify-center rounded-md bg-slate-900 px-4 py-1.5 text-sm font-medium text-white transition group-hover:bg-slate-700">
          Learn More
        </span>
      </div>
    </Link>
  );
}
