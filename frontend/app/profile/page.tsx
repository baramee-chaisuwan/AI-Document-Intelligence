"use client";

import { ShieldCheck } from "lucide-react";

import AppLayout from "@/components/layout/AppLayout";
import { useAuth } from "@/contexts/AuthContext";
import {
    accountInitials,
    profileDetails,
} from "@/lib/account-ux";


export default function ProfilePage() {
    const { user } = useAuth();

    if (!user) {
        return null;
    }

    const details = profileDetails(user);

    return (
        <AppLayout
            title="Profile"
            description="Your authenticated ATS account information."
        >
            <section className="max-w-2xl rounded-2xl border border-gray-200 bg-white p-6 shadow-sm sm:p-8">
                <div className="flex items-center gap-4 border-b border-gray-100 pb-6">
                    <div className="flex h-16 w-16 shrink-0 items-center justify-center rounded-full bg-blue-600 text-xl font-bold text-white">
                        {accountInitials(user.full_name)}
                    </div>
                    <div className="min-w-0">
                        <h2 className="truncate text-xl font-semibold text-slate-900">
                            {user.full_name}
                        </h2>
                        <p className="mt-1 truncate text-sm text-gray-500">
                            {user.email}
                        </p>
                    </div>
                </div>

                <dl className="mt-6 divide-y divide-gray-100">
                    {details.map((detail) => (
                        <div
                            key={detail.label}
                            className="grid gap-1 py-4 sm:grid-cols-[10rem_1fr] sm:gap-4"
                        >
                            <dt className="text-sm font-medium text-gray-500">
                                {detail.label}
                            </dt>
                            <dd className="flex items-center gap-2 break-words text-sm font-semibold text-slate-900">
                                {detail.label === "Role" && (
                                    <ShieldCheck
                                        size={16}
                                        className="shrink-0 text-green-600"
                                        aria-hidden="true"
                                    />
                                )}
                                {detail.value}
                            </dd>
                        </div>
                    ))}
                </dl>
            </section>
        </AppLayout>
    );
}
