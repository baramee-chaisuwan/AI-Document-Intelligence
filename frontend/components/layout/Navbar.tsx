"use client";

import {
    Bell,
    Menu,
    ShieldCheck,
} from "lucide-react";


type NavbarProps = {
    onMenuClick?: () => void;
};


export default function Navbar({
    onMenuClick,
}: NavbarProps) {

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

                <button
                    type="button"
                    className="
                        rounded-full
                        p-2
                        transition
                        hover:bg-gray-100
                    "
                    aria-label="Notifications"
                >

                    <Bell
                        size={20}
                        className="text-gray-600"
                    />

                </button>


                <div
                    className="
                        hidden
                        h-8
                        w-px
                        bg-gray-200
                        sm:block
                    "
                />


                <div
                    className="
                        flex
                        items-center
                        gap-3
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
                        AI
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
                            ATS Admin
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
                                Administrator
                            </span>

                        </div>

                    </div>

                </div>

            </div>

        </header>

    );

}