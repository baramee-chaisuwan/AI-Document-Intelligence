"use client";

import Link from "next/link";
import {
    AlertCircle,
    ArrowRight,
    ExternalLink,
    Kanban,
    Loader2,
    Users,
} from "lucide-react";
import {
    useEffect,
    useRef,
    useState,
} from "react";

import AppLayout from "@/components/layout/AppLayout";
import {
    getCandidates,
    updateCandidateStage,
} from "@/services/candidate";
import type {
    Candidate,
    CandidateStage,
} from "@/services/candidate";


const PIPELINE_LIMIT = 50;


const PIPELINE_STAGES: Array<{
    value: CandidateStage;
    label: string;
    accent: string;
    badge: string;
}> = [
    {
        value: "APPLIED",
        label: "Applied",
        accent: "border-t-blue-500",
        badge: "bg-blue-100 text-blue-700",
    },
    {
        value: "SCREENING",
        label: "Screening",
        accent: "border-t-amber-500",
        badge: "bg-amber-100 text-amber-700",
    },
    {
        value: "INTERVIEW",
        label: "Interview",
        accent: "border-t-purple-500",
        badge: "bg-purple-100 text-purple-700",
    },
    {
        value: "OFFER",
        label: "Offer",
        accent: "border-t-green-500",
        badge: "bg-green-100 text-green-700",
    },
    {
        value: "REJECTED",
        label: "Rejected",
        accent: "border-t-red-500",
        badge: "bg-red-100 text-red-700",
    },
];


export default function PipelinePage() {

    const [candidates, setCandidates] = (
        useState<Candidate[]>([])
    );
    const [loading, setLoading] = useState(true);
    const [loadError, setLoadError] = useState("");
    const [updatingIds, setUpdatingIds] = (
        useState<Set<number>>(new Set())
    );
    const [updateErrors, setUpdateErrors] = (
        useState<Record<number, string>>({})
    );
    const updatingIdsRef = useRef<Set<number>>(
        new Set()
    );


    useEffect(() => {

        let active = true;

        getCandidates(0, PIPELINE_LIMIT)
            .then((result) => {

                if (active) {
                    setCandidates(result);
                }

            })
            .catch(() => {

                if (active) {
                    setLoadError(
                        "Could not load the candidate pipeline. Please try again."
                    );
                }

            })
            .finally(() => {

                if (active) {
                    setLoading(false);
                }

            });

        return () => {
            active = false;
        };

    }, []);


    async function moveCandidate(
        candidate: Candidate,
        nextStage: CandidateStage
    ) {

        if (
            candidate.candidate_stage === nextStage
            || updatingIdsRef.current.has(candidate.id)
        ) {
            return;
        }

        updatingIdsRef.current.add(candidate.id);
        setUpdatingIds(
            new Set(updatingIdsRef.current)
        );
        setUpdateErrors((current) => {
            const next = {...current};
            delete next[candidate.id];
            return next;
        });

        try {

            const updated = await updateCandidateStage(
                candidate.id,
                nextStage
            );

            setCandidates((current) => (
                current.map((item) => (
                    item.id === candidate.id
                        ? {
                            ...item,
                            ...updated,
                        }
                        : item
                ))
            ));

        } catch (error) {

            const message = error instanceof Error
                ? error.message
                : (
                    "Could not update the candidate stage. "
                    + "Please try again."
                );

            setUpdateErrors((current) => ({
                ...current,
                [candidate.id]: message,
            }));

        } finally {

            updatingIdsRef.current.delete(candidate.id);
            setUpdatingIds(
                new Set(updatingIdsRef.current)
            );

        }

    }


    return (
        <AppLayout
            title="Candidate Pipeline"
            description="Move candidates through the recruiter hiring workflow"
        >
            <div className="mb-6 flex items-start gap-3 rounded-xl border border-blue-100 bg-blue-50 p-4 text-sm text-blue-800">
                <Kanban
                    size={20}
                    className="mt-0.5 shrink-0"
                    aria-hidden="true"
                />
                <p>
                    Showing the first {PIPELINE_LIMIT} candidates returned by the existing candidate list API.
                </p>
            </div>

            {loading ? (
                <div
                    role="status"
                    className="flex items-center justify-center gap-3 rounded-2xl border border-gray-200 bg-white p-12 text-sm text-gray-500 shadow-sm"
                >
                    <Loader2
                        size={20}
                        className="animate-spin"
                    />
                    Loading candidate pipeline...
                </div>
            ) : loadError ? (
                <div
                    role="alert"
                    className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-700"
                >
                    {loadError}
                </div>
            ) : candidates.length === 0 ? (
                <div className="rounded-2xl border border-dashed border-gray-300 bg-white p-12 text-center shadow-sm">
                    <Users
                        size={38}
                        className="mx-auto text-gray-400"
                    />
                    <h2 className="mt-4 text-lg font-semibold text-gray-900">
                        No candidates in the pipeline
                    </h2>
                    <p className="mt-2 text-sm text-gray-500">
                        Upload a resume to add the first candidate.
                    </p>
                    <Link
                        href="/upload"
                        className="mt-5 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700"
                    >
                        Upload Resume
                        <ArrowRight size={16} />
                    </Link>
                </div>
            ) : (
                <div className="overflow-x-auto pb-4">
                    <div className="grid min-w-[1500px] grid-cols-5 gap-4">
                        {PIPELINE_STAGES.map((stage) => {
                            const stageCandidates = candidates.filter(
                                (candidate) => (
                                    candidate.candidate_stage
                                    === stage.value
                                )
                            );

                            return (
                                <PipelineColumn
                                    key={stage.value}
                                    stage={stage}
                                    candidates={stageCandidates}
                                    updatingIds={updatingIds}
                                    updateErrors={updateErrors}
                                    onMove={moveCandidate}
                                />
                            );
                        })}
                    </div>
                </div>
            )}
        </AppLayout>
    );
}


