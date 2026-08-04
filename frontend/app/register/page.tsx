"use client";

import { useState } from "react";
import type { FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
    BrainCircuit,
    Loader2,
    LockKeyhole,
    Mail,
    UserRound,
} from "lucide-react";

import { setRegistrationSuccess } from "@/lib/registration-flash";
import { registerUser } from "@/services/auth";


const EMAIL_PATTERN = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;


function validateRegistration(
    fullName: string,
    email: string,
    password: string,
    confirmPassword: string
): string | null {

    if (!fullName.trim()) {
        return "Full name is required.";
    }

    if (fullName.trim().length > 255) {
        return "Full name must not exceed 255 characters.";
    }

    if (!email.trim()) {
        return "Email address is required.";
    }

    if (
        email.trim().length > 320
        || !EMAIL_PATTERN.test(email.trim())
    ) {
        return "Enter a valid email address.";
    }

    if (!password) {
        return "Password is required.";
    }

    if (password.length < 8) {
        return "Password must contain at least 8 characters.";
    }

    if (
        password.length > 72
        || new TextEncoder().encode(password).length > 72
    ) {
        return "Password must not exceed 72 UTF-8 bytes.";
    }

    if (!confirmPassword) {
        return "Password confirmation is required.";
    }

    if (password !== confirmPassword) {
        return "Passwords do not match.";
    }

    return null;

}


export default function RegisterPage() {

    const router = useRouter();

    const [fullName, setFullName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [confirmPassword, setConfirmPassword] = (
        useState("")
    );
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");


    async function handleSubmit(
        event: FormEvent<HTMLFormElement>
    ) {

        event.preventDefault();

        if (loading) {
            return;
        }

        const validationError = validateRegistration(
            fullName,
            email,
            password,
            confirmPassword
        );

        if (validationError) {
            setError(validationError);
            return;
        }

        try {

            setLoading(true);
            setError("");

            await registerUser({
                full_name: fullName.trim(),
                email: email.trim().toLowerCase(),
                password,
            });

            setRegistrationSuccess();
            router.replace("/login");

        } catch (registrationError) {

            setError(
                registrationError instanceof Error
                    ? registrationError.message
                    : "Unable to create your account."
            );

        } finally {

            setLoading(false);

        }

    }


    return (

        <main className="flex min-h-screen items-center justify-center bg-slate-100 px-4 py-10">

            <div className="w-full max-w-md">

                <div className="mb-8 text-center">
                    <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-200">
                        <BrainCircuit size={34} />
                    </div>
                    <h1 className="mt-5 text-3xl font-bold tracking-tight text-slate-900">
                        AI Resume Intelligence
                    </h1>
                    <p className="mt-2 text-sm text-gray-500">
                        Create your recruiter account
                    </p>
                </div>


                <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm sm:p-8">

                    <div>
                        <h2 className="text-xl font-semibold text-gray-900">
                            Create account
                        </h2>
                        <p className="mt-1 text-sm text-gray-500">
                            Register for recruiter access to the ATS.
                        </p>
                    </div>


                    <form
                        onSubmit={handleSubmit}
                        className="mt-7 space-y-5"
                        noValidate
                    >

                        <div>
                            <label htmlFor="full_name" className="text-sm font-medium text-gray-700">
                                Full name
                            </label>
                            <div className="relative mt-2">
                                <UserRound size={18} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                                <input
                                    id="full_name"
                                    name="full_name"
                                    type="text"
                                    autoComplete="name"
                                    required
                                    maxLength={255}
                                    value={fullName}
                                    onChange={(event) => setFullName(event.target.value)}
                                    className="w-full rounded-xl border border-gray-300 py-3 pl-10 pr-4 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                                    placeholder="Your full name"
                                />
                            </div>
                        </div>


                        <div>
                            <label htmlFor="email" className="text-sm font-medium text-gray-700">
                                Email address
                            </label>
                            <div className="relative mt-2">
                                <Mail size={18} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                                <input
                                    id="email"
                                    name="email"
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


                        <div>
                            <label htmlFor="password" className="text-sm font-medium text-gray-700">
                                Password
                            </label>
                            <div className="relative mt-2">
                                <LockKeyhole size={18} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    autoComplete="new-password"
                                    required
                                    minLength={8}
                                    maxLength={72}
                                    value={password}
                                    onChange={(event) => setPassword(event.target.value)}
                                    className="w-full rounded-xl border border-gray-300 py-3 pl-10 pr-4 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                                    placeholder="8–72 characters"
                                />
                            </div>
                        </div>


                        <div>
                            <label htmlFor="confirm_password" className="text-sm font-medium text-gray-700">
                                Confirm password
                            </label>
                            <div className="relative mt-2">
                                <LockKeyhole size={18} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                                <input
                                    id="confirm_password"
                                    name="confirm_password"
                                    type="password"
                                    autoComplete="new-password"
                                    required
                                    minLength={8}
                                    maxLength={72}
                                    value={confirmPassword}
                                    onChange={(event) => setConfirmPassword(event.target.value)}
                                    className="w-full rounded-xl border border-gray-300 py-3 pl-10 pr-4 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                                    placeholder="Enter your password again"
                                />
                            </div>
                        </div>


                        {error && (
                            <div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
                                {error}
                            </div>
                        )}


                        <button
                            type="submit"
                            disabled={loading}
                            className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                            {loading && (
                                <Loader2 size={18} className="animate-spin" />
                            )}
                            {loading ? "Creating account..." : "Create account"}
                        </button>

                    </form>


                    <p className="mt-6 text-center text-sm text-gray-500">
                        Already have an account?{" "}
                        <Link
                            href="/login"
                            className="font-semibold text-blue-600 transition hover:text-blue-700"
                        >
                            Back to sign in
                        </Link>
                    </p>

                </section>

            </div>

        </main>

    );

}
