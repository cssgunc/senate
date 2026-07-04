import type { CalendarEvent, FinanceHearingDate } from "@/types";

const FINANCE_HEARING_ID_OFFSET = 1000000;
const DEFAULT_DURATION_MINUTES = 30;

/**
 * Converts a finance hearing date into a synthetic CalendarEvent so it can
 * be rendered alongside regular events in CalendarWidget.
 */
export function financeHearingToCalendarEvent(
  hearing: FinanceHearingDate,
): CalendarEvent {
  const start = new Date(`${hearing.hearing_date}T${hearing.hearing_time}`);
  const end = new Date(start.getTime() + DEFAULT_DURATION_MINUTES * 60 * 1000);

  return {
    id: FINANCE_HEARING_ID_OFFSET + hearing.id,
    title: `Finance Hearing${hearing.is_full ? " (Full)" : ""}`,
    description: hearing.description,
    start_datetime: start.toISOString(),
    end_datetime: end.toISOString(),
    location: hearing.location,
    event_type: "Finance Hearing",
    is_published: true,
  };
}

export function financeHearingsToCalendarEvents(
  hearings: FinanceHearingDate[],
): CalendarEvent[] {
  return hearings.map(financeHearingToCalendarEvent);
}
