"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import {
    LayoutDashboard,
    Users,
    Upload,
    Search,
    Sparkles,
    BarChart3,
    Bot,
    FileDown,
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
        title: "AI Search",
        href: "/search",
        icon: Search,
    },

    {
        title: "Recommendation",
        href: "/recommend",
        icon: Sparkles,
    },

    {
        title: "Analytics",
        href: "/analytics",
        icon: BarChart3,
    },

    {
        title: "AI Assistant",
        href: "/assistant",
        icon: Bot,
    },

    {
        title: "Export",
        href: "/export",
        icon: FileDown,
    },

];

export default function Sidebar() {


    const pathname = usePathname();


    return (

        <aside
            className="
                sticky
                top-16
                h-[calc(100vh-4rem)]
                w-64
                border-r
                bg-white
                shadow-sm
            "
        >


            <div className="border-b p-6">

                <h2 className="text-lg font-bold text-slate-900">
                    ATS Navigation
                </h2>

                <p className="mt-1 text-sm text-gray-500">
                    AI Document Intelligence
                </p>

            </div>



            <nav className="space-y-2 p-4">


                {menuItems.map((item) => {


                    const Icon = item.icon;


                    const active =
                        pathname === item.href ||
                        pathname.startsWith(
                            item.href + "/"
                        );


                    return (

                        <Link

                            key={item.title}

                            href={item.href}

                            className={`

                                flex
                                items-center
                                gap-3
                                rounded-xl
                                px-4
                                py-3
                                transition-all
                                duration-200


                                ${active

                                    ? "bg-blue-600 text-white shadow"

                                    : "text-gray-700 hover:bg-slate-100 hover:text-blue-600"

                                }

                            `}

                        >

                            <Icon size={20} />


                            <span className="font-medium">

                                {item.title}

                            </span>


                        </Link>

                    );


                })}


            </nav>


        </aside>

    );

}