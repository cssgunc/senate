"use client";

import { Card } from "@/components/ui/card";
import type { CalendarEvent } from "@/types";
import {
  format,
  getDate,
  getDay,
  getDaysInMonth,
  startOfMonth,
} from "date-fns";
import { useMemo, useState } from "react";

interface CalendarWidgetProps {
  events: CalendarEvent[];
  compact?: boolean;
}

interface DayEvents {
  [key: number]: CalendarEvent[];
}

export default function CalendarWidget({
  events,
  compact = false,
}: CalendarWidgetProps) {
  const [selectedDate, setSelectedDate] = useState<number | null>(null);
  const [currentMonth, setCurrentMonth] = useState(new Date());

  const dayNames = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

  // Group events by date
  const eventsByDate = useMemo<DayEvents>(() => {
    const grouped: DayEvents = {};
    events.forEach((event) => {
      const date = new Date(event.start_datetime);
      const monthYear = format(date, "yyyy-MM");
      const currentMonthYear = format(currentMonth, "yyyy-MM");

      if (monthYear === currentMonthYear) {
        const day = getDate(date);
        if (!grouped[day]) {
          grouped[day] = [];
        }
        grouped[day].push(event);
      }
    });
    return grouped;
  }, [events, currentMonth]);

  const today = new Date();
  const isCurrentMonth =
    format(today, "yyyy-MM") === format(currentMonth, "yyyy-MM");
  const todayDate = isCurrentMonth ? getDate(today) : null;

  const firstDay = getDay(startOfMonth(currentMonth));
  const daysInMonth = getDaysInMonth(currentMonth);

  const days = [
    ...Array(firstDay).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => i + 1),
  ];

  const selectedDateEvents = selectedDate
    ? eventsByDate[selectedDate] || []
    : [];

  const goToPreviousMonth = () => {
    setCurrentMonth(
      (prev) => new Date(prev.getFullYear(), prev.getMonth() - 1),
    );
    setSelectedDate(null);
  };

  const goToNextMonth = () => {
    setCurrentMonth(
      (prev) => new Date(prev.getFullYear(), prev.getMonth() + 1),
    );
    setSelectedDate(null);
  };

  const handleDayClick = (day: number) => {
    setSelectedDate(selectedDate === day ? null : day);
  };

  const formatEventTime = (event: CalendarEvent) => {
    return format(new Date(event.start_datetime), "h:mm a");
  };

  if (compact) {
    return (
      <div className="w-full">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-xl font-bold">
            {format(currentMonth, "MMMM yyyy")}
          </h2>
          <div className="flex gap-2">
            <button
              onClick={goToPreviousMonth}
              className="px-3 py-1 rounded border border-gray-300 text-sm hover:bg-gray-100"
              aria-label="Previous month"
            >
              ←
            </button>
            <button
              onClick={goToNextMonth}
              className="px-3 py-1 rounded border border-gray-300 text-sm hover:bg-gray-100"
              aria-label="Next month"
            >
              →
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow">
          <div className="grid grid-cols-7 gap-2 p-4">
            {dayNames.map((day) => (
              <div key={day} className="text-center text-sm font-semibold">
                {day}
              </div>
            ))}
          </div>

          <div className="grid grid-cols-7 gap-2 p-4 border-t">
            {days.map((day, index) => (
              <div
                key={index}
                className={`relative aspect-square flex items-center justify-center text-sm cursor-pointer rounded ${
                  day === null
                    ? "text-gray-300"
                    : selectedDate === day
                      ? "bg-blue-500 text-white font-bold"
                      : day === todayDate
                        ? "bg-blue-600 text-white font-bold ring-2 ring-blue-400"
                        : eventsByDate[day]
                          ? "bg-blue-50 border-2 border-blue-300"
                          : "hover:bg-gray-50"
                }`}
                onClick={() => day !== null && handleDayClick(day)}
              >
                {day}
                {day !== null && eventsByDate[day] && (
                  <div className="absolute bottom-1 h-1 w-1 bg-blue-500 rounded-full"></div>
                )}
              </div>
            ))}
          </div>

          {selectedDateEvents.length > 0 && (
            <div className="border-t p-4">
              <h3 className="font-semibold mb-2">
                {format(
                  new Date(
                    currentMonth.getFullYear(),
                    currentMonth.getMonth(),
                    selectedDate!,
                  ),
                  "MMM d",
                )}
              </h3>
              <div className="space-y-2 max-h-48 overflow-y-auto">
                {selectedDateEvents.map((event) => (
                  <div
                    key={event.id}
                    className="text-sm p-2 bg-blue-50 rounded border border-blue-200"
                  >
                    <p className="font-medium truncate">{event.title}</p>
                    <p className="text-xs text-gray-600">
                      {formatEventTime(event)}
                    </p>
                    {event.location && (
                      <p className="text-xs text-gray-600">{event.location}</p>
                    )}
                    <p className="text-xs text-gray-600">{event.event_type}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Full page version
  return (
    <div className="w-full">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-3xl font-bold">
          {format(currentMonth, "MMMM yyyy")}
        </h1>
        <div className="flex gap-2">
          <button
            onClick={goToPreviousMonth}
            className="px-4 py-2 rounded border border-gray-300 text-sm hover:bg-gray-100 font-medium"
            aria-label="Previous month"
          >
            ← Previous
          </button>
          <button
            onClick={goToNextMonth}
            className="px-4 py-2 rounded border border-gray-300 text-sm hover:bg-gray-100 font-medium"
            aria-label="Next month"
          >
            Next →
          </button>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow-lg overflow-hidden">
        <div className="grid grid-cols-7 gap-0 border-b">
          {dayNames.map((day) => (
            <div
              key={day}
              className="bg-gray-100 px-4 py-3 text-center font-semibold text-sm border-r last:border-r-0"
            >
              {day}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-7 border-b">
          {days.map((day, index) => (
            <div
              key={index}
              className={`min-h-[8rem] p-3 border-r border-b cursor-pointer transition-colors last:border-r-0 ${
                day === null
                  ? "bg-gray-50"
                  : selectedDate === day
                    ? "bg-blue-50"
                    : "hover:bg-gray-50"
              }`}
              onClick={() => day !== null && handleDayClick(day)}
            >
              {day !== null && (
                <>
                  <div
                    className={`font-semibold text-lg mb-2 w-8 h-8 flex items-center justify-center rounded-full ${
                      day === todayDate
                        ? "bg-blue-600 text-white"
                        : ""
                    }`}
                  >
                    {day}
                  </div>
                  <div className="space-y-1">
                    {eventsByDate[day]?.slice(0, 3).map((event) => (
                      <div
                        key={event.id}
                        className="text-xs bg-blue-100 text-blue-800 p-1 rounded truncate hover:bg-blue-200"
                      >
                        {event.title}
                      </div>
                    ))}
                    {eventsByDate[day]?.length > 3 && (
                      <div className="text-xs text-gray-500 font-medium">
                        +{eventsByDate[day].length - 3} more
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          ))}
        </div>
      </div>

      {selectedDateEvents.length > 0 && (
        <div className="mt-6">
          <h2 className="text-2xl font-bold mb-4">
            Events on{" "}
            {format(
              new Date(
                currentMonth.getFullYear(),
                currentMonth.getMonth(),
                selectedDate!,
              ),
              "MMMM d, yyyy",
            )}
          </h2>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {selectedDateEvents.map((event) => (
              <Card
                key={event.id}
                className="p-6 hover:shadow-lg transition-shadow"
              >
                <h3 className="text-lg font-bold mb-2">{event.title}</h3>
                <div className="space-y-2 text-sm">
                  <p>
                    <span className="font-semibold">Time:</span>{" "}
                    {formatEventTime(event)} -{" "}
                    {format(new Date(event.end_datetime), "h:mm a")}
                  </p>
                  {event.location && (
                    <p>
                      <span className="font-semibold">Location:</span>{" "}
                      {event.location}
                    </p>
                  )}
                  <p>
                    <span className="font-semibold">Type:</span>{" "}
                    {event.event_type}
                  </p>
                  {event.description && (
                    <p className="text-gray-600">{event.description}</p>
                  )}
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
