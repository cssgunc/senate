"use client";

import { cn } from "@/lib/utils";

export const utilityLinks = [
  { title: "Accessibility", href: "https://www.unc.edu/about/accessibility/" },
  { title: "Events", href: "https://www.unc.edu/events/", desktopOnly: true },
  { title: "Libraries", href: "http://library.unc.edu/", desktopOnly: true },
  { title: "Maps", href: "https://maps.unc.edu/" },
  { title: "Departments", href: "https://www.unc.edu/a-z/" },
  {
    title: "ConnectCarolina",
    href: "https://connectcarolina.unc.edu/",
    desktopOnly: true,
  },
  { title: "UNC Search", href: "https://www.unc.edu/search", id: "unc-search" },
];

const compactUtilityTitles = new Set([
  "Accessibility",
  "Maps",
  "Departments",
  "UNC Search",
]);

export function UNCUtilityBar() {
  return (
    <div className="bg-slate-950 text-white">
      <div className="mx-auto flex w-full max-w-7xl flex-nowrap items-center gap-3 overflow-x-auto px-4 py-2.5 lg:justify-between lg:px-6">
        <a
          href="http://www.unc.edu/"
          className="flex min-w-0 flex-nowrap items-center gap-2.5 whitespace-nowrap transition-opacity hover:opacity-90 lg:gap-3"
        >
          <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full border border-white/15 bg-white/5 p-1.5 shadow-[0_0_0_1px_rgba(255,255,255,0.06)] lg:h-10 lg:w-10">
            <svg
              id="unc-interlocking-logo"
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 40 35"
              className="h-7 w-7 lg:h-8 lg:w-8"
              aria-hidden="true"
            >
              <path
                id="logo-fill"
                fill="currentColor"
                d="M33.3,22.5c-.3-1.6-.4-3.2-.4-4.9s.1-3.4.4-4.9c.9.7,1.7,1.4,2.2,2.3l3.8-3.8c-1.1-1.4-2.7-2.7-4.5-3.8.4-.9.8-1.7,1.3-2.4-1.5-.9-3.1-1.6-4.9-2.2-.4.8-.9,1.6-1.3,2.4-2.6-.8-5.6-1.3-8.7-1.3s-5.3.3-7.6,1l-2-2.3c-1.9.6-3.7,1.4-5.3,2.3h0c.4.8.9,1.6,1.3,2.4C3.4,9.8.7,13.5.7,17.5s2.7,7.7,6.9,10.2c-.4.9-.8,1.7-1.3,2.4,1.5.9,3.1,1.6,4.9,2.2.4-.8.9-1.6,1.3-2.4,2.6.8,5.6,1.3,8.7,1.3s5.3-.3,7.6-1l2,2.3c1.9-.6,3.7-1.4,5.3-2.3h0c-.4-.8-.9-1.5-1.3-2.4,1.8-1.1,3.3-2.3,4.5-3.8l-3.8-3.8c-.5.8-1.3,1.6-2.2,2.3h0ZM9.2,22.5c-1.9-1.4-3-3.1-3-4.9s1.1-3.6,3-4.9c.3,1.6.4,3.2.4,4.9s-.1,3.4-.4,4.9ZM21.2,25.8c-2.5,0-4.9-.3-7-.9.5-2.3.8-4.8.8-7.3s0-2-.1-3l9.7,11c-1.1.1-2.3.2-3.4.2h0ZM27.5,20.5l-9.7-11c1.1-.1,2.3-.2,3.4-.2,2.5,0,4.9.3,7,.9-.5,2.3-.8,4.7-.8,7.3s0,2,.1,3h0Z"
              />
            </svg>
          </span>
        </a>

        <div className="flex min-w-0 flex-nowrap items-center gap-0.5 overflow-x-auto lg:hidden">
          {utilityLinks
            .filter((link) => compactUtilityTitles.has(link.title))
            .map((link) => (
              <a
                key={link.title}
                href={link.href}
                id={link.id}
                className={cn(
                  "shrink-0 whitespace-nowrap rounded px-2 py-1.5 text-[9px] font-medium uppercase tracking-[0.08em] text-white/80 transition-colors hover:bg-white/10 hover:text-white",
                  link.desktopOnly ? "hidden xl:inline-flex" : "inline-flex",
                )}
              >
                {link.title}
              </a>
            ))}
        </div>

        <div className="hidden min-w-0 flex-nowrap items-center gap-0.5 lg:flex">
          {utilityLinks.map((link) => (
            <a
              key={link.title}
              href={link.href}
              id={link.id}
              className={cn(
                "shrink-0 whitespace-nowrap rounded px-2.5 py-1.5 text-[9px] font-medium uppercase tracking-[0.1em] text-white/80 transition-colors hover:bg-white/10 hover:text-white",
                link.desktopOnly ? "hidden xl:inline-flex" : "inline-flex",
              )}
            >
              {link.title}
            </a>
          ))}
        </div>
      </div>
    </div>
  );
}
