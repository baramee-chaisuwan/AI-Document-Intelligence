"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import {
    LayoutDashboard,
    Users,
    Upload,
    Search,
    BarChart3,
    Settings,
} from "lucide-react";

const menuItems = [
    {
        title: "Dashboard",
        href: "/dashboard",
        icon: LayoutDashboard,
    },
    {
        title: "Candidates",
        href: "/candidates",
        icon: Users,
    },
    {
        title: "Upload Resume",
        href: "/upload",
        icon: Upload,
    },
    {
        title: "Search",
        href: "/search",
        icon: Search,
    },
    {
        title: "Analytics",
        href: "#",
        icon: BarChart3,
    },
    {
        title: "Settings",
        href: "#",
        icon: Settings,
    },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="w-64 border-r bg-white p-6">
            <p className="mb-6 text-lg font-semibold">
                Navigation
            </p>

            <nav className="space-y-2">
                {menuItems.map((item) => {
                    const Icon = item.icon;
                    const active = pathname === item.href;

                    return (
                        <Link
                            key={item.title}
                            href={item.href}
                            className={`flex items-center gap-3 rounded-lg px-4 py-3 transition ${active
                                    ? "bg-blue-600 text-white"
                                    : "text-gray-700 hover:bg-gray-100"
                                }`}
                        >
                            <Icon size={20} />
                            <span>{item.title}</span>
                        </Link>
                    );
                })}
            </nav>
        </aside>
    );
}