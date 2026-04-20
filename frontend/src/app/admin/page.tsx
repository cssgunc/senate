"use client";

import { AdminCard, AdminPageShell } from "@/components/admin/AdminPageShell";
import { getAdminEvents, getAdminNews, getAdminSenators } from "@/lib/admin-api";
import { getLegislation } from "@/lib/api";
import type { CalendarEvent } from "@/types";
import type { AdminNews } from "@/types/admin";
import Link from "next/link";
import { useEffect, useState } from "react";

interface Stats {
  activeSenators: number | null;
  legislation: number | null;
  upcomingEvents: number | null;
  publishedNews: number | null;
}

const STAT_CARDS = [
  { label: "Active Senators", key: "activeSenators" as const },
  { label: "Legislation", key: "legislation" as const },
  { label: "Upcoming Events", key: "upcomingEvents" as const },
  { label: "Published News", key: "publishedNews" as const },
];

function formatEventDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatNewsDate(iso: string) {
  return new Date(iso).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

export default function AdminPage() {
  const [stats, setStats] = useState<Stats>({
    activeSenators: null,
    legislation: null,
    upcomingEvents: null,
    publishedNews: null,
  });
  const [upcomingEvents, setUpcomingEvents] = useState<CalendarEvent[] | null>(null);
  const [recentNews, setRecentNews] = useState<AdminNews[] | null>(null);

  useEffect(() => {
    async function load() {
      const now = new Date();

      const [senatorsRes, legislationRes, eventsRes, newsRes] =
        await Promise.allSettled([
          getAdminSenators(1, 1, true),
          getLegislation({ page: 1, limit: 1 }),
          getAdminEvents(),
          getAdminNews(1, 5, true),
        ]);

      const upcoming =
        eventsRes.status === "fulfilled"
          ? eventsRes.value
              .filter((e) => new Date(e.start_datetime) >= now)
              .sort(
                (a, b) =>
                  new Date(a.start_datetime).getTime() -
                  new Date(b.start_datetime).getTime(),
              )
              .slice(0, 5)
          : null;

      setUpcomingEvents(upcoming);

      if (newsRes.status === "fulfilled") {
        setRecentNews(newsRes.value.items);
      }

      setStats({
        activeSenators:
          senatorsRes.status === "fulfilled" ? senatorsRes.value.total : null,
        legislation:
          legislationRes.status === "fulfilled"
            ? legislationRes.value.total
            : null,
        upcomingEvents: upcoming ? upcoming.length : null,
        publishedNews:
          newsRes.status === "fulfilled" ? newsRes.value.total : null,
      });
    }

    load();
  }, []);

  return (
    <AdminPageShell>
      <div>
        <h1 className="text-2xl font-semibold text-slate-900">Dashboard</h1>
        <p className="mt-1 text-sm text-slate-500">
          Welcome to the Senate admin dashboard.
        </p>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {STAT_CARDS.map(({ label, key }) => {
          const value = stats[key];
          return (
            <AdminCard key={key}>
              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                {label}
              </p>
              <p className="mt-2 text-3xl font-semibold text-slate-900">
                {value === null ? (
                  <span className="text-slate-300">—</span>
                ) : (
                  value
                )}
              </p>
            </AdminCard>
          );
        })}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <AdminCard>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-900">Upcoming Events</h2>
            <Link
              href="/admin/events"
              className="text-xs text-slate-400 hover:text-slate-600"
            >
              View all
            </Link>
          </div>
          {upcomingEvents === null ? (
            <p className="text-sm text-slate-400">Loading…</p>
          ) : upcomingEvents.length === 0 ? (
            <p className="text-sm text-slate-400">No upcoming events.</p>
          ) : (
            <ul className="divide-y divide-slate-100">
              {upcomingEvents.map((event) => (
                <li key={event.id} className="py-3 first:pt-0 last:pb-0">
                  <p className="text-sm font-medium text-slate-800">{event.title}</p>
                  <p className="mt-0.5 text-xs text-slate-400">
                    {formatEventDate(event.start_datetime)}
                    {event.location ? ` · ${event.location}` : ""}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </AdminCard>

        <AdminCard>
          <div className="mb-4 flex items-center justify-between">
            <h2 className="text-sm font-semibold text-slate-900">Recent News</h2>
            <Link
              href="/admin/news"
              className="text-xs text-slate-400 hover:text-slate-600"
            >
              View all
            </Link>
          </div>
          {recentNews === null ? (
            <p className="text-sm text-slate-400">Loading…</p>
          ) : recentNews.length === 0 ? (
            <p className="text-sm text-slate-400">No published news.</p>
          ) : (
            <ul className="divide-y divide-slate-100">
              {recentNews.map((article) => (
                <li key={article.id} className="py-3 first:pt-0 last:pb-0">
                  <p className="text-sm font-medium text-slate-800">{article.title}</p>
                  <p className="mt-0.5 text-xs text-slate-400">
                    {formatNewsDate(article.date_published)}
                  </p>
                </li>
              ))}
            </ul>
          )}
        </AdminCard>
      </div>
    </AdminPageShell>
  );
}
