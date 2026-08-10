"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import { Loader2, Mail } from "lucide-react";
import { useRouter } from "next/navigation";

import RecoveryShell from "@/components/auth/RecoveryShell";
import { setResetEmail } from "@/lib/password-reset-storage";
import { requestPasswordReset } from "@/services/auth";


export default function ForgotPasswordPage() {
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    async function handleSubmit(
        event: FormEvent<HTMLFormElement>
    ) {
        event.preventDefault();
        if (loading) return;

        try {
            setLoading(true);
            setError("");
            await requestPasswordReset(
                email.trim().toLowerCase()
            );
            setResetEmail(email.trim().toLowerCase());
            router.push("/verify-reset-otp");
        } catch (requestError) {
            setError(
                requestError instanceof Error
                    ? requestError.message
                    : "Unable to request a verification code."
            );
        } finally {
            setLoading(false);
        }
    }

    return (
        <RecoveryShell
            title="Forgot password"
            description="Enter your account email. If an account exists, we will send a six-digit verification code."
        >
            <form onSubmit={handleSubmit} className="mt-7 space-y-5">
                <div>
                    <label htmlFor="email" className="text-sm font-medium text-gray-700">
                        Email address
                    </label>
                    <div className="relative mt-2">
                        <Mail size={18} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                        <input
                            id="email"
                            type="email"
                            autoComplete="email"
                            required
                            maxLength={320}
                            value={email}
                            onChange={(event) => setEmail(event.target.value)}
                            className="w-full rounded-xl border border-gray-300 py-3 pl-10 pr-4 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                            placeholder="name@example.com"
                        />
                    </div>
                </div>
                {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
                <button type="submit" disabled={loading} className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60">
                    {loading && <Loader2 size={18} className="animate-spin" />}
                    {loading ? "Sending code..." : "Send verification code"}
                </button>
            </form>
        </RecoveryShell>
    );
}
