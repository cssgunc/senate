"use client";

import { cn } from "@/lib/utils";
import Link from "next/link";
import { usePathname } from "next/navigation";

export type AdminRole = "admin" | "staff";

interface NavItem {
  label: string;
  href: string;
  adminOnly?: boolean;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/admin" },
  { label: "News", href: "/admin/news" },
  { label: "Senators", href: "/admin/senators" },
  { label: "Leadership", href: "/admin/leadership" },
  { label: "Committees", href: "/admin/committees" },
  { label: "Legislation", href: "/admin/legislation" },
  { label: "Events", href: "/admin/events" },
  { label: "Carousel", href: "/admin/carousel" },
  { label: "Finance Hearings", href: "/admin/finance-hearings" },
  { label: "Staff", href: "/admin/staff" },
  { label: "Budget", href: "/admin/budget" },
  { label: "Static Pages", href: "/admin/static-pages" },
  { label: "Districts", href: "/admin/districts" },
  { label: "Accounts", href: "/admin/accounts", adminOnly: true },
];

interface SidebarProps {
  role: AdminRole;
  onNavigate?: () => void;
}

export function Sidebar({ role, onNavigate }: SidebarProps) {
  const pathname = usePathname();

  return (
    <nav className="h-full w-full overflow-y-auto p-4">
      <ul className="space-y-1">
        {NAV_ITEMS.filter((item) => !item.adminOnly || role === "admin").map(
          (item) => {
            const isActive =
              item.href === "/admin"
                ? pathname === "/admin"
                : pathname?.startsWith(item.href);

            return (
              <li key={item.href}>
                <Link
                  href={item.href}
                  onClick={onNavigate}
                  className={cn(
                    "block rounded-md px-3 py-2 text-sm font-medium transition-colors",
                    isActive
                      ? "bg-sky-100 text-sky-900"
                      : "text-slate-700 hover:bg-slate-100 hover:text-slate-900",
                  )}
                >
                  {item.label}
                </Link>
              </li>
            );
          },
        )}
      </ul>
    </nav>
  );
}
