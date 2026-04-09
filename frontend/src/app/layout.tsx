import { AppChrome } from "@/components/layout/AppChrome";
import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Senate",
  description: "Senate application",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased flex flex-col min-h-screen">
        <AppChrome>{children}</AppChrome>
      </body>
    </html>
  );
}
