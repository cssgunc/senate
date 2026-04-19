"use client";

import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  createNews,
  getMe,
  login,
  logout,
} from "@/lib/admin-api";

type Status = {
  kind: "idle" | "success" | "error";
  message: string;
};

const initialStatus: Status = { kind: "idle", message: "" };

export default function AdminPage() {
  const [email, setEmail] = useState("");
  const [pid, setPid] = useState("");

  const [title, setTitle] = useState("");
  const [summary, setSummary] = useState("");
  const [body, setBody] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [isPublished, setIsPublished] = useState(false);

  const [authStatus, setAuthStatus] = useState<Status>(initialStatus);
  const [newsStatus, setNewsStatus] = useState<Status>(initialStatus);
  const [loadingAuth, setLoadingAuth] = useState(false);
  const [loadingNews, setLoadingNews] = useState(false);

  async function handleLogin(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoadingAuth(true);
    setAuthStatus(initialStatus);

    try {
      const result = await login(email, pid);
      setAuthStatus({
        kind: "success",
        message: `Logged in. Token saved (${result.access_token.slice(0, 10)}...)`,
      });
    } catch (error) {
      setAuthStatus({
        kind: "error",
        message: error instanceof Error ? error.message : "Login failed",
      });
    } finally {
      setLoadingAuth(false);
    }
  }

  async function handleWhoAmI() {
    setLoadingAuth(true);
    setAuthStatus(initialStatus);

    try {
      const me = await getMe();
      setAuthStatus({
        kind: "success",
        message: `Authenticated as ${me.first_name} ${me.last_name} (${me.role})`,
      });
    } catch (error) {
      setAuthStatus({
        kind: "error",
        message: error instanceof Error ? error.message : "Could not fetch account",
      });
    } finally {
      setLoadingAuth(false);
    }
  }

  function handleLogout() {
    logout();
    setAuthStatus({ kind: "success", message: "Token cleared. You are logged out." });
  }

  async function handleCreateNews(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setLoadingNews(true);
    setNewsStatus(initialStatus);

    try {
      await createNews({
        title,
        summary,
        body,
        image_url: imageUrl.trim() ? imageUrl : null,
        is_published: isPublished,
      });

      setNewsStatus({ kind: "success", message: "News article created successfully." });
      setTitle("");
      setSummary("");
      setBody("");
      setImageUrl("");
      setIsPublished(false);
    } catch (error) {
      setNewsStatus({
        kind: "error",
        message: error instanceof Error ? error.message : "Create news failed",
      });
    } finally {
      setLoadingNews(false);
    }
  }

  return (
    <section className="mx-auto max-w-3xl space-y-8 px-4 py-8">
      <div className="space-y-2">
        <h1 className="text-3xl font-semibold">Admin Dashboard</h1>
        <p className="text-sm text-muted-foreground">
          This page is a starter integration for auth and one mutation (create news).
        </p>
      </div>

      <div className="rounded-lg border bg-card p-6 shadow-sm">
        <h2 className="mb-4 text-xl font-medium">1) Login</h2>
        <form onSubmit={handleLogin} className="space-y-3">
          <div className="space-y-1">
            <label htmlFor="email" className="text-sm font-medium">
              Email
            </label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          <div className="space-y-1">
            <label htmlFor="pid" className="text-sm font-medium">
              PID
            </label>
            <Input
              id="pid"
              value={pid}
              onChange={(e) => setPid(e.target.value)}
              required
            />
          </div>
          <div className="flex flex-wrap gap-2">
            <Button type="submit" disabled={loadingAuth}>
              {loadingAuth ? "Signing in..." : "Login"}
            </Button>
            <Button type="button" variant="outline" onClick={handleWhoAmI} disabled={loadingAuth}>
              Check Me
            </Button>
            <Button type="button" variant="secondary" onClick={handleLogout}>
              Logout
            </Button>
          </div>
        </form>
        {authStatus.kind !== "idle" && (
          <p
            className={`mt-3 text-sm ${
              authStatus.kind === "error" ? "text-red-600" : "text-green-700"
            }`}
          >
            {authStatus.message}
          </p>
        )}
      </div>

      <div className="rounded-lg border bg-card p-6 shadow-sm">
        <h2 className="mb-4 text-xl font-medium">2) Create News</h2>
        <form onSubmit={handleCreateNews} className="space-y-3">
          <div className="space-y-1">
            <label htmlFor="title" className="text-sm font-medium">
              Title
            </label>
            <Input id="title" value={title} onChange={(e) => setTitle(e.target.value)} required />
          </div>
          <div className="space-y-1">
            <label htmlFor="summary" className="text-sm font-medium">
              Summary
            </label>
            <Input
              id="summary"
              value={summary}
              onChange={(e) => setSummary(e.target.value)}
              required
            />
          </div>
          <div className="space-y-1">
            <label htmlFor="body" className="text-sm font-medium">
              Body
            </label>
            <textarea
              id="body"
              className="min-h-32 w-full rounded-md border border-input bg-transparent px-3 py-2 text-sm"
              value={body}
              onChange={(e) => setBody(e.target.value)}
              required
            />
          </div>
          <div className="space-y-1">
            <label htmlFor="image_url" className="text-sm font-medium">
              Image URL (optional)
            </label>
            <Input
              id="image_url"
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
            />
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={isPublished}
              onChange={(e) => setIsPublished(e.target.checked)}
            />
            Publish immediately
          </label>
          <Button type="submit" disabled={loadingNews}>
            {loadingNews ? "Creating..." : "Create News"}
          </Button>
        </form>
        {newsStatus.kind !== "idle" && (
          <p
            className={`mt-3 text-sm ${
              newsStatus.kind === "error" ? "text-red-600" : "text-green-700"
            }`}
          >
            {newsStatus.message}
          </p>
        )}
      </div>
    </section>
  );
}
