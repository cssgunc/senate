"use client";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { getMe, login } from "@/lib/admin-api";
import { useRouter, useSearchParams } from "next/navigation";
import { FormEvent, Suspense, useEffect, useState } from "react";

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

function AdminLoginContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [onyen, setOnyen] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isCheckingSession, setIsCheckingSession] = useState(true);
  const redirectTarget = resolveNextPath(searchParams.get("next"));

  const isFormValid = onyen.trim() !== "" && password !== "";

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

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);

    if (!isFormValid) {
      setError("Please enter your Onyen and password.");
      return;
    }

    setIsSubmitting(true);

    try {
      await login(onyen.trim(), password);
      router.replace(redirectTarget);
    } catch {
      setError("Invalid credentials. Please check your Onyen and password.");
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
          Sign in with your Onyen credentials to access the admin dashboard.
        </p>

        <form className="mt-6 space-y-4" onSubmit={handleSubmit}>
          <div className="space-y-1">
            <label
              className="text-sm font-medium text-slate-700"
              htmlFor="onyen"
            >
              Onyen
            </label>
            <Input
              id="onyen"
              name="onyen"
              type="text"
              autoComplete="username"
              value={onyen}
              onChange={(event) => setOnyen(event.target.value)}
              placeholder="onyen"
              required
            />
          </div>

          <div className="space-y-1">
            <label
              className="text-sm font-medium text-slate-700"
              htmlFor="password"
            >
              Password
            </label>
            <Input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </div>

          {error ? (
            <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              {error}
            </p>
          ) : null}

          <Button
            className="w-full"
            type="submit"
            disabled={isSubmitting || !isFormValid}
          >
            {isSubmitting ? "Signing in..." : "Sign in"}
          </Button>
        </form>
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
