"use client";

import * as React from "react";
import Link from "next/link";
import { Menu } from "lucide-react";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import Image from "next/image";
import {
    Sheet,
    SheetContent,
    SheetTitle,
    SheetTrigger,
} from "@/components/ui/sheet";
import {
    NavigationMenu,
    NavigationMenuContent,
    NavigationMenuItem,
    NavigationMenuLink,
    NavigationMenuList,
    NavigationMenuTrigger,
    navigationMenuTriggerStyle,
} from "@/components/ui/navigation-menu";

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
    { title: "How a Bill Becomes a Law", href: "/about/how-a-bill-becomes-a-law" },
    { title: "Elections", href: "/about/elections" },
];

const fundingItems = [
    { title: "How to Apply", href: "/funding/apply" },
    { title: "Budget Process", href: "/funding/budget-process" },
    { title: "Where Does My Money Go?", href: "/funding/where-does-money-go" },
];

export function Header() {
    const [isOpen, setIsOpen] = React.useState(false);

    return (
        <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
            <div className="flex flex-col items-center">
                {/* Very Top Row: Title Bar (Black with White Text) */}
                <div className="w-full bg-carolina-black px-4 py-2 flex justify-start">
                    <span className="text-xl font-bold tracking-tight text-carolina-white">The University of North Carolina at Chapel Hill</span>
                </div>

                {/* Middle Row: Logo & Mobile Trigger Row (White Background) */}
                <div className="w-full bg-white border-b">
                    <div className="container mx-auto px-4 py-3 flex items-center justify-between relative">
                        <div className="flex flex-col items-start gap-2">
                            <Link href="/" className="flex items-center">
                                <Image
                                    src="/UNClogo.png"
                                    alt="UNC Senate Logo"
                                    width={800}
                                    height={800}
                                    className="object-contain"
                                />
                            </Link>
                        </div>
                        {/* Mobile Menu Trigger (Right-aligned on small screens) */}
                        <div className="absolute right-0 flex md:hidden items-center">
                            <Sheet open={isOpen} onOpenChange={setIsOpen}>
                                <SheetTrigger asChild>
                                    <Button variant="ghost" size="icon" className="md:hidden">
                                        <Menu className="h-5 w-5" />
                                        <span className="sr-only">Toggle mobile menu</span>
                                    </Button>
                                </SheetTrigger>
                                <SheetContent side="left" className="w-[300px] sm:w-[400px] overflow-y-auto bg-black text-white border-r border-gray-800">
                                    <nav className="flex flex-col gap-4 mt-8">
                                        <Link onClick={() => setIsOpen(false)} href="/" className="text-lg py-2 font-medium hover:text-primary transition-colors">
                                            Home
                                        </Link>
                                        <Link onClick={() => setIsOpen(false)} href="/news" className="text-lg py-2 font-medium hover:text-primary transition-colors">
                                            News
                                        </Link>

                                        <div className="space-y-3 pt-2">
                                            <h4 className="font-semibold text-muted-foreground uppercase tracking-wider text-sm">Senators</h4>
                                            <div className="flex flex-col gap-2 pl-4">
                                                {senatorsItems.map((item) => (
                                                    <Link onClick={() => setIsOpen(false)} key={item.title} href={item.href} className="text-sm py-1 pt-1 text-muted-foreground hover:text-primary transition-colors">
                                                        {item.title}
                                                    </Link>
                                                ))}
                                            </div>
                                        </div>

                                        <div className="space-y-3 pt-2">
                                            <h4 className="font-semibold text-muted-foreground uppercase tracking-wider text-sm">Committees</h4>
                                            <Link onClick={() => setIsOpen(false)} href="/committees" className="text-lg py-2 font-medium hover:text-primary transition-colors">
                                                Committees
                                            </Link>
                                        </div>

                                        <div className="space-y-3 pt-2">
                                            <h4 className="font-semibold text-muted-foreground uppercase tracking-wider text-sm">Legislation</h4>
                                            <div className="flex flex-col gap-2 pl-4">
                                                {legislationItems.map((item) => (
                                                    <Link onClick={() => setIsOpen(false)} key={item.title} href={item.href} className="text-sm py-1 pt-1 text-muted-foreground hover:text-primary transition-colors">
                                                        {item.title}
                                                    </Link>
                                                ))}
                                                <a onClick={() => setIsOpen(false)} href="https://drive.google.com/" target="_blank" rel="noopener noreferrer" className="text-sm py-1 pt-1 text-muted-foreground hover:text-primary transition-colors">
                                                    Senate Archives
                                                </a>
                                            </div>
                                        </div>

                                        <div className="space-y-3 pt-2">
                                            <h4 className="font-semibold text-muted-foreground uppercase tracking-wider text-sm">About</h4>
                                            <div className="flex flex-col gap-2 pl-4">
                                                {aboutItems.map((item) => (
                                                    <Link onClick={() => setIsOpen(false)} key={item.title} href={item.href} className="text-sm py-1 pt-1 text-muted-foreground hover:text-primary transition-colors">
                                                        {item.title}
                                                    </Link>
                                                ))}
                                            </div>
                                        </div>

                                        <div className="space-y-3 pt-2">
                                            <h4 className="font-semibold text-muted-foreground uppercase tracking-wider text-sm">Funding</h4>
                                            <div className="flex flex-col gap-2 pl-4">
                                                {fundingItems.map((item) => (
                                                    <Link onClick={() => setIsOpen(false)} key={item.title} href={item.href} className="text-sm py-1 pt-1 text-muted-foreground hover:text-primary transition-colors">
                                                        {item.title}
                                                    </Link>
                                                ))}
                                            </div>
                                        </div>

                                        <Link onClick={() => setIsOpen(false)} href="/meetings" className="text-lg py-2 mt-2 font-medium hover:text-primary transition-colors">
                                            Meetings
                                        </Link>
                                    </nav>
                                </SheetContent>
                            </Sheet>
                        </div>
                    </div>
                </div>

                {/* Bottom Row: Desktop Navigation (Black Background) */}
                <div className="w-full bg-carolina-black hidden md:flex items-center justify-center py-1">
                    <NavigationMenu>
                        <NavigationMenuList>

                            <NavigationMenuItem>
                                <Link href="/" legacyBehavior passHref>
                                    <NavigationMenuLink className={cn(navigationMenuTriggerStyle(), "bg-transparent text-white hover:bg-white/10 hover:text-white focus:bg-white/10 focus:text-white data-[active]:bg-white/10 data-[state=open]:bg-white/10")}>
                                        Home
                                    </NavigationMenuLink>
                                </Link>
                            </NavigationMenuItem>

                            <NavigationMenuItem>
                                <Link href="/news" legacyBehavior passHref>
                                    <NavigationMenuLink className={cn(navigationMenuTriggerStyle(), "bg-transparent text-white hover:bg-white/10 hover:text-white focus:bg-white/10 focus:text-white data-[active]:bg-white/10 data-[state=open]:bg-white/10")}>
                                        News
                                    </NavigationMenuLink>
                                </Link>
                            </NavigationMenuItem>

                            <NavigationMenuItem>
                                <NavigationMenuTrigger className="bg-transparent text-white hover:bg-white/10 hover:text-white focus:bg-white/10 focus:text-white data-[active]:bg-white/10 data-[state=open]:bg-white/10">Senators</NavigationMenuTrigger>
                                <NavigationMenuContent>
                                    <ul className="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2 lg:w-[600px] bg-black border border-gray-800">
                                        {senatorsItems.map((item) => (
                                            <ListItem key={item.title} title={item.title} href={item.href} />
                                        ))}
                                    </ul>
                                </NavigationMenuContent>
                            </NavigationMenuItem>

                            <NavigationMenuItem>
                                <Link href="/committees" legacyBehavior passHref>
                                    <NavigationMenuLink className={cn(navigationMenuTriggerStyle(), "bg-transparent text-white hover:bg-white/10 hover:text-white focus:bg-white/10 focus:text-white data-[active]:bg-white/10 data-[state=open]:bg-white/10")}>
                                        Committees
                                    </NavigationMenuLink>
                                </Link>
                            </NavigationMenuItem>

                            <NavigationMenuItem>
                                <NavigationMenuTrigger className="bg-transparent text-white hover:bg-white/10 hover:text-white focus:bg-white/10 focus:text-white data-[active]:bg-white/10 data-[state=open]:bg-white/10">Legislation</NavigationMenuTrigger>
                                <NavigationMenuContent>
                                    <ul className="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2 lg:w-[600px] bg-black border border-gray-800">
                                        {legislationItems.map((item) => (
                                            <ListItem key={item.title} title={item.title} href={item.href} />
                                        ))}
                                        {/* External Link for Senate Archives */}
                                        <li>
                                            <NavigationMenuLink asChild>
                                                <a
                                                    href="https://drive.google.com/"
                                                    target="_blank"
                                                    rel="noopener noreferrer"
                                                    className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-white/10 focus:bg-white/10 text-white hover:text-white focus:text-white"
                                                    aria-label="Senate Archives (opens in a new tab)"
                                                >
                                                    <div className="text-sm font-medium leading-none">Senate Archives</div>
                                                </a>
                                            </NavigationMenuLink>
                                        </li>
                                    </ul>
                                </NavigationMenuContent>
                            </NavigationMenuItem>

                            <NavigationMenuItem>
                                <NavigationMenuTrigger className="bg-transparent text-white hover:bg-white/10 hover:text-white focus:bg-white/10 focus:text-white data-[active]:bg-white/10 data-[state=open]:bg-white/10">About</NavigationMenuTrigger>
                                <NavigationMenuContent>
                                    <ul className="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2 lg:w-[600px] bg-black border border-gray-800">
                                        {aboutItems.map((item) => (
                                            <ListItem key={item.title} title={item.title} href={item.href} />
                                        ))}
                                    </ul>
                                </NavigationMenuContent>
                            </NavigationMenuItem>

                            <NavigationMenuItem>
                                <NavigationMenuTrigger className="bg-transparent text-white hover:bg-white/10 hover:text-white focus:bg-white/10 focus:text-white data-[active]:bg-white/10 data-[state=open]:bg-white/10">Funding</NavigationMenuTrigger>
                                <NavigationMenuContent>
                                    <ul className="grid w-[400px] gap-3 p-4 md:w-[500px] md:grid-cols-2 lg:w-[600px] bg-black border border-gray-800">
                                        {fundingItems.map((item) => (
                                            <ListItem key={item.title} title={item.title} href={item.href} />
                                        ))}
                                    </ul>
                                </NavigationMenuContent>
                            </NavigationMenuItem>

                            <NavigationMenuItem>
                                <Link href="/meetings" legacyBehavior passHref>
                                    <NavigationMenuLink className={cn(navigationMenuTriggerStyle(), "bg-transparent text-white hover:bg-white/10 hover:text-white focus:bg-white/10 focus:text-white data-[active]:bg-white/10 data-[state=open]:bg-white/10")}>
                                        Meetings
                                    </NavigationMenuLink>
                                </Link>
                            </NavigationMenuItem>

                        </NavigationMenuList>
                    </NavigationMenu>
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
                {/* Wrap the accessible Shadcn a-tag in a Next.js Link to enable client-side routing */}
                <Link href={href} legacyBehavior passHref>
                    <a
                        ref={ref}
                        className={cn(
                            "block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-white/10 focus:bg-white/10 text-white hover:text-white focus:text-white",
                            className
                        )}
                        {...props}
                    >
                        <div className="text-sm font-medium leading-none">{title}</div>
                        {children && (
                            <p className="line-clamp-2 text-sm leading-snug text-gray-400 mt-1">
                                {children}
                            </p>
                        )}
                    </a>
                </Link>
            </NavigationMenuLink>
        </li>
    );
});
ListItem.displayName = "ListItem";
