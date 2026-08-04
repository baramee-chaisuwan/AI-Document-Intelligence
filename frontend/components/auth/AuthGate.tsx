"use client";

import {
    useEffect,
} from "react";
import {
    usePathname,
    useRouter,
} from "next/navigation";

import { useAuth } from "@/contexts/AuthContext";


const PUBLIC_PATHS = new Set([
    "/login",
    "/register",
]);

const ADMIN_PATHS = new Set([
    "/export",
]);


export default function AuthGate({
    children,
}: {
    children: React.ReactNode;
}) {

    const pathname = usePathname();
    const router = useRouter();

    const {
        user,
        loading,
        isAdmin,
    } = useAuth();

    const isPublic = PUBLIC_PATHS.has(
        pathname
    );

    const isAdminPath = ADMIN_PATHS.has(
        pathname
    );


    useEffect(() => {

        if (loading) {
            return;
        }

        if (isPublic && user) {

            router.replace("/dashboard");
            return;

        }

        if (!isPublic && !user) {

            router.replace("/login");
            return;

        }

        if (
            user
            && isAdminPath
            && !isAdmin
        ) {

            router.replace("/dashboard");

        }

    }, [
        isAdmin,
        isAdminPath,
        isPublic,
        loading,
        router,
        user,
    ]);


    const redirecting = (
        loading
        || (isPublic && Boolean(user))
        || (!isPublic && !user)
        || (
            Boolean(user)
            && isAdminPath
            && !isAdmin
        )
    );

    if (redirecting) {

        return (

            <div
                className="flex min-h-screen items-center justify-center bg-slate-100"
                role="status"
                aria-live="polite"
            >
                <div className="text-sm font-medium text-gray-500">
                    Loading authentication...
                </div>
            </div>

        );

    }

    return children;

}
