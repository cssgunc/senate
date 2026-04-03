"use client";

import { useEffect, useState } from "react";

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
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    let isMounted = true;

    const loadPage = async () => {
      setIsLoading(true);
      setErrorMessage(null);

      try {
        const data = await getStaticPage(slug);
        if (!isMounted) {
          return;
        }
        setPage(data);
      } catch (error) {
        if (!isMounted) {
          return;
        }

        if (error instanceof ApiError && error.status === 404) {
          setErrorMessage(
            "This page does not have published content yet. Showing placeholder text for now.",
          );
        } else {
          setErrorMessage(
            "Unable to load page content right now. Showing placeholder text until the backend is ready.",
          );
        }
        setPage(null);
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    void loadPage();

    return () => {
      isMounted = false;
    };
  }, [slug]);

  if (isLoading) {
    return (
      <section>
        <h1>Loading...</h1>
        <p>Fetching page content.</p>
      </section>
    );
  }

  const title = page?.title || placeholderTitle;
  const body = page?.body || `<p>${placeholderBody}</p>`;

  return (
    <section>
      <h1>{title}</h1>
      {errorMessage ? <p>{errorMessage}</p> : null}
      <div
        // TODO: Add server-side sanitization before rendering user-managed HTML.
        dangerouslySetInnerHTML={{ __html: body }}
      />
    </section>
  );
}
