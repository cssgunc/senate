import crypto from "node:crypto";
import { NextRequest, NextResponse } from "next/server";

const INGEST_SECRET = process.env.ANALYTICS_INGEST_SECRET;
const API_BASE = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(
  /\/+$/,
  "",
);

function hashVisitor(ip: string, userAgent: string): string {
  const today = new Date().toISOString().slice(0, 10);
  return crypto
    .createHash("sha256")
    .update(`${ip}:${userAgent}:${today}`)
    .digest("hex")
    .slice(0, 32);
}

function refererHost(refererHeader: string | null): string | null {
  if (!refererHeader) return null;
  try {
    return new URL(refererHeader).hostname;
  } catch {
    return null;
  }
}

export function proxy(request: NextRequest) {
  const isPrefetch =
    request.headers.get("next-router-prefetch") === "1" ||
    request.headers.get("purpose") === "prefetch";

  if (INGEST_SECRET && !isPrefetch) {
    const ip = request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ?? "unknown";
    const userAgent = request.headers.get("user-agent") ?? "unknown";

    fetch(`${API_BASE}/api/analytics/pageview`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Analytics-Secret": INGEST_SECRET,
      },
      body: JSON.stringify({
        path: request.nextUrl.pathname,
        referrer_host: refererHost(request.headers.get("referer")),
        user_agent: userAgent,
        visitor_hash: hashVisitor(ip, userAgent),
      }),
    }).catch(() => {
      // Best-effort only — a failed analytics call must never block the page.
    });
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/((?!admin|api|_next/static|_next/image|favicon.ico).*)"],
};
