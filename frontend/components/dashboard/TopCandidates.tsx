import Link from "next/link";

import {
    Eye,
    Trophy,
} from "lucide-react";

import type {
    TopCandidate,
} from "@/services/dashboard";


type Props = {
    candidates: TopCandidate[];
};


function scoreColor(
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


function rankBadge(
    rank: number
) {

    if (rank === 1) {
        return "🥇";
    }

    if (rank === 2) {
        return "🥈";
    }

    if (rank === 3) {
        return "🥉";
    }

    return `#${rank}`;
}


export default function TopCandidates({
    candidates,
}: Props) {

    return (

        <section
            className="
                rounded-2xl
                border
                border-gray-200
                bg-white
                p-6
                shadow-sm
            "
        >

            <div
                className="
                    mb-5
                    flex
                    items-center
                    justify-between
                    gap-4
                "
            >

                <div
                    className="
                        flex
                        items-center
                        gap-2
                    "
                >

                    <Trophy
                        size={22}
                        className="text-yellow-500"
                    />

                    <h3
                        className="
                            text-lg
                            font-semibold
                            text-gray-900
                        "
                    >
                        Top Candidates
                    </h3>

                </div>

                <span
                    className="
                        rounded-full
                        bg-gray-100
                        px-3
                        py-1
                        text-xs
                        font-medium
                        text-gray-600
                    "
                >
                    {candidates.length} candidates
                </span>

            </div>


            {candidates.length === 0 ? (

                <div
                    className="
                        flex
                        min-h-56
                        items-center
                        justify-center
                        rounded-xl
                        border
                        border-dashed
                        border-gray-200
                        bg-gray-50
                        px-6
                        text-center
                        text-sm
                        text-gray-500
                    "
                >
                    No ranked candidates are available yet.
                </div>

            ) : (

                <div className="overflow-x-auto">

                    <table className="w-full min-w-[620px]">

                        <thead>

                            <tr
                                className="
                                    border-b
                                    text-left
                                    text-sm
                                    text-gray-500
                                "
                            >

                                <th className="pb-3 font-medium">
                                    Rank
                                </th>

                                <th className="pb-3 font-medium">
                                    Candidate
                                </th>

                                <th className="pb-3 font-medium">
                                    AI Score
                                </th>

                                <th
                                    className="
                                        pb-3
                                        text-right
                                        font-medium
                                    "
                                >
                                    Action
                                </th>

                            </tr>

                        </thead>


                        <tbody>

                            {candidates.map(
                                (
                                    candidate,
                                    index
                                ) => (

                                    <tr
                                        key={candidate.id}
                                        className="
                                            border-b
                                            last:border-b-0
                                            transition-colors
                                            hover:bg-gray-50
                                        "
                                    >

                                        <td
                                            className="
                                                py-4
                                                text-lg
                                                font-semibold
                                                text-gray-900
                                            "
                                        >
                                            {rankBadge(index + 1)}
                                        </td>


                                        <td
                                            className="
                                                max-w-xs
                                                py-4
                                                font-medium
                                                text-gray-900
                                            "
                                        >
                                            <span
                                                className="
                                                    block
                                                    truncate
                                                "
                                                title={candidate.name}
                                            >
                                                {candidate.name}
                                            </span>
                                        </td>


                                        <td className="py-4">

                                            <span
                                                className={`
                                                    inline-flex
                                                    min-w-12
                                                    justify-center
                                                    rounded-full
                                                    px-3
                                                    py-1
                                                    text-sm
                                                    font-semibold
                                                    ${scoreColor(
                                                    candidate.ai_score
                                                )}
                                                `}
                                            >
                                                {candidate.ai_score}
                                            </span>

                                        </td>


                                        <td className="py-4 text-right">

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

                                        </td>

                                    </tr>

                                )
                            )}

                        </tbody>

                    </table>

                </div>

            )}

        </section>

    );
}