function PipelineColumn({
    stage,
    candidates,
    updatingIds,
    updateErrors,
    onMove,
}: {
    stage: (typeof PIPELINE_STAGES)[number];
    candidates: Candidate[];
    updatingIds: Set<number>;
    updateErrors: Record<number, string>;
    onMove: (
        candidate: Candidate,
        stage: CandidateStage
    ) => Promise<void>;
}) {

    return (
        <section
            aria-labelledby={`pipeline-${stage.value}`}
            className={`min-h-[28rem] rounded-2xl border border-t-4 border-gray-200 bg-gray-50 p-4 ${stage.accent}`}
        >
            <div className="flex items-center justify-between gap-3">
                <h2
                    id={`pipeline-${stage.value}`}
                    className="font-semibold text-gray-900"
                >
                    {stage.label}
                </h2>
                <span
                    className={`rounded-full px-2.5 py-1 text-xs font-semibold ${stage.badge}`}
                    aria-label={`${candidates.length} candidates`}
                >
                    {candidates.length}
                </span>
            </div>

            {candidates.length === 0 ? (
                <div className="mt-4 rounded-xl border border-dashed border-gray-300 bg-white p-6 text-center text-sm text-gray-400">
                    No candidates
                </div>
            ) : (
                <div className="mt-4 space-y-3">
                    {candidates.map((candidate) => (
                        <CandidatePipelineCard
                            key={candidate.id}
                            candidate={candidate}
                            updating={updatingIds.has(candidate.id)}
                            error={updateErrors[candidate.id]}
                            onMove={onMove}
                        />
                    ))}
                </div>
            )}
        </section>
    );
}


function CandidatePipelineCard({
    candidate,
    updating,
    error,
    onMove,
}: {
    candidate: Candidate;
    updating: boolean;
    error?: string;
    onMove: (
        candidate: Candidate,
        stage: CandidateStage
    ) => Promise<void>;
}) {

    return (
        <article className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
            <div className="flex items-start justify-between gap-3">
                <div className="min-w-0">
                    <h3
                        className="truncate font-semibold text-gray-900"
                        title={candidate.name}
                    >
                        {candidate.name}
                    </h3>
                    <p className="mt-1 text-xs text-gray-500">
                        Candidate #{candidate.id}
                    </p>
                </div>
                <span className="shrink-0 rounded-full bg-blue-50 px-2.5 py-1 text-xs font-semibold text-blue-700">
                    AI {candidate.ai_score}
                </span>
            </div>

            <div className="mt-4 flex items-center justify-between gap-3 border-t border-gray-100 pt-3">
                <span className="rounded-md bg-gray-100 px-2 py-1 text-xs font-medium text-gray-700">
                    {candidate.candidate_level}
                </span>
                <Link
                    href={`/candidates/${candidate.id}`}
                    className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700"
                >
                    Details
                    <ExternalLink size={13} />
                </Link>
            </div>

            <div className="mt-4">
                <label
                    htmlFor={`candidate-stage-${candidate.id}`}
                    className="text-xs font-medium text-gray-600"
                >
                    Move to stage
                </label>
                <div className="relative mt-1.5">
                    <select
                        id={`candidate-stage-${candidate.id}`}
                        value={candidate.candidate_stage}
                        disabled={updating}
                        onChange={(event) => {
                            void onMove(
                                candidate,
                                event.target.value as CandidateStage
                            );
                        }}
                        className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 pr-9 text-sm text-gray-800 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:cursor-wait disabled:bg-gray-100"
                    >
                        {PIPELINE_STAGES.map((stage) => (
                            <option
                                key={stage.value}
                                value={stage.value}
                            >
                                {stage.label}
                            </option>
                        ))}
                    </select>
                    {updating && (
                        <Loader2
                            size={15}
                            className="pointer-events-none absolute right-8 top-2.5 animate-spin text-blue-600"
                            aria-label="Updating candidate stage"
                        />
                    )}
                </div>
            </div>

            {error && (
                <div
                    role="alert"
                    className="mt-3 flex items-start gap-2 rounded-lg bg-red-50 p-2.5 text-xs leading-5 text-red-700"
                >
                    <AlertCircle
                        size={14}
                        className="mt-0.5 shrink-0"
                    />
                    {error}
                </div>
            )}
        </article>
    );
}
