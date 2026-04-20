"use client";

import { Footer } from "@/components/layout/Footer";
import { Header } from "@/components/layout/Header";

export function AppChrome({ children }: { children: React.ReactNode }) {
  return (
    <>
      <Header />
      <main id="main" className="flex-grow">
        {children}
      </main>
      <Footer />
    </>
  );
}
