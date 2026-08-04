"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import {
    BarChart3,
    Bot,
    FileDown,
    LayoutDashboard,
    Search,
    Sparkles,
    Upload,
    Users,
    X,
} from "lucide-react";

import { useAuth } from "@/contexts/AuthContext";


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
        adminOnly: true,
    },
];


type SidebarProps = {
    isOpen?: boolean;
    onClose?: () => void;
};


export default function Sidebar({
    isOpen = false,
    onClose,
}: SidebarProps) {

    const pathname = usePathname();
    const { isAdmin } = useAuth();

    const visibleMenuItems = menuItems.filter(
        (item) => !item.adminOnly || isAdmin
    );


    function handleNavigation() {

        onClose?.();

    }


    return (

        <>

            {isOpen && (

                <button
                    type="button"
                    aria-label="Close navigation"
                    onClick={onClose}
                    className="
                        fixed
                        inset-0
                        z-40
                        bg-black/40
                        lg:hidden
                    "
                />

            )}


            <aside
                className={`
                    fixed
                    left-0
                    top-16
                    z-50
                    h-[calc(100vh-4rem)]
                    w-72
                    border-r
                    border-gray-200
                    bg-white
                    shadow-lg
                    transition-transform
                    duration-200
                    lg:sticky
                    lg:z-20
                    lg:w-64
                    lg:translate-x-0
                    lg:shadow-sm
                    ${isOpen
                        ? "translate-x-0"
                        : "-translate-x-full"
                    }
                `}
            >

                <div
                    className="
                        flex
                        items-start
                        justify-between
                        gap-4
                        border-b
                        border-gray-100
                        p-6
                    "
                >

                    <div>

                        <h2
                            className="
                                text-lg
                                font-bold
                                text-slate-900
                            "
                        >
                            ATS Navigation
                        </h2>

                        <p
                            className="
                                mt-1
                                text-sm
                                text-gray-500
                            "
                        >
                            AI Document Intelligence
                        </p>

                    </div>


                    <button
                        type="button"
                        aria-label="Close navigation"
                        onClick={onClose}
                        className="
                            inline-flex
                            h-9
                            w-9
                            items-center
                            justify-center
                            rounded-lg
                            text-gray-500
                            transition-colors
                            hover:bg-gray-100
                            hover:text-gray-900
                            lg:hidden
                        "
                    >
                        <X size={20} />
                    </button>

                </div>


                <nav
                    aria-label="Primary navigation"
                    className="
                        h-[calc(100%-105px)]
                        space-y-2
                        overflow-y-auto
                        p-4
                    "
                >

                    {visibleMenuItems.map((item) => {

                        const Icon = item.icon;

                        const active = (
                            pathname === item.href
                            || pathname.startsWith(
                                item.href + "/"
                            )
                        );


                        return (

                            <Link
                                key={item.href}
                                href={item.href}
                                onClick={handleNavigation}
                                aria-current={
                                    active
                                        ? "page"
                                        : undefined
                                }
                                className={`
                                    flex
                                    items-center
                                    gap-3
                                    rounded-xl
                                    px-4
                                    py-3
                                    text-sm
                                    font-medium
                                    transition-all
                                    duration-200
                                    ${active
                                        ? (
                                            "bg-blue-600 "
                                            + "text-white "
                                            + "shadow-sm"
                                        )
                                        : (
                                            "text-gray-700 "
                                            + "hover:bg-slate-100 "
                                            + "hover:text-blue-600"
                                        )
                                    }
                                `}
                            >

                                <Icon
                                    size={20}
                                    aria-hidden="true"
                                />

                                <span>
                                    {item.title}
                                </span>

                            </Link>

                        );

                    })}

                </nav>

            </aside>

        </>

    );

}
