"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import {
    Eye,
    Trash2,
} from "lucide-react";

import { deleteCandidate } from "@/services/candidate";

import type {
    Candidate,
} from "@/services/candidate";


type CandidateTableProps = {
    candidates: Candidate[];
};


function levelBadge(
    level: string
) {

    switch (level) {

        case "Senior":
            return "bg-purple-100 text-purple-700";

        case "Mid-Level":
            return "bg-blue-100 text-blue-700";

        case "Junior":
            return "bg-green-100 text-green-700";

        case "Entry-Level":
            return "bg-yellow-100 text-yellow-700";

        default:
            return "bg-gray-100 text-gray-700";

    }

}


function scoreBadge(
    score: number
) {

    if (score >= 80) {
        return "bg-green-100 text-green-700";
    }

    if (score >= 60) {
        return "bg-blue-100 text-blue-700";
    }

    if (score >= 40) {
        return "bg-yellow-100 text-yellow-700";
    }

    return "bg-red-100 text-red-700";

}


function statusBadge(
    status?: string
) {

    switch (
    status?.toLowerCase()
    ) {

        case "success":
            return "bg-green-100 text-green-700";

        case "fallback":
            return "bg-yellow-100 text-yellow-700";

        case "failed":
        case "error":
            return "bg-red-100 text-red-700";

        case "processing":
            return "bg-blue-100 text-blue-700";

        default:
            return "bg-gray-100 text-gray-700";

    }

}


function statusLabel(
    status?: string
) {

    switch (
    status?.toLowerCase()
    ) {

        case "success":
            return "AI Success";

        case "fallback":
            return "Rule Fallback";

        case "failed":
        case "error":
            return "Failed";

        case "processing":
            return "Processing";

        default:
            return status || "Unknown";

    }

}


