"use client";

import { setToken } from "@/lib/token";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

function resolveNextPath(rawNext: string | null): string {
  if (!rawNext) {
    return "/admin";
  }

  // Prevent open redirects by only allowing internal admin paths.
  if (!rawNext.startsWith("/admin") || rawNext.startsWith("/admin/login")) {
    return "/admin";
  }

  return rawNext;
}

export default function SsoCallbackPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const hash = new URLSearchParams(window.location.hash.slice(1));
    const token = hash.get("token");

    if (!token) {
      setError("Sign-in did not complete. Please try again.");
      return;
    }

    setToken(token);
    router.replace(resolveNextPath(hash.get("next")));
  }, [router]);

  return (
    <section className="grid min-h-screen place-items-center bg-slate-50 px-6">
      <p className="text-sm text-slate-600">
        {error ?? "Finishing sign-in..."}
      </p>
    </section>
  );
}
