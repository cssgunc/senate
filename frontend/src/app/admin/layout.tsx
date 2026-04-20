"use client";

import { Sidebar } from "@/components/admin/Sidebar";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { getMe, logout } from "@/lib/mock/admin-api";
import type { Account } from "@/types/admin";
import { Menu } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState } from "react";

function getLoginRedirectUrl(): string {
  if (typeof window === "undefined") {
    return "/admin/login";
  }

  const requestedPath = `${window.location.pathname}${window.location.search}`;
  const encodedTarget = encodeURIComponent(requestedPath);
  return `/admin/login?next=${encodedTarget}`;
}

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<Account | null>(null);
  const [isCheckingAuth, setIsCheckingAuth] = useState(true);
  const [mobileNavOpen, setMobileNavOpen] = useState(false);

  const isLoginRoute = pathname === "/admin/login";

  useEffect(() => {
    if (isLoginRoute) {
      setIsCheckingAuth(false);
      return;
    }

    let isMounted = true;

    async function verifySession() {
      try {
        const me = await getMe();
        if (isMounted) {
          setUser(me);
        }
      } catch {
        logout();
        if (isMounted) {
          router.replace(getLoginRedirectUrl());
        }
      } finally {
        if (isMounted) {
          setIsCheckingAuth(false);
        }
      }
    }

    verifySession();

    return () => {
      isMounted = false;
    };
  }, [isLoginRoute, router]);

  const handleLogout = () => {
    logout();
    router.push("/admin/login");
  };

  if (isLoginRoute) {
    return children;
  }

  if (isCheckingAuth) {
    return (
      <div className="grid min-h-screen place-items-center bg-slate-50">
        <p className="text-sm text-slate-600">Checking your session...</p>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <div className="flex min-h-screen">
        <aside className="hidden w-64 border-r border-slate-200 bg-white md:block">
          <Sidebar role={user.role} />
        </aside>

        <div className="flex min-h-screen min-w-0 flex-1 flex-col">
          <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3 md:px-6">
            <div className="flex items-center gap-3">
              <Sheet open={mobileNavOpen} onOpenChange={setMobileNavOpen}>
                <SheetTrigger asChild>
                  <Button
                    variant="outline"
                    size="icon"
                    className="md:hidden"
                    aria-label="Open navigation"
                  >
                    <Menu className="h-4 w-4" />
                  </Button>
                </SheetTrigger>
                <SheetContent side="left" className="w-[280px] p-0">
                  <Sidebar
                    role={user.role}
                    onNavigate={() => setMobileNavOpen(false)}
                  />
                </SheetContent>
              </Sheet>
              <h1 className="text-base font-semibold md:text-lg">
                Admin Dashboard
              </h1>
            </div>

            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className="text-sm font-medium">
                  {user.first_name} {user.last_name}
                </p>
                <p className="text-xs text-slate-500">{user.email}</p>
              </div>
              <span className="rounded-full bg-sky-100 px-2 py-1 text-xs font-semibold uppercase tracking-wide text-sky-900">
                {user.role}
              </span>
              <Button variant="outline" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </header>

          <main className="flex-1 p-4 md:p-6">{children}</main>
        </div>
      </div>
    </div>
  );
}
