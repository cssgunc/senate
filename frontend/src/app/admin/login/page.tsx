"use client";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { devLogin, getMe, samlLoginUrl } from "@/lib/admin-api";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, Suspense, useEffect, useState } from "react";

const IS_DEV = process.env.NODE_ENV !== "production";

function resolveNextPath(rawNext: string | null): string {
  if (!rawNext) {
    return "/admin";
  }

  // Prevent open redirects by only allowing internal admin paths, and never
  // loop back into an auth-flow page itself.
  if (
    !rawNext.startsWith("/admin") ||
    rawNext.startsWith("/admin/login") ||
    rawNext.startsWith("/admin/sso-callback")
  ) {
    return "/admin";
  }

  return rawNext;
}

function AdminLoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [devOnyen, setDevOnyen] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isCheckingSession, setIsCheckingSession] = useState(true);
  const redirectTarget = resolveNextPath(searchParams.get("next"));

  useEffect(() => {
    if (searchParams.get("error") === "no_access") {
      setError(
        "Your UNC account signed in, but it isn't on the admin allowlist. Contact an admin to be added.",
      );
    }
  }, [searchParams]);

  useEffect(() => {
    let isMounted = true;

    async function checkExistingSession() {
      try {
        await getMe();
        if (isMounted) {
          router.replace(redirectTarget);
        }
      } catch {
        if (isMounted) {
          setIsCheckingSession(false);
        }
      }
    }

    checkExistingSession();

    return () => {
      isMounted = false;
    };
  }, [redirectTarget, router]);

  const handleSsoLogin = () => {
    const url = new URL(samlLoginUrl());
    url.searchParams.set("next", redirectTarget);
    window.location.href = url.toString();
  };

  const handleDevSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (!devOnyen.trim()) {
      setError("Please enter an Onyen.");
      return;
    }

    setIsSubmitting(true);

    try {
      await devLogin(devOnyen.trim());
      router.replace(redirectTarget);
    } catch {
      setError("No account found for that Onyen.");
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isCheckingSession) {
    return (
      <section className="grid min-h-screen place-items-center bg-slate-50 px-6">
        <p className="text-sm text-slate-600">Checking your session...</p>
      </section>
    );
  }

  return (
    <section className="mx-auto flex min-h-screen w-full max-w-md flex-col justify-center px-6">
      <Card className="bg-white p-6">
        <p className="text-xs uppercase tracking-[0.2em] text-slate-500">UNC</p>
        <h1 className="mt-2 text-2xl font-bold text-slate-900">Admin Login</h1>
        <p className="mt-2 text-sm text-slate-600">
          Sign in with your Onyen to access the admin dashboard.
        </p>

        {error ? (
          <p className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </p>
        ) : null}

        <Button className="mt-6 w-full" type="button" onClick={handleSsoLogin}>
          Log in with Onyen
        </Button>

        {IS_DEV ? (
          <div className="mt-6 border-t pt-6">
            <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
              Dev-only bypass
            </p>
            <p className="mt-1 text-xs text-slate-500">
              Not available in production. Logs in as any onyen already on the
              accounts allowlist, no SSO round-trip required.
            </p>
            <form className="mt-3 flex gap-2" onSubmit={handleDevSubmit}>
              <Input
                id="dev-onyen"
                name="dev-onyen"
                type="text"
                autoComplete="off"
                value={devOnyen}
                onChange={(event) => setDevOnyen(event.target.value)}
                placeholder="onyen"
              />
              <Button type="submit" variant="outline" disabled={isSubmitting}>
                {isSubmitting ? "Signing in..." : "Dev sign in"}
              </Button>
            </form>
          </div>
        ) : null}
      </Card>
    </section>
  );
}

export default function AdminLoginPage() {
  return (
    <Suspense
      fallback={
        <section className="grid min-h-screen place-items-center bg-slate-50 px-6">
          <p className="text-sm text-slate-600">Loading login page...</p>
        </section>
      }
    >
      <AdminLoginContent />
    </Suspense>
  );
}
