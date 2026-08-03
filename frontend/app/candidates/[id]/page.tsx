import Link from "next/link";
import { notFound } from "next/navigation";

import {
    ArrowLeft,
    Bot,
    UserRound,
} from "lucide-react";

import AppLayout from "@/components/layout/AppLayout";
import ScoreBreakdown from "@/components/candidates/ScoreBreakdown";

import { getCandidateById } from "@/services/candidate";


export const dynamic = "force-dynamic";


type Props = {
    params: Promise<{
        id: string;
    }>;
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


function levelColor(
    level: string
) {

    switch (level.toLowerCase()) {

        case "senior":
            return "bg-purple-100 text-purple-700";

        case "mid-level":
            return "bg-blue-100 text-blue-700";

        case "junior":
            return "bg-green-100 text-green-700";

        case "entry-level":
            return "bg-yellow-100 text-yellow-700";

        default:
            return "bg-gray-100 text-gray-700";

    }

}


function statusColor(
    status: string
) {

    switch (status.toLowerCase()) {

        case "success":
            return "bg-green-100 text-green-700";

        case "fallback":
            return "bg-yellow-100 text-yellow-700";

        case "processing":
            return "bg-blue-100 text-blue-700";

        case "failed":
        case "error":
            return "bg-red-100 text-red-700";

        default:
            return "bg-gray-100 text-gray-700";

    }

}


function statusLabel(
    status: string
) {

    switch (status.toLowerCase()) {

        case "success":
            return "AI Success";

        case "fallback":
            return "Rule Fallback";

        case "processing":
            return "Processing";

        case "failed":
        case "error":
            return "Failed";

        default:
            return status || "Unknown";

    }

}


export default async function CandidateDetailPage({
    params,
}: Props) {

    const { id } = await params;

    const candidateId = Number(id);


    if (
        !Number.isInteger(candidateId)
        || candidateId <= 0
    ) {

        notFound();

    }


    let candidate;


    try {

        candidate = await getCandidateById(
            candidateId
        );

    } catch {

        notFound();

    }


    const aiScore = candidate.ai_score ?? 0;
    const skillScore = candidate.skill_score ?? 0;
    const ruleScore = candidate.rule_score ?? 0;


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
                    border-gray-200
                    bg-white
                    px-4
                    py-2
                    text-sm
                    font-medium
                    text-gray-700
                    shadow-sm
                    transition-colors
                    hover:bg-gray-50
                "
            >
                <ArrowLeft size={18} />
                Back to Candidates
            </Link>


            <section
                className="
                    rounded-2xl
                    border
                    border-gray-200
                    bg-white
                    p-6
                    shadow-sm
                    sm:p-8
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

                    <div className="min-w-0">

                        <div
                            className="
                                flex
                                items-center
                                gap-3
                            "
                        >

                            <div
                                className="
                                    flex
                                    h-12
                                    w-12
                                    shrink-0
                                    items-center
                                    justify-center
                                    rounded-xl
                                    bg-blue-50
                                "
                            >
                                <UserRound
                                    size={26}
                                    className="text-blue-600"
                                />
                            </div>

                            <div className="min-w-0">

                                <h2
                                    className="
                                        truncate
                                        text-2xl
                                        font-bold
                                        text-gray-900
                                        sm:text-3xl
                                    "
                                    title={candidate.name}
                                >
                                    {candidate.name}
                                </h2>

                                <p
                                    className="
                                        mt-1
                                        text-sm
                                        text-gray-500
                                    "
                                >
                                    Candidate #{candidate.id}
                                </p>

                            </div>

                        </div>


                        <div
                            className="
                                mt-5
                                flex
                                flex-wrap
                                gap-3
                            "
                        >

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
                                {statusLabel(
                                    candidate.ai_status
                                )}
                            </span>

                        </div>

                    </div>


                    <div
                        className={`
                            inline-flex
                            items-center
                            gap-2
                            self-start
                            rounded-xl
                            px-5
                            py-3
                            text-xl
                            font-bold
                            md:self-auto
                            ${scoreColor(aiScore)}
                        `}
                    >
                        <Bot size={21} />
                        AI Score {aiScore}
                    </div>

                </div>

            </section>


            <div
                className="
                    mt-6
                    grid
                    gap-6
                    sm:grid-cols-2
                    xl:grid-cols-3
                "
            >

                <ScoreCard
                    title="Final Skill Score"
                    value={skillScore}
                />

                <ScoreCard
                    title="Rule Score"
                    value={ruleScore}
                />

                <ScoreCard
                    title="AI Score"
                    value={aiScore}
                />

            </div>


            <section
                className="
                    mt-6
                    rounded-2xl
                    border
                    border-gray-200
                    bg-white
                    p-6
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
                    AI Summary
                </h3>

                <p
                    className="
                        mt-4
                        whitespace-pre-line
                        leading-7
                        text-gray-700
                    "
                >
                    {
                        candidate.summary
                        || "No AI summary available."
                    }
                </p>

            </section>


            <ScoreBreakdown
                breakdown={
                    candidate.score_breakdown
                }
            />

        </AppLayout>

    );

}


function ScoreCard({
    title,
    value,
}: {
    title: string;
    value: number;
}) {

    return (

        <div
            className="
                rounded-2xl
                border
                border-gray-200
                bg-white
                p-6
                shadow-sm
            "
        >

            <p
                className="
                    text-sm
                    font-medium
                    uppercase
                    tracking-wide
                    text-gray-500
                "
            >
                {title}
            </p>

            <div
                className="
                    mt-4
                    flex
                    items-end
                    gap-1
                "
            >

                <p
                    className="
                        text-4xl
                        font-bold
                        text-gray-900
                    "
                >
                    {value}
                </p>

                <span
                    className="
                        pb-1
                        text-sm
                        text-gray-500
                    "
                >
                    /100
                </span>

            </div>

        </div>

    );

}