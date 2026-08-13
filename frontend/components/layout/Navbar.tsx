"use client";

import Link from "next/link";
import {
    LogOut,
    Menu,
    ShieldCheck,
} from "lucide-react";

import { useAuth } from "@/contexts/AuthContext";
import NotificationBell from "@/components/layout/NotificationBell";
import {
    accountInitials,
    accountRoleLabel,
    PROFILE_PATH,
} from "@/lib/account-ux";


type NavbarProps = {
    onMenuClick?: () => void;
};


export default function Navbar({
    onMenuClick,
}: NavbarProps) {

    const {
        user,
        logout,
    } = useAuth();

    const initials = accountInitials(
        user?.full_name ?? ""
    );

    const roleLabel = user
        ? accountRoleLabel(user.role)
        : "Recruiter";

    return (

        <header
            className="
                sticky
                top-0
                z-50
                flex
                h-16
                items-center
                justify-between
                border-b
                border-gray-200
                bg-white
                px-4
                shadow-sm
                sm:px-6
                lg:px-8
            "
        >

            <div
                className="
                    flex
                    items-center
                    gap-3
                "
            >

                <button
                    type="button"
                    onClick={onMenuClick}
                    className="
                        inline-flex
                        h-10
                        w-10
                        items-center
                        justify-center
                        rounded-lg
                        transition
                        hover:bg-gray-100
                        lg:hidden
                    "
                    aria-label="Open navigation"
                >

                    <Menu size={22} />

                </button>


                <div>

                    <h1
                        className="
                            text-lg
                            font-bold
                            text-slate-900
                            sm:text-xl
                            lg:text-2xl
                        "
                    >
                        AI Resume Intelligence
                    </h1>

                    <p
                        className="
                            hidden
                            text-sm
                            text-gray-500
                            sm:block
                        "
                    >
                        Applicant Tracking System
                    </p>

                </div>

            </div>



            <div
                className="
                    flex
                    items-center
                    gap-4
                    sm:gap-6
                "
            >

                <NotificationBell />


                <div
                    className="
                        hidden
                        h-8
                        w-px
                        bg-gray-200
                        sm:block
                    "
                />


                <Link
                    href={PROFILE_PATH}
                    aria-label={`View profile for ${user?.full_name ?? "ATS User"}`}
                    className="
                        flex
                        items-center
                        gap-3
                        rounded-xl
                        p-1
                        transition
                        hover:bg-gray-100
                        focus-visible:outline-none
                        focus-visible:ring-2
                        focus-visible:ring-blue-500
                    "
                >

                    <div
                        className="
                            flex
                            h-10
                            w-10
                            items-center
                            justify-center
                            rounded-full
                            bg-blue-600
                            font-bold
                            text-white
                        "
                    >
                        {initials}
                    </div>


                    <div
                        className="
                            hidden
                            sm:block
                        "
                    >

                        <p
                            className="
                                font-semibold
                                text-slate-900
                            "
                        >
                            {user?.full_name ?? "ATS User"}
                        </p>


                        <div
                            className="
                                flex
                                items-center
                                gap-2
                            "
                        >

                            <ShieldCheck
                                size={14}
                                className="text-green-600"
                            />

                            <span
                                className="
                                    text-xs
                                    text-gray-500
                                "
                            >
                                {roleLabel}
                            </span>

                        </div>

                    </div>

                </Link>


                <button
                    type="button"
                    onClick={logout}
                    className="inline-flex items-center gap-2 rounded-lg border border-gray-200 px-3 py-2 text-sm font-medium text-gray-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-600"
                    aria-label="Sign out"
                >
                    <LogOut size={17} />
                    <span className="hidden md:inline">
                        Logout
                    </span>
                </button>

            </div>

        </header>

    );

}