export default function CandidateTable({
    candidates,
}: CandidateTableProps) {

    const router = useRouter();

    const [
        deletingId,
        setDeletingId,
    ] = useState<number | null>(
        null
    );

    const [
        errorMessage,
        setErrorMessage,
    ] = useState("");


    async function handleDelete(
        candidate: Candidate
    ) {

        const confirmDelete = window.confirm(
            `Delete ${candidate.name}? This action cannot be undone.`
        );


        if (!confirmDelete) {
            return;
        }


        try {

            setErrorMessage("");
            setDeletingId(
                candidate.id
            );


            await deleteCandidate(
                candidate.id
            );


            router.refresh();

        } catch (error) {

            setErrorMessage(
                error instanceof Error
                    ? error.message
                    : "Failed to delete candidate."
            );

        } finally {

            setDeletingId(
                null
            );

        }

    }


    if (
        !candidates
        || candidates.length === 0
    ) {

        return (

            <section
                className="
                    mt-6
                    rounded-2xl
                    border
                    border-dashed
                    border-gray-200
                    bg-white
                    p-10
                    text-center
                    shadow-sm
                "
            >

                <h3
                    className="
                        text-lg
                        font-semibold
                        text-gray-900
                    "
                >
                    No Candidates Found
                </h3>

                <p
                    className="
                        mt-2
                        text-sm
                        text-gray-500
                    "
                >
                    Upload resumes to start AI candidate evaluation.
                </p>

                <Link
                    href="/upload"
                    className="
                        mt-5
                        inline-flex
                        rounded-lg
                        bg-blue-600
                        px-4
                        py-2
                        text-sm
                        font-medium
                        text-white
                        transition-colors
                        hover:bg-blue-700
                    "
                >
                    Upload Resume
                </Link>

            </section>

        );

    }


    return (

        <section
            className="
                mt-6
                overflow-hidden
                rounded-2xl
                border
                border-gray-200
                bg-white
                shadow-sm
            "
        >

            {errorMessage && (

                <div
                    role="alert"
                    className="
                        border-b
                        border-red-200
                        bg-red-50
                        px-6
                        py-4
                        text-sm
                        text-red-700
                    "
                >
                    {errorMessage}
                </div>

            )}


            <div className="overflow-x-auto">

                <table
                    className="
                        min-w-[760px]
                        w-full
                    "
                >

                    <thead className="bg-gray-50">

                        <tr>

                            <th
                                className="
                                    px-6
                                    py-4
                                    text-left
                                    text-sm
                                    font-semibold
                                    text-gray-600
                                "
                            >
                                Candidate
                            </th>

                            <th
                                className="
                                    px-6
                                    py-4
                                    text-left
                                    text-sm
                                    font-semibold
                                    text-gray-600
                                "
                            >
                                Level
                            </th>

                            <th
                                className="
                                    px-6
                                    py-4
                                    text-left
                                    text-sm
                                    font-semibold
                                    text-gray-600
                                "
                            >
                                AI Score
                            </th>

                            <th
                                className="
                                    px-6
                                    py-4
                                    text-left
                                    text-sm
                                    font-semibold
                                    text-gray-600
                                "
                            >
                                AI Status
                            </th>

                            <th
                                className="
                                    px-6
                                    py-4
                                    text-right
                                    text-sm
                                    font-semibold
                                    text-gray-600
                                "
                            >
                                Action
                            </th>

                        </tr>

                    </thead>


                    <tbody>

                        {candidates.map(
                            (candidate) => (

                                <tr
                                    key={candidate.id}
                                    className="
                                        border-t
                                        border-gray-100
                                        transition-colors
                                        hover:bg-gray-50
                                    "
                                >

                                    <td
                                        className="
                                            max-w-xs
                                            px-6
                                            py-4
                                        "
                                    >

                                        <p
                                            className="
                                                truncate
                                                font-medium
                                                text-gray-900
                                            "
                                            title={candidate.name}
                                        >
                                            {candidate.name}
                                        </p>

                                        <p
                                            className="
                                                mt-1
                                                text-xs
                                                text-gray-500
                                            "
                                        >
                                            Candidate #{candidate.id}
                                        </p>

                                    </td>


                                    <td className="px-6 py-4">

                                        <span
                                            className={`
                                                inline-flex
                                                rounded-full
                                                px-3
                                                py-1
                                                text-sm
                                                font-semibold
                                                ${levelBadge(
                                                candidate.candidate_level
                                            )}
                                            `}
                                        >
                                            {candidate.candidate_level}
                                        </span>

                                    </td>


                                    <td className="px-6 py-4">

                                        <span
                                            className={`
                                                inline-flex
                                                min-w-12
                                                justify-center
                                                rounded-full
                                                px-3
                                                py-1
                                                text-sm
                                                font-bold
                                                ${scoreBadge(
                                                candidate.ai_score
                                            )}
                                            `}
                                        >
                                            {candidate.ai_score}
                                        </span>

                                    </td>


                                    <td className="px-6 py-4">

                                        <span
                                            className={`
                                                inline-flex
                                                rounded-full
                                                px-3
                                                py-1
                                                text-sm
                                                font-medium
                                                ${statusBadge(
                                                candidate.ai_status
                                            )}
                                            `}
                                        >
                                            {statusLabel(
                                                candidate.ai_status
                                            )}
                                        </span>

                                    </td>


                                    <td
                                        className="
                                            px-6
                                            py-4
                                            text-right
                                        "
                                    >

                                        <div
                                            className="
                                                flex
                                                justify-end
                                                gap-2
                                            "
                                        >

                                            <Link
                                                href={`/candidates/${candidate.id}`}
                                                aria-label={
                                                    `View ${candidate.name}`
                                                }
                                                className="
                                                    inline-flex
                                                    items-center
                                                    gap-1.5
                                                    rounded-lg
                                                    border
                                                    border-gray-200
                                                    px-3
                                                    py-2
                                                    text-sm
                                                    font-medium
                                                    text-blue-600
                                                    transition-colors
                                                    hover:border-blue-200
                                                    hover:bg-blue-50
                                                "
                                            >
                                                <Eye size={16} />
                                                View
                                            </Link>


                                            <button
                                                type="button"
                                                onClick={() =>
                                                    handleDelete(
                                                        candidate
                                                    )
                                                }
                                                disabled={
                                                    deletingId
                                                    === candidate.id
                                                }
                                                aria-label={
                                                    `Delete ${candidate.name}`
                                                }
                                                className="
                                                    inline-flex
                                                    items-center
                                                    gap-1.5
                                                    rounded-lg
                                                    border
                                                    border-red-200
                                                    px-3
                                                    py-2
                                                    text-sm
                                                    font-medium
                                                    text-red-600
                                                    transition-colors
                                                    hover:bg-red-50
                                                    disabled:cursor-not-allowed
                                                    disabled:opacity-50
                                                "
                                            >
                                                <Trash2 size={16} />

                                                {
                                                    deletingId
                                                        === candidate.id
                                                        ? "Deleting..."
                                                        : "Delete"
                                                }
                                            </button>

                                        </div>

                                    </td>

                                </tr>

                            )
                        )}

                    </tbody>

                </table>

            </div>

        </section>

    );

}