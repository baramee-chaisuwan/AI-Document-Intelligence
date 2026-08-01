"use client";

export default function Error({
    reset,
}: {
    reset: () => void;
}) {
    return (
        <div className="flex h-64 flex-col items-center justify-center gap-4">
            <p className="text-red-500">
                Failed to load candidates.
            </p>

            <button
                onClick={() => reset()}
                className="rounded-lg bg-blue-600 px-4 py-2 text-white"
            >
                Try again
            </button>
        </div>
    );
}