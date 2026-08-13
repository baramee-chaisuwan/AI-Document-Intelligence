"use client";

import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Loader2 } from "lucide-react";
import { useRouter } from "next/navigation";

import RecoveryShell from "@/components/auth/RecoveryShell";
import PasswordInput from "@/components/auth/PasswordInput";
import { setPasswordResetSuccess } from "@/lib/password-reset-flash";
import {
    clearPasswordResetState,
    getResetToken,
} from "@/lib/password-reset-storage";
import { resetPassword } from "@/services/auth";


function validatePasswords(
    password: string,
    confirmation: string
): string | null {
    if (password.length < 8) {
        return "Password must contain at least 8 characters.";
    }
    if (
        password.length > 72
        || new TextEncoder().encode(password).length > 72
    ) {
        return "Password must not exceed 72 UTF-8 bytes.";
    }
    if (password !== confirmation) {
        return "Passwords do not match.";
    }
    return null;
}


export default function ResetPasswordPage() {
    const router = useRouter();
    const [resetToken, setResetToken] = useState("");
    const [password, setPassword] = useState("");
    const [confirmation, setConfirmation] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        const initializationTimer = window.setTimeout(() => {
            const storedToken = getResetToken();
            if (!storedToken) {
                router.replace("/forgot-password");
                return;
            }
            setResetToken(storedToken);
        }, 0);

        return () => {
            window.clearTimeout(initializationTimer);
        };
    }, [router]);

    async function handleSubmit(
        event: FormEvent<HTMLFormElement>
    ) {
        event.preventDefault();
        if (loading) return;

        const validationError = validatePasswords(
            password,
            confirmation
        );
        if (validationError) {
            setError(validationError);
            return;
        }

        try {
            setLoading(true);
            setError("");
            const result = await resetPassword(
                resetToken,
                password,
                confirmation
            );
            clearPasswordResetState();
            setPasswordResetSuccess(result.message);
            router.replace("/login");
        } catch (resetError) {
            setError(
                resetError instanceof Error
                    ? resetError.message
                    : "Unable to reset your password."
            );
        } finally {
            setLoading(false);
        }
    }

    return (
        <RecoveryShell
            title="Set a new password"
            description="Choose a new password for your ATS account. This will invalidate your existing access tokens."
        >
            <form onSubmit={handleSubmit} className="mt-7 space-y-5">
                {[
                    {
                        id: "new_password",
                        label: "New password",
                        value: password,
                        setter: setPassword,
                    },
                    {
                        id: "confirm_password",
                        label: "Confirm password",
                        value: confirmation,
                        setter: setConfirmation,
                    },
                ].map((field) => (
                    <div key={field.id}>
                        <label htmlFor={field.id} className="text-sm font-medium text-gray-700">
                            {field.label}
                        </label>
                        <PasswordInput
                            id={field.id}
                            name={field.id}
                            autoComplete="new-password"
                            required
                            minLength={8}
                            maxLength={72}
                            value={field.value}
                            onChange={(event) => field.setter(event.target.value)}
                        />
                    </div>
                ))}
                {error && <div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>}
                <button type="submit" disabled={loading || !resetToken} className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60">
                    {loading && <Loader2 size={18} className="animate-spin" />}
                    {loading ? "Resetting password..." : "Reset password"}
                </button>
            </form>
        </RecoveryShell>
    );
}
