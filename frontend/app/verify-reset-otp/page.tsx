"use client";

import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { KeyRound, Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";

import RecoveryShell from "@/components/auth/RecoveryShell";
import {
    getResetEmail,
    setResetToken,
} from "@/lib/password-reset-storage";
import { verifyPasswordResetOTP } from "@/services/auth";


export default function VerifyResetOTPPage() {
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [otp, setOTP] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        const initializationTimer = window.setTimeout(() => {
            const storedEmail = getResetEmail();
            if (!storedEmail) {
                router.replace("/forgot-password");
                return;
            }
            setEmail(storedEmail);
        }, 0);

        return () => {
            window.clearTimeout(initializationTimer);
        };
    }, [router]);

    async function handleSubmit(
        event: FormEvent<HTMLFormElement>
    ) {
        event.preventDefault();
        if (loading || otp.length !== 6) return;

        try {
            setLoading(true);
            setError("");
            const result = await verifyPasswordResetOTP(
                email,
                otp
            );
            setResetToken(result.reset_token);
            router.push("/reset-password");
        } catch (verifyError) {
            setError(
                verifyError instanceof Error
                    ? verifyError.message
                    : "The verification code is invalid or expired."
            );
        } finally {
            setLoading(false);
        }
    }

    return (
        <RecoveryShell
            title="Verify your code"
            description="Enter the six-digit code sent to your email. The code expires after 10 minutes."
        >
            <form onSubmit={handleSubmit} className="mt-7 space-y-5">
                <div>
                    <label htmlFor="otp" className="text-sm font-medium text-gray-700">
                        Verification code
                    </label>
                    <div className="relative mt-2">
                        <KeyRound size={18} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                        <input
                            id="otp"
                            type="text"
                            inputMode="numeric"
                            autoComplete="one-time-code"
                            required
                            pattern="[0-9]{6}"
                            maxLength={6}
                            value={otp}
                            onChange={(event) => setOTP(event.target.value.replace(/\D/g, "").slice(0, 6))}
                            className="w-full rounded-xl border border-gray-300 py-3 pl-10 pr-4 text-center font-mono text-xl tracking-[0.4em] text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                            placeholder="000000"
                        />
                    </div>
                </div>
                {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
                <button type="submit" disabled={loading || otp.length !== 6 || !email} className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60">
                    {loading && <Loader2 size={18} className="animate-spin" />}
                    {loading ? "Verifying..." : "Verify code"}
                </button>
            </form>
        </RecoveryShell>
    );
}
