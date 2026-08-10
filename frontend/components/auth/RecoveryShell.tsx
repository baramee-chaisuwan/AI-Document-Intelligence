import Link from "next/link";
import { BrainCircuit } from "lucide-react";


export default function RecoveryShell({
    title,
    description,
    children,
}: {
    title: string;
    description: string;
    children: React.ReactNode;
}) {
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
                </div>
                <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm sm:p-8">
                    <h2 className="text-xl font-semibold text-gray-900">
                        {title}
                    </h2>
                    <p className="mt-1 text-sm leading-6 text-gray-500">
                        {description}
                    </p>
                    {children}
                    <p className="mt-6 text-center text-sm text-gray-500">
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
