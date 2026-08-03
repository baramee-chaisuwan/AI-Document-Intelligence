"use client";

import {
    useEffect,
    useState,
} from "react";

import Navbar from "@/components/layout/Navbar";
import Sidebar from "@/components/layout/Sidebar";


type AppLayoutProps = {
    title: string;
    description?: string;
    children: React.ReactNode;
};


export default function AppLayout({
    title,
    description,
    children,
}: AppLayoutProps) {

    const [
        sidebarOpen,
        setSidebarOpen,
    ] = useState(false);


    useEffect(() => {

        document.body.style.overflow = (
            sidebarOpen
                ? "hidden"
                : ""
        );


        return () => {

            document.body.style.overflow = "";

        };

    }, [
        sidebarOpen,
    ]);


    function openSidebar() {

        setSidebarOpen(true);

    }


    function closeSidebar() {

        setSidebarOpen(false);

    }


    return (

        <div
            className="
                min-h-screen
                bg-slate-100
            "
        >

            <Navbar
                onMenuClick={openSidebar}
            />


            <div
                className="
                    flex
                    min-h-[calc(100vh-4rem)]
                "
            >

                <Sidebar
                    isOpen={sidebarOpen}
                    onClose={closeSidebar}
                />


                <main
                    className="
                        min-w-0
                        flex-1
                        bg-slate-100
                        px-4
                        py-6
                        sm:px-6
                        lg:px-8
                        lg:py-8
                    "
                >

                    <div
                        className="
                            mx-auto
                            w-full
                            max-w-7xl
                        "
                    >

                        <header className="mb-8">

                            <h1
                                className="
                                    text-2xl
                                    font-bold
                                    tracking-tight
                                    text-slate-900
                                    sm:text-3xl
                                "
                            >
                                {title}
                            </h1>


                            {description && (

                                <p
                                    className="
                                        mt-2
                                        max-w-3xl
                                        text-sm
                                        leading-6
                                        text-gray-500
                                        sm:text-base
                                    "
                                >
                                    {description}
                                </p>

                            )}

                        </header>


                        {children}

                    </div>

                </main>

            </div>

        </div>

    );

}