import StaticPage from "@/components/StaticPage";
import { getFinanceHearings } from "@/lib/api";

function formatHearingDate(dateString: string): string {
  const parsed = new Date(`${dateString}T12:00:00`);
  if (Number.isNaN(parsed.getTime())) return dateString;
  return new Intl.DateTimeFormat("en-US", {
    weekday: "short",
    month: "long",
    day: "numeric",
    year: "numeric",
  }).format(parsed);
}

function formatHearingTime(timeString: string): string {
  const [hoursRaw, minutesRaw] = timeString.split(":");
  const hours = Number(hoursRaw);
  const minutes = Number(minutesRaw);

  if (
    Number.isNaN(hours) ||
    Number.isNaN(minutes) ||
    hours < 0 ||
    hours > 23 ||
    minutes < 0 ||
    minutes > 59
  ) {
    return timeString;
  }

  const period = hours >= 12 ? "PM" : "AM";
  const twelveHour = hours % 12 || 12;
  return `${twelveHour}:${minutes.toString().padStart(2, "0")} ${period}`;
}

export default async function FundingApplyPage() {
  const hearingConfig = await getFinanceHearings().catch(() => null);
  const hearingDates = [...(hearingConfig?.dates ?? [])].sort((a, b) => {
    const left = `${a.hearing_date} ${a.hearing_time}`;
    const right = `${b.hearing_date} ${b.hearing_time}`;
    return left.localeCompare(right);
  });

  return (
    <div className="space-y-10 pb-12">
      <StaticPage slug="how-to-apply" />

      <section
        id="finance-hearing-dates"
        className="container mx-auto px-4"
        aria-label="Finance hearing dates"
      >
        <div className="rounded-lg border border-slate-200 bg-white p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-2xl font-semibold text-slate-900">
              Finance Hearing Dates
            </h2>
            {hearingConfig?.is_active ? (
              <span className="inline-flex items-center rounded-md border border-emerald-300 bg-emerald-50 px-3 py-1 text-xs font-medium text-emerald-700">
                Hearing Season Active
              </span>
            ) : (
              <span className="inline-flex items-center rounded-md border border-slate-300 bg-slate-50 px-3 py-1 text-xs font-medium text-slate-600">
                Currently Inactive
              </span>
            )}
          </div>

          {hearingDates.length === 0 ? (
            <p className="mt-4 text-slate-600">
              No finance hearing dates are available right now.
            </p>
          ) : (
            <ul className="mt-5 space-y-3">
              {hearingDates.map((item) => (
                <li
                  key={item.id}
                  className="rounded-md border border-slate-200 bg-white p-4"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div>
                      <p className="text-base font-medium text-slate-900">
                        {formatHearingDate(item.hearing_date)} at{" "}
                        {formatHearingTime(item.hearing_time)}
                      </p>
                      <p className="mt-1 text-sm text-slate-700">
                        {item.location || "Location TBD"}
                      </p>
                      {item.description ? (
                        <p className="mt-1 text-sm text-slate-600">
                          {item.description}
                        </p>
                      ) : null}
                    </div>
                    {item.is_full ? (
                      <span className="inline-flex items-center rounded-md border border-amber-300 bg-amber-50 px-3 py-1 text-xs font-medium text-amber-800">
                        Full
                      </span>
                    ) : null}
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </div>
  );
}
