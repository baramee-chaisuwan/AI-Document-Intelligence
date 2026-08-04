"use client";

import {
    useEffect,
    useState,
} from "react";
import type { FormEvent } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
    BrainCircuit,
    Loader2,
    LockKeyhole,
    Mail,
} from "lucide-react";

import { useAuth } from "@/contexts/AuthContext";
import { consumeRegistrationSuccess } from "@/lib/registration-flash";


export default function LoginPage() {

    const router = useRouter();
    const { login } = useAuth();

    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [success, setSuccess] = useState("");


    useEffect(() => {

        const timer = window.setTimeout(
            () => {
                setSuccess(
                    consumeRegistrationSuccess()
                    ?? ""
                );
            },
            0
        );

        return () => {
            window.clearTimeout(timer);
        };

    }, []);


    async function handleSubmit(
        event: FormEvent<HTMLFormElement>
    ) {

        event.preventDefault();

        if (loading) {
            return;
        }

        try {

            setLoading(true);
            setError("");

            await login({
                email,
                password,
            });

            router.replace("/dashboard");

        } catch (loginError) {

            setError(
                loginError instanceof Error
                    ? loginError.message
                    : "Unable to sign in."
            );

        } finally {

            setLoading(false);

        }

    }


    return (

        <main
            className="flex min-h-screen items-center justify-center bg-slate-100 px-4 py-10"
        >

            <div className="w-full max-w-md">

                <div className="mb-8 text-center">

                    <div
                        className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-200"
                    >
                        <BrainCircuit size={34} />
                    </div>

                    <h1 className="mt-5 text-3xl font-bold tracking-tight text-slate-900">
                        AI Resume Intelligence
                    </h1>

                    <p className="mt-2 text-sm text-gray-500">
                        Sign in to access the applicant tracking system
                    </p>

                </div>


                <section
                    className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm sm:p-8"
                >

                    <div>
                        <h2 className="text-xl font-semibold text-gray-900">
                            Welcome back
                        </h2>
                        <p className="mt-1 text-sm text-gray-500">
                            Enter your recruiter or administrator credentials.
                        </p>
                    </div>


                    <form
                        onSubmit={handleSubmit}
                        className="mt-7 space-y-5"
                    >

                        {success && (

                            <div
                                role="status"
                                className="rounded-xl border border-green-200 bg-green-50 px-4 py-3 text-sm text-green-700"
                            >
                                {success}
                            </div>

                        )}

                        <div>
                            <label
                                htmlFor="email"
                                className="text-sm font-medium text-gray-700"
                            >
                                Email address
                            </label>

                            <div className="relative mt-2">
                                <Mail
                                    size={18}
                                    className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                                />
                                <input
                                    id="email"
                                    name="email"
                                    type="email"
                                    autoComplete="email"
                                    required
                                    value={email}
                                    onChange={(event) => {
                                        setEmail(event.target.value);
                                    }}
                                    className="w-full rounded-xl border border-gray-300 py-3 pl-10 pr-4 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                                    placeholder="name@example.com"
                                />
                            </div>
                        </div>


                        <div>
                            <label
                                htmlFor="password"
                                className="text-sm font-medium text-gray-700"
                            >
                                Password
                            </label>

                            <div className="relative mt-2">
                                <LockKeyhole
                                    size={18}
                                    className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400"
                                />
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    autoComplete="current-password"
                                    required
                                    value={password}
                                    onChange={(event) => {
                                        setPassword(event.target.value);
                                    }}
                                    className="w-full rounded-xl border border-gray-300 py-3 pl-10 pr-4 text-gray-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                                    placeholder="Enter your password"
                                />
                            </div>
                        </div>


                        {error && (

                            <div
                                role="alert"
                                className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700"
                            >
                                {error}
                            </div>

                        )}


                        <button
                            type="submit"
                            disabled={loading}
                            className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                            {loading && (
                                <Loader2
                                    size={18}
                                    className="animate-spin"
                                />
                            )}
                            {loading ? "Signing in..." : "Sign in"}
                        </button>

                    </form>


                    <p className="mt-6 text-center text-sm text-gray-500">
                        Need a recruiter account?{" "}
                        <Link
                            href="/register"
                            className="font-semibold text-blue-600 transition hover:text-blue-700"
                        >
                            Create account
                        </Link>
                    </p>

                </section>

            </div>

        </main>

    );

}
