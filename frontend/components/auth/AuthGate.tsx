"use client";

import {
    useEffect,
} from "react";
import {
    usePathname,
    useRouter,
} from "next/navigation";

import { useAuth } from "@/contexts/AuthContext";
import {
    isAdminPath,
    isPublicPath,
} from "@/lib/route-access";


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

    const isPublic = isPublicPath(pathname);

    const adminOnly = isAdminPath(pathname);


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
            && adminOnly
            && !isAdmin
        ) {

            router.replace("/dashboard");

        }

    }, [
        isAdmin,
        adminOnly,
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
            && adminOnly
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
