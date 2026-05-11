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
const contentClassName = [
  "mt-8 text-base leading-7 text-slate-700",
  "[&_a]:font-semibold [&_a]:text-slate-950 [&_a]:decoration-[#4B9CD3] [&_a]:decoration-2 [&_a]:underline [&_a]:underline-offset-4",
  "[&_a:hover]:text-[#1f5f85] [&_a:hover]:decoration-[#1f5f85]",
  "[&_a:focus-visible]:rounded-sm [&_a:focus-visible]:outline [&_a:focus-visible]:outline-2 [&_a:focus-visible]:outline-offset-2 [&_a:focus-visible]:outline-[#4B9CD3]",
  "[&_blockquote]:my-6 [&_blockquote]:border-l-4 [&_blockquote]:border-[#4B9CD3] [&_blockquote]:bg-slate-50 [&_blockquote]:px-4 [&_blockquote]:py-3 [&_blockquote]:text-slate-700",
  "[&_h2]:mb-3 [&_h2]:mt-8 [&_h2]:text-2xl [&_h2]:font-semibold [&_h2]:leading-tight [&_h2]:text-slate-950",
  "[&_h3]:mb-2 [&_h3]:mt-6 [&_h3]:text-xl [&_h3]:font-semibold [&_h3]:text-slate-950",
  "[&_li]:mb-2 [&_ol]:my-5 [&_ol]:list-decimal [&_ol]:pl-6 [&_p]:mb-5 [&_strong]:font-semibold [&_strong]:text-slate-950 [&_ul]:my-5 [&_ul]:list-disc [&_ul]:pl-6",
].join(" ");

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
    <section className="container mx-auto max-w-4xl px-4 py-12">
      <h1 className="text-4xl font-bold leading-tight text-slate-950 sm:text-5xl">
        {title}
      </h1>
      <HtmlContent
        html={body}
        className={`static-page-content ${contentClassName}`}
      />
    </section>
  );
}
