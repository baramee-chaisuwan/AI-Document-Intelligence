import Link from "next/link";

import {
    AlertCircle,
    CheckCircle2,
    Circle,
    Clock3,
    Loader2,
} from "lucide-react";


export type UploadProgressState = (
    "idle"
    | "uploading"
    | "queued"
    | "processing"
    | "completed"
    | "duplicate"
    | "failed"
    | "polling_error"
    | "timed_out"
);


interface ProcessingStatusProps {
    state: UploadProgressState;
    message: string;
    processingJobId: number | null;
    candidateId: number | null;
    onRetryPolling: () => void;
}


const STEPS = [
    { key: "uploading", label: "Uploading" },
    { key: "queued", label: "Queued" },
    { key: "processing", label: "AI Processing" },
    { key: "completed", label: "Completed" },
] as const;


const PROGRESS_INDEX: Record<UploadProgressState, number> = {
    idle: -1,
    uploading: 0,
    queued: 1,
    processing: 2,
    completed: 3,
    duplicate: -1,
    failed: -1,
    polling_error: -1,
    timed_out: -1,
};


export default function ProcessingStatus({
    state,
    message,
    processingJobId,
    candidateId,
    onRetryPolling,
}: ProcessingStatusProps) {

    if (state === "idle") {
        return null;
    }

    const currentIndex = PROGRESS_INDEX[state];
    const isFailure = state === "failed";
    const isDuplicate = state === "duplicate";
    const canRetryPolling = (
        state === "polling_error"
        || state === "timed_out"
    ) && processingJobId !== null;

    return (
        <section
            aria-live="polite"
            className="mt-6 rounded-xl border border-gray-200 bg-gray-50 p-5"
        >
            <div className="grid gap-3 sm:grid-cols-4">
                {STEPS.map((step, index) => {
                    const isCurrent = index === currentIndex;
                    const isComplete = index < currentIndex;

                    return (
                        <div
                            key={step.key}
                            className={`flex items-center gap-2 rounded-lg border px-3 py-2.5 text-sm font-medium ${
                                isCurrent
                                    ? "border-blue-200 bg-blue-50 text-blue-700"
                                    : isComplete
                                        ? "border-green-200 bg-green-50 text-green-700"
                                        : "border-gray-200 bg-white text-gray-500"
                            }`}
                        >
                            {isComplete ? (
                                <CheckCircle2 size={17} />
                            ) : isCurrent && state !== "completed" ? (
                                <Loader2
                                    size={17}
                                    className="animate-spin"
                                />
                            ) : isCurrent ? (
                                <CheckCircle2 size={17} />
                            ) : (
                                <Circle size={17} />
                            )}
                            {step.label}
                        </div>
                    );
                })}
            </div>

            <div
                role={isFailure ? "alert" : "status"}
                className={`mt-4 flex items-start gap-3 rounded-lg border p-4 ${
                    isFailure
                        ? "border-red-200 bg-red-50 text-red-700"
                        : isDuplicate
                            ? "border-amber-200 bg-amber-50 text-amber-800"
                            : state === "completed"
                                ? "border-green-200 bg-green-50 text-green-700"
                                : canRetryPolling
                                    ? "border-amber-200 bg-amber-50 text-amber-800"
                                    : "border-blue-200 bg-blue-50 text-blue-700"
                }`}
            >
                {isFailure ? (
                    <AlertCircle className="mt-0.5 shrink-0" size={20} />
                ) : isDuplicate ? (
                    <AlertCircle className="mt-0.5 shrink-0" size={20} />
                ) : state === "completed" ? (
                    <CheckCircle2 className="mt-0.5 shrink-0" size={20} />
                ) : canRetryPolling ? (
                    <Clock3 className="mt-0.5 shrink-0" size={20} />
                ) : (
                    <Loader2
                        className="mt-0.5 shrink-0 animate-spin"
                        size={20}
                    />
                )}

                <div>
                    <p className="font-medium">{message}</p>

                    {processingJobId !== null && (
                        <p className="mt-1 text-xs opacity-75">
                            Processing job #{processingJobId}
                        </p>
                    )}

                    {state === "completed" && candidateId !== null && (
                        <Link
                            href={`/candidates/${candidateId}`}
                            className="mt-4 inline-flex rounded-lg bg-gray-900 px-5 py-2 text-sm font-medium text-white transition-colors hover:bg-black"
                        >
                            View Candidate
                        </Link>
                    )}

                    {isDuplicate && candidateId !== null && (
                        <Link
                            href={`/candidates/${candidateId}`}
                            className="mt-4 inline-flex rounded-lg bg-gray-900 px-5 py-2 text-sm font-medium text-white transition-colors hover:bg-black"
                        >
                            View Existing Candidate
                        </Link>
                    )}

                    {isDuplicate && candidateId === null && (
                        <p className="mt-2 text-sm">
                            This resume is already being processed. Select
                            another file to continue.
                        </p>
                    )}

                    {canRetryPolling && (
                        <button
                            type="button"
                            onClick={onRetryPolling}
                            className="mt-4 rounded-lg bg-gray-900 px-5 py-2 text-sm font-medium text-white transition-colors hover:bg-black"
                        >
                            Check status again
                        </button>
                    )}
                </div>
            </div>
        </section>
    );
}
