"use client";

import { useEffect, useState } from "react";

import { HtmlContent } from "@/components/content/HtmlContent";
import { ApiError, getStaticPage } from "@/lib/api";
import type { StaticPage as StaticPageContent } from "@/types";

interface StaticPageProps {
  slug: string;
}

const placeholderTitle = "Content Coming Soon";
const placeholderBody =
  "This page is being prepared. Please check back soon for the latest information.";

export default function StaticPage({ slug }: StaticPageProps) {
  const [page, setPage] = useState<StaticPageContent | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const loadPage = async () => {
      setIsLoading(true);

      try {
        const data = await getStaticPage(slug);
        if (isMounted) setPage(data);
      } catch (error) {
        if (!isMounted) return;
        if (!(error instanceof ApiError && error.status === 404)) {
          console.error("Failed to load static page:", slug, error);
        }
        setPage(null);
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };

    void loadPage();

    return () => {
      isMounted = false;
    };
  }, [slug]);

  if (isLoading) {
    return <section aria-busy="true" />;
  }

  const title = page?.title || placeholderTitle;
  const body = page?.body || `<p>${placeholderBody}</p>`;

  return (
    <section>
      <h1>{title}</h1>
      <HtmlContent html={body} />
    </section>
  );
}
