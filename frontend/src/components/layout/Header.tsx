"use client";

import { UNCUtilityBar } from "@/components/layout/UNCUtilityBar";
import { Button } from "@/components/ui/button";
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
  navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";
import {
  Sheet,
  SheetContent,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { cn } from "@/lib/utils";
import { Menu } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import * as React from "react";

const senatorsItems = [
  { title: "Leadership", href: "/senators/leadership" },
  { title: "Roster", href: "/senators/roster" },
  { title: "Contact Your Senator", href: "/senators/contact" },
  { title: "Previous Leadership", href: "/senators/previous-leadership" },
];

const legislationItems = [
  { title: "Search", href: "/legislation/search" },
  { title: "Recent Legislation", href: "/legislation/recent" },
  { title: "Recent Nominations", href: "/legislation/nominations" },
  { title: "Senate Rules", href: "/legislation/rules" },
  { title: "Public Disclosure", href: "/legislation/disclosure" },
];

const aboutItems = [
  { title: "Staff", href: "/about/staff" },
  { title: "Powers of the Senate", href: "/about/powers" },
  {
    title: "Bill Process",
    href: "/about/bill-process",
  },
  { title: "Elections", href: "/elections" },
];

const fundingItems = [
  { title: "How to Apply", href: "/funding/apply" },
  { title: "Budget", href: "/funding/budget" },
  { title: "Where Does My Money Go?", href: "/funding/where-does-money-go" },
];

export function Header() {
  const [isOpen, setIsOpen] = React.useState(false);
  const pathname = usePathname();

  const isActive = (href: string) => pathname === href;
  const isActivePrefix = (prefix: string) => pathname.startsWith(prefix);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-200/80 bg-white/95 shadow-sm backdrop-blur supports-[backdrop-filter]:bg-white/80">
      <UNCUtilityBar />

      <div className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex w-full max-w-7xl items-center justify-between gap-3 px-4 py-3.5 lg:px-6">
          <Link href="/" className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-full border border-slate-300 bg-slate-100 shadow-sm overflow-hidden">
              <Image src="/USG logo.png" alt="USG Logo" width={44} height={44} className="object-contain" />
            </div>
            <span className="flex flex-col leading-tight">
              <span className="text-[10px] font-semibold uppercase tracking-[0.18em] text-slate-950 sm:text-sm sm:tracking-[0.22em]">
                Senate
              </span>
              <span className="text-[10px] text-slate-500 sm:text-xs">
                Undergraduate Senate
              </span>
            </span>
          </Link>

          <div className="hidden md:flex items-center gap-1">
            <NavigationMenu>
              <NavigationMenuList className="space-x-0 rounded-full border border-slate-200 bg-slate-50 p-1.5 shadow-sm">
                <NavigationMenuItem>
                  <NavigationMenuLink asChild active={isActive("/")}>
                    <Link
                      href="/"
                      className={cn(
                        navigationMenuTriggerStyle(),
                        "rounded-full bg-transparent px-4 text-slate-700 hover:bg-white hover:text-slate-950 focus:bg-white focus:text-slate-950 data-[active]:bg-white data-[state=open]:bg-white",
                      )}
                    >
                      Home
                    </Link>
                  </NavigationMenuLink>
                </NavigationMenuItem>

                <NavigationMenuItem>
                  <NavigationMenuLink asChild active={isActivePrefix("/news")}>
                    <Link
                      href="/news"
                      className={cn(
                        navigationMenuTriggerStyle(),
                        "rounded-full bg-transparent px-4 text-slate-700 hover:bg-white hover:text-slate-950 focus:bg-white focus:text-slate-950 data-[active]:bg-white data-[state=open]:bg-white",
                      )}
                    >
                      News
                    </Link>
                  </NavigationMenuLink>
                </NavigationMenuItem>

                <NavigationMenuItem>
                  <NavigationMenuTrigger className={cn("rounded-full bg-transparent px-4 text-slate-700 hover:bg-white hover:text-slate-950 focus:bg-white focus:text-slate-950 data-[active]:bg-white data-[state=open]:bg-white", isActivePrefix("/senators") && "bg-white text-slate-950")}>
                    Senators
                  </NavigationMenuTrigger>
                  <NavigationMenuContent>
                    <ul className="grid w-[380px] gap-3 overflow-hidden rounded-xl border border-slate-200 bg-white p-4 shadow-xl md:grid-cols-2 lg:w-[540px]">
                      {senatorsItems.map((item) => (
                        <ListItem
                          key={item.title}
                          title={item.title}
                          href={item.href}
                        />
                      ))}
                    </ul>
                  </NavigationMenuContent>
                </NavigationMenuItem>

                <NavigationMenuItem>
                  <NavigationMenuLink asChild active={isActivePrefix("/committees")}>
                    <Link
                      href="/committees"
                      className={cn(
                        navigationMenuTriggerStyle(),
                        "rounded-full bg-transparent px-4 text-slate-700 hover:bg-white hover:text-slate-950 focus:bg-white focus:text-slate-950 data-[active]:bg-white data-[state=open]:bg-white",
                      )}
                    >
                      Committees
                    </Link>
                  </NavigationMenuLink>
                </NavigationMenuItem>

                <NavigationMenuItem>
                  <NavigationMenuTrigger className={cn("rounded-full bg-transparent px-4 text-slate-700 hover:bg-white hover:text-slate-950 focus:bg-white focus:text-slate-950 data-[active]:bg-white data-[state=open]:bg-white", isActivePrefix("/legislation") && "bg-white text-slate-950")}>
                    Legislation
                  </NavigationMenuTrigger>
                  <NavigationMenuContent>
                    <ul className="grid w-[380px] gap-3 overflow-hidden rounded-xl border border-slate-200 bg-white p-4 shadow-xl md:grid-cols-2 lg:w-[540px]">
                      {legislationItems.map((item) => (
                        <ListItem
                          key={item.title}
                          title={item.title}
                          href={item.href}
                        />
                      ))}
                      <li>
                        <NavigationMenuLink asChild>
                          <a
                            href="https://drive.google.com/"
                            target="_blank"
                            rel="noopener noreferrer"
                            className="block select-none space-y-1 rounded-lg border border-transparent p-3 leading-none no-underline outline-none transition-colors hover:border-slate-200 hover:bg-slate-50 hover:text-slate-950 focus:border-slate-200 focus:bg-slate-50"
                            aria-label="Senate Archives (opens in a new tab)"
                          >
                            <div className="text-sm font-medium leading-none text-slate-900">
                              Senate Archives
                            </div>
                          </a>
                        </NavigationMenuLink>
                      </li>
                    </ul>
                  </NavigationMenuContent>
                </NavigationMenuItem>

                <NavigationMenuItem>
                  <NavigationMenuTrigger className={cn("rounded-full bg-transparent px-4 text-slate-700 hover:bg-white hover:text-slate-950 focus:bg-white focus:text-slate-950 data-[active]:bg-white data-[state=open]:bg-white", (isActivePrefix("/about") || isActive("/elections")) && "bg-white text-slate-950")}>
                    About
                  </NavigationMenuTrigger>
                  <NavigationMenuContent className="left-auto right-0">
                    <ul className="grid w-[380px] gap-3 overflow-hidden rounded-xl border border-slate-200 bg-white p-4 shadow-xl md:grid-cols-2 lg:w-[540px]">
                      {aboutItems.map((item) => (
                        <ListItem
                          key={item.title}
                          title={item.title}
                          href={item.href}
                        />
                      ))}
                    </ul>
                  </NavigationMenuContent>
                </NavigationMenuItem>

                <NavigationMenuItem>
                  <NavigationMenuTrigger className={cn("rounded-full bg-transparent px-4 text-slate-700 hover:bg-white hover:text-slate-950 focus:bg-white focus:text-slate-950 data-[active]:bg-white data-[state=open]:bg-white", isActivePrefix("/funding") && "bg-white text-slate-950")}>
                    Funding
                  </NavigationMenuTrigger>
                  <NavigationMenuContent className="left-auto right-0">
                    <ul className="grid w-[380px] gap-3 overflow-hidden rounded-xl border border-slate-200 bg-white p-4 shadow-xl md:grid-cols-2 lg:w-[540px]">
                      {fundingItems.map((item) => (
                        <ListItem
                          key={item.title}
                          title={item.title}
                          href={item.href}
                        />
                      ))}
                    </ul>
                  </NavigationMenuContent>
                </NavigationMenuItem>

                <NavigationMenuItem>
                  <NavigationMenuLink asChild active={isActivePrefix("/meetings")}>
                    <Link
                      href="/meetings"
                      className={cn(
                        navigationMenuTriggerStyle(),
                        "rounded-full bg-transparent px-4 text-slate-700 hover:bg-white hover:text-slate-950 focus:bg-white focus:text-slate-950 data-[active]:bg-white data-[state=open]:bg-white",
                      )}
                    >
                      Meetings
                    </Link>
                  </NavigationMenuLink>
                </NavigationMenuItem>

                <NavigationMenuItem>
                  <NavigationMenuLink asChild active={isActivePrefix("/admin")}>
                    <Link
                      href="/admin/login"
                      className={cn(
                        navigationMenuTriggerStyle(),
                        "rounded-full bg-transparent px-4 text-slate-700 hover:bg-white hover:text-slate-950 focus:bg-white focus:text-slate-950 data-[active]:bg-white data-[state=open]:bg-white",
                      )}
                    >
                      Internal Login
                    </Link>
                  </NavigationMenuLink>
                </NavigationMenuItem>
              </NavigationMenuList>
            </NavigationMenu>
          </div>

          <div className="ml-auto flex md:hidden items-center">
            <Sheet open={isOpen} onOpenChange={setIsOpen}>
              <SheetTrigger asChild>
                <Button
                  variant="ghost"
                  className="h-9 rounded-full border border-slate-200 bg-slate-50 px-3 text-slate-700 hover:bg-slate-100 hover:text-slate-950"
                >
                  <Menu className="h-5 w-5" />
                  <span className="ml-2 text-xs font-semibold uppercase tracking-[0.18em]">
                    Menu
                  </span>
                  <span className="sr-only">Open navigation menu</span>
                </Button>
              </SheetTrigger>
              <SheetContent
                side="left"
                className="w-[320px] overflow-y-auto border-r border-slate-800 bg-slate-950 text-white sm:w-[380px]"
              >
                <SheetTitle className="text-sm font-semibold uppercase tracking-[0.24em] text-white/70">
                  Menu
                </SheetTitle>
                <nav className="mt-8 flex flex-col gap-6">
                  <div className="space-y-3">
                    <h4 className="text-xs font-semibold uppercase tracking-[0.24em] text-white/55">
                      Main
                    </h4>
                    <div className="grid gap-2">
                      <Link
                        onClick={() => setIsOpen(false)}
                        href="/"
                        className="rounded border border-white/8 px-3 py-2 text-sm text-white/85 transition-colors hover:border-white/16 hover:bg-white/8 hover:text-white"
                      >
                        Home
                      </Link>
                      <Link
                        onClick={() => setIsOpen(false)}
                        href="/news"
                        className="rounded border border-white/8 px-3 py-2 text-sm text-white/85 transition-colors hover:border-white/16 hover:bg-white/8 hover:text-white"
                      >
                        News
                      </Link>
                      <Link
                        onClick={() => setIsOpen(false)}
                        href="/meetings"
                        className="rounded border border-white/8 px-3 py-2 text-sm text-white/85 transition-colors hover:border-white/16 hover:bg-white/8 hover:text-white"
                      >
                        Meetings
                      </Link>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <h4 className="text-xs font-semibold uppercase tracking-[0.24em] text-white/55">
                      Senators
                    </h4>
                    <div className="grid gap-2">
                      {senatorsItems.map((item) => (
                        <Link
                          key={item.title}
                          onClick={() => setIsOpen(false)}
                          href={item.href}
                          className="rounded border border-white/8 px-3 py-2 text-sm text-white/85 transition-colors hover:border-white/16 hover:bg-white/8 hover:text-white"
                        >
                          {item.title}
                        </Link>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <h4 className="text-xs font-semibold uppercase tracking-[0.24em] text-white/55">
                      Committees
                    </h4>
                    <div className="grid gap-2">
                      <Link
                        onClick={() => setIsOpen(false)}
                        href="/committees"
                        className="rounded border border-white/8 px-3 py-2 text-sm text-white/85 transition-colors hover:border-white/16 hover:bg-white/8 hover:text-white"
                      >
                        All Committees
                      </Link>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <h4 className="text-xs font-semibold uppercase tracking-[0.24em] text-white/55">
                      Legislation
                    </h4>
                    <div className="grid gap-2">
                      {legislationItems.map((item) => (
                        <Link
                          key={item.title}
                          onClick={() => setIsOpen(false)}
                          href={item.href}
                          className="rounded border border-white/8 px-3 py-2 text-sm text-white/85 transition-colors hover:border-white/16 hover:bg-white/8 hover:text-white"
                        >
                          {item.title}
                        </Link>
                      ))}
                      <a
                        href="https://drive.google.com/"
                        onClick={() => setIsOpen(false)}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="rounded border border-white/8 px-3 py-2 text-sm text-white/85 transition-colors hover:border-white/16 hover:bg-white/8 hover:text-white"
                        aria-label="Senate Archives (opens in a new tab)"
                      >
                        Senate Archives
                      </a>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <h4 className="text-xs font-semibold uppercase tracking-[0.24em] text-white/55">
                      About
                    </h4>
                    <div className="grid gap-2">
                      {aboutItems.map((item) => (
                        <Link
                          key={item.title}
                          onClick={() => setIsOpen(false)}
                          href={item.href}
                          className="rounded border border-white/8 px-3 py-2 text-sm text-white/85 transition-colors hover:border-white/16 hover:bg-white/8 hover:text-white"
                        >
                          {item.title}
                        </Link>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <h4 className="text-xs font-semibold uppercase tracking-[0.24em] text-white/55">
                      Funding
                    </h4>
                    <div className="grid gap-2">
                      {fundingItems.map((item) => (
                        <Link
                          key={item.title}
                          onClick={() => setIsOpen(false)}
                          href={item.href}
                          className="rounded border border-white/8 px-3 py-2 text-sm text-white/85 transition-colors hover:border-white/16 hover:bg-white/8 hover:text-white"
                        >
                          {item.title}
                        </Link>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-3">
                    <h4 className="text-xs font-semibold uppercase tracking-[0.24em] text-white/55">
                      Admin
                    </h4>
                    <div className="grid gap-2">
                      <Link
                        onClick={() => setIsOpen(false)}
                        href="/admin/login"
                        className="rounded border border-white/8 px-3 py-2 text-sm text-white/85 transition-colors hover:border-white/16 hover:bg-white/8 hover:text-white"
                      >
                        Internal Login
                      </Link>
                    </div>
                  </div>
                </nav>
              </SheetContent>
            </Sheet>
          </div>
        </div>
      </div>
    </header>
  );
}

const ListItem = React.forwardRef<
  React.ElementRef<"a">,
  React.ComponentPropsWithoutRef<"a"> & { href: string } // Ensure href is strongly typed for Link
>(({ className, title, children, href, ...props }, ref) => {
  return (
    <li>
      <NavigationMenuLink asChild>
        <Link
          href={href}
          className={cn(
            "block select-none space-y-1 rounded-lg border border-transparent p-3.5 leading-none no-underline outline-none transition-colors hover:border-slate-200 hover:bg-slate-50 hover:text-slate-950 focus:border-slate-200 focus:bg-slate-50",
            className,
          )}
          {...props}
        >
          <div className="text-sm font-medium leading-none text-slate-900">
            {title}
          </div>
          {children && (
            <p className="mt-1 line-clamp-2 text-sm leading-snug text-slate-500">
              {children}
            </p>
          )}
        </Link>
      </NavigationMenuLink>
    </li>
  );
});
ListItem.displayName = "ListItem";
