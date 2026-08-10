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
import {
    requestPasswordReset,
    verifyPasswordResetOTP,
} from "@/services/auth";


export default function VerifyResetOTPPage() {
    const router = useRouter();
    const [email, setEmail] = useState("");
    const [otp, setOTP] = useState("");
    const [loading, setLoading] = useState(false);
    const [resendLoading, setResendLoading] = useState(false);
    const [resendCooldown, setResendCooldown] = useState(60);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");

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

    useEffect(() => {
        const cooldownTimer = window.setInterval(() => {
            setResendCooldown((current) => Math.max(0, current - 1));
        }, 1000);

        return () => {
            window.clearInterval(cooldownTimer);
        };
    }, []);

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

    async function handleResend() {
        if (resendLoading || resendCooldown > 0 || !email) return;

        try {
            setResendLoading(true);
            setError("");
            setSuccess("");
            await requestPasswordReset(email);
            setOTP("");
            setResendCooldown(60);
            setSuccess("If an account exists, a new verification code has been sent.");
        } catch {
            setError("Unable to resend the verification code. Please try again later.");
        } finally {
            setResendLoading(false);
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
                {success && <div role="status" className="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700">{success}</div>}
                <button type="submit" disabled={loading || otp.length !== 6 || !email} className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60">
                    {loading && <Loader2 size={18} className="animate-spin" />}
                    {loading ? "Verifying..." : "Verify code"}
                </button>
                <button
                    type="button"
                    onClick={handleResend}
                    disabled={resendLoading || resendCooldown > 0 || !email}
                    className="inline-flex w-full items-center justify-center gap-2 text-sm font-medium text-blue-600 transition hover:text-blue-700 disabled:cursor-not-allowed disabled:text-gray-400"
                >
                    {resendLoading && <Loader2 size={16} className="animate-spin" />}
                    {resendLoading
                        ? "Resending..."
                        : resendCooldown > 0
                            ? `Resend code in ${resendCooldown}s`
                            : "Resend code"}
                </button>
            </form>
        </RecoveryShell>
    );
}
