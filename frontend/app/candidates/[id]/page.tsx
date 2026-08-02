import Link from "next/link";
import { ArrowLeft, UserRound } from "lucide-react";

import AppLayout from "@/components/layout/AppLayout";
import ScoreBreakdown from "@/components/candidates/ScoreBreakdown";
import { getCandidateById } from "@/services/candidate";

export const dynamic = "force-dynamic";

type Props = {
    params: Promise<{
        id: string;
    }>;
};

function scoreColor(score: number) {

    if (score >= 80)
        return "bg-green-100 text-green-700";

    if (score >= 60)
        return "bg-blue-100 text-blue-700";

    if (score >= 40)
        return "bg-yellow-100 text-yellow-700";

    return "bg-red-100 text-red-700";

}

function levelColor(level: string) {

    switch (level) {

        case "Senior":
            return "bg-purple-100 text-purple-700";

        case "Mid-Level":
            return "bg-blue-100 text-blue-700";

        case "Junior":
            return "bg-green-100 text-green-700";

        default:
            return "bg-yellow-100 text-yellow-700";

    }

}

function statusColor(status: string) {

    switch (status?.toLowerCase()) {

        case "completed":
            return "bg-green-100 text-green-700";

        case "processing":
            return "bg-yellow-100 text-yellow-700";

        case "failed":
            return "bg-red-100 text-red-700";

        default:
            return "bg-gray-100 text-gray-700";

    }

}

export default async function CandidateDetailPage({
    params,
}: Props) {


    const { id } = await params;

    const candidate = await getCandidateById(
        Number(id)
    );

    return (

        <AppLayout
            title="Candidate Detail"
            description="Candidate profile and AI evaluation"
        >

            <Link
                href="/candidates"
                className="
                    mb-6
                    inline-flex
                    items-center
                    gap-2
                    rounded-lg
                    border
                    bg-white
                    px-4
                    py-2
                    text-sm
                    font-medium
                    text-gray-700
                    shadow-sm
                    transition
                    hover:bg-gray-50
                "
            >

                <ArrowLeft size={18} />

                Back to Candidates

            </Link>

            <div
                className="
                    rounded-xl
                    border
                    bg-white
                    p-8
                    shadow-sm
                "
            >

                <div
                    className="
                        flex
                        flex-col
                        justify-between
                        gap-6
                        md:flex-row
                        md:items-center
                    "
                >

                    <div>

                        <div className="flex items-center gap-3">

                            <UserRound
                                size={28}
                                className="text-blue-600"
                            />


                            <h2 className="text-3xl font-bold text-gray-900">
                                {candidate.name}
                            </h2>

                        </div>

                        <p className="mt-3 text-sm text-gray-500">
                            Candidate ID #{candidate.id}
                        </p>

                        <div className="mt-4 flex gap-3">

                            <span
                                className={`
                                    rounded-full
                                    px-3
                                    py-1
                                    text-sm
                                    font-semibold
                                    ${levelColor(
                                    candidate.candidate_level
                                )}
                                `}
                            >
                                {candidate.candidate_level}
                            </span>


                            <span
                                className={`
                                    rounded-full
                                    px-3
                                    py-1
                                    text-sm
                                    font-semibold
                                    ${statusColor(
                                    candidate.ai_status
                                )}
                                `}
                            >
                                {candidate.ai_status}
                            </span>


                        </div>


                    </div>

                    <div>

                        <span
                            className={`
                                rounded-xl
                                px-5
                                py-3
                                text-xl
                                font-bold
                                ${scoreColor(
                                candidate.ai_score
                            )}
                            `}
                        >

                            AI Score {candidate.ai_score}

                        </span>


                    </div>


                </div>


            </div>

            <div
                className="
                    mt-6
                    grid
                    gap-6
                    md:grid-cols-3
                "
            >

                <div className="rounded-xl border bg-white p-6 shadow-sm">

                    <p className="text-sm text-gray-500">
                        Skill Score
                    </p>

                    <p className="mt-3 text-4xl font-bold">
                        {candidate.skill_score}
                    </p>

                </div>

                <div className="rounded-xl border bg-white p-6 shadow-sm">

                    <p className="text-sm text-gray-500">
                        Rule Score
                    </p>

                    <p className="mt-3 text-4xl font-bold">
                        {candidate.rule_score}
                    </p>

                </div>

                <div className="rounded-xl border bg-white p-6 shadow-sm">

                    <p className="text-sm text-gray-500">
                        AI Score
                    </p>

                    <p className="mt-3 text-4xl font-bold">
                        {candidate.ai_score}
                    </p>

                </div>


            </div>

            <div
                className="
                    mt-6
                    rounded-xl
                    border
                    bg-white
                    p-6
                    shadow-sm
                "
            >

                <h3 className="text-lg font-semibold">
                    AI Summary
                </h3>


                <p className="mt-4 whitespace-pre-line leading-7 text-gray-700">

                    {candidate.summary ||
                        "No AI summary available."
                    }

                </p>


            </div>

            <ScoreBreakdown

                breakdown={
                    candidate.score_breakdown ?? {}
                }

            />

        </AppLayout>

    );

}