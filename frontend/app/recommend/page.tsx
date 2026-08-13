"use client";

import Link from "next/link";
import {
    Bot,
    BriefcaseBusiness,
    CheckCircle2,
    ExternalLink,
    Loader2,
    Search,
    Sparkles,
    Target,
} from "lucide-react";
import { useState } from "react";

import AppLayout from "@/components/layout/AppLayout";

import {
    getRecommendation,
} from "@/services/recommend";

import type {
    RecommendationResponse,
} from "@/services/recommend";


const MAX_REQUIREMENT_LENGTH = 2000;


const EXAMPLE_REQUIREMENTS = [
    "AI Engineer with Python, RAG, LLM, FastAPI, and Docker experience",
    "Project Manager with PMP, budget ownership, risk management, and stakeholder leadership",
    "Accountant with CPA, GAAP reporting, reconciliation, audit, and financial controls",
];


function clampScore(
    score: number
) {

    if (!Number.isFinite(score)) {
        return 0;
    }

    return Math.min(
        Math.max(
            Math.round(score),
            0
        ),
        100
    );

}


function scoreStyles(
    score: number
) {

    if (score >= 80) {

        return {
            badge: "bg-green-100 text-green-700",
            bar: "bg-green-500",
        };

    }

    if (score >= 60) {

        return {
            badge: "bg-blue-100 text-blue-700",
            bar: "bg-blue-500",
        };

    }

    if (score >= 40) {

        return {
            badge: "bg-amber-100 text-amber-700",
            bar: "bg-amber-500",
        };

    }

    return {
        badge: "bg-red-100 text-red-700",
        bar: "bg-red-500",
    };

}


export default function RecommendPage() {

    const [
        question,
        setQuestion,
    ] = useState("");

    const [
        result,
        setResult,
    ] = useState<RecommendationResponse | null>(
        null
    );

    const [
        loading,
        setLoading,
    ] = useState(false);

    const [
        error,
        setError,
    ] = useState("");


    const normalizedQuestion = (
        question.trim()
    );

    const isQuestionValid = (
        normalizedQuestion.length > 0
        && normalizedQuestion.length
        <= MAX_REQUIREMENT_LENGTH
    );


    async function handleRecommend() {

        if (!normalizedQuestion) {

            setError(
                "Please describe the job requirement."
            );

            return;

        }


        if (
            normalizedQuestion.length
            > MAX_REQUIREMENT_LENGTH
        ) {

            setError(
                `Job requirement must not exceed `
                + `${MAX_REQUIREMENT_LENGTH} characters.`
            );

            return;

        }


        try {

            setLoading(true);
            setError("");
            setResult(null);


            const data = await getRecommendation(
                normalizedQuestion
            );


            setResult(
                data
            );

        } catch (error) {

            setError(
                error instanceof Error
                    ? error.message
                    : "Unable to generate recommendation."
            );

        } finally {

            setLoading(false);

        }

    }


    function applyExample(
        requirement: string
    ) {

        setQuestion(
            requirement
        );

        setError("");
        setResult(null);

    }


    const hasCandidate = Boolean(
        result
        && result.candidate_id
        && result.candidate_id !== "N/A"
    );

    const matchScore = clampScore(
        result?.match_score ?? 0
    );

    const scoreStyle = scoreStyles(
        matchScore
    );


    return (

        <AppLayout
            title="Recommendation"
            description={
                "Find the best candidate for a job requirement "
                + "using hybrid retrieval and AI evaluation"
            }
        >

            <section
                className="
                    mt-8
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
                        items-start
                        gap-4
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
                        <Target
                            size={25}
                            className="text-blue-600"
                        />
                    </div>


                    <div>

                        <h2
                            className="
                                text-xl
                                font-semibold
                                text-gray-900
                            "
                        >
                            Find the Best Candidate
                        </h2>

                        <p
                            className="
                                mt-1
                                text-sm
                                leading-6
                                text-gray-500
                            "
                        >
                            Describe the role, required competencies,
                            responsibilities, credentials, and preferred experience.
                        </p>

                    </div>

                </div>


                <label
                    htmlFor="job-requirement"
                    className="
                        mt-7
                        block
                        text-sm
                        font-medium
                        text-gray-700
                    "
                >
                    Job Requirement
                </label>


                <textarea
                    id="job-requirement"
                    value={question}
                    disabled={loading}
                    maxLength={
                        MAX_REQUIREMENT_LENGTH
                    }
                    onChange={(event) => {

                        setQuestion(
                            event.target.value
                        );

                        setError("");

                    }}
                    placeholder={
                        "Example: AI Engineer with Python, "
                        + "FastAPI, RAG, LLM, Docker, and "
                        + "production deployment experience"
                    }
                    rows={7}
                    className="
                        mt-2
                        w-full
                        resize-y
                        rounded-xl
                        border
                        border-gray-300
                        bg-white
                        p-4
                        text-gray-900
                        outline-none
                        transition
                        placeholder:text-gray-400
                        focus:border-blue-500
                        focus:ring-4
                        focus:ring-blue-100
                        disabled:cursor-not-allowed
                        disabled:bg-gray-50
                    "
                />


                <div
                    className="
                        mt-2
                        flex
                        items-center
                        justify-between
                        gap-4
                        text-xs
                        text-gray-500
                    "
                >

                    <span>
                        Include required skills and responsibilities
                        for a more accurate match.
                    </span>

                    <span>
                        {question.length}/{MAX_REQUIREMENT_LENGTH}
                    </span>

                </div>


                <div className="mt-5">

                    <p
                        className="
                            text-xs
                            font-medium
                            uppercase
                            tracking-wide
                            text-gray-500
                        "
                    >
                        Try an example
                    </p>


                    <div
                        className="
                            mt-3
                            flex
                            flex-wrap
                            gap-2
                        "
                    >

                        {EXAMPLE_REQUIREMENTS.map(
                            (
                                requirement,
                                index
                            ) => (

                                <button
                                    key={requirement}
                                    type="button"
                                    disabled={loading}
                                    onClick={() =>
                                        applyExample(
                                            requirement
                                        )
                                    }
                                    className="
                                        rounded-full
                                        border
                                        border-gray-200
                                        bg-gray-50
                                        px-3
                                        py-2
                                        text-left
                                        text-xs
                                        text-gray-700
                                        transition-colors
                                        hover:border-blue-200
                                        hover:bg-blue-50
                                        disabled:cursor-not-allowed
                                        disabled:opacity-50
                                    "
                                >
                                    Example {index + 1}
                                </button>

                            )
                        )}

                    </div>

                </div>


                <button
                    type="button"
                    onClick={
                        handleRecommend
                    }
                    disabled={
                        loading
                        || !isQuestionValid
                    }
                    className="
                        mt-6
                        inline-flex
                        w-full
                        items-center
                        justify-center
                        gap-2
                        rounded-xl
                        bg-blue-600
                        px-6
                        py-3.5
                        font-medium
                        text-white
                        transition-colors
                        hover:bg-blue-700
                        disabled:cursor-not-allowed
                        disabled:opacity-50
                        sm:w-auto
                    "
                >

                    {loading ? (

                        <>
                            <Loader2
                                size={19}
                                className="animate-spin"
                            />

                            Comparing Candidates...
                        </>

                    ) : (

                        <>
                            <Search size={19} />
                            Recommend Candidate
                        </>

                    )}

                </button>


                {loading && (

                    <p
                        role="status"
                        className="
                            mt-3
                            text-sm
                            text-gray-500
                        "
                    >
                        Retrieving relevant resumes and evaluating
                        candidate evidence against the requirement.
                    </p>

                )}

            </section>


            {error && (

                <div
                    role="alert"
                    className="
                        mt-6
                        rounded-xl
                        border
                        border-red-200
                        bg-red-50
                        p-4
                        text-sm
                        text-red-700
                    "
                >
                    {error}
                </div>

            )}


            {result && !hasCandidate && (

                <section
                    className="
                        mt-6
                        rounded-2xl
                        border
                        border-dashed
                        border-gray-300
                        bg-white
                        p-10
                        text-center
                        shadow-sm
                    "
                >

                    <BriefcaseBusiness
                        size={36}
                        className="
                            mx-auto
                            text-gray-400
                        "
                    />

                    <h3
                        className="
                            mt-4
                            text-lg
                            font-semibold
                            text-gray-900
                        "
                    >
                        No Matching Candidate Found
                    </h3>

                    <p
                        className="
                            mx-auto
                            mt-2
                            max-w-xl
                            text-sm
                            leading-6
                            text-gray-500
                        "
                    >
                        {result.reason
                            || (
                                "No indexed resume contained enough "
                                + "evidence to support a recommendation."
                            )}
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

            )}


            {result && hasCandidate && (

                <section
                    className="
                        mt-6
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
                            gap-5
                            md:flex-row
                            md:items-center
                        "
                    >

                        <div
                            className="
                                flex
                                min-w-0
                                items-start
                                gap-4
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
                                    bg-purple-50
                                "
                            >
                                <Sparkles
                                    size={24}
                                    className="text-purple-600"
                                />
                            </div>


                            <div className="min-w-0">

                                <p
                                    className="
                                        text-xs
                                        font-medium
                                        uppercase
                                        tracking-wide
                                        text-purple-600
                                    "
                                >
                                    Recommended Candidate
                                </p>

                                <h3
                                    title={
                                        result.candidate_name
                                    }
                                    className="
                                        mt-1
                                        truncate
                                        text-2xl
                                        font-bold
                                        text-gray-900
                                    "
                                >
                                    {result.candidate_name}
                                </h3>

                                <p
                                    className="
                                        mt-1
                                        text-sm
                                        text-gray-500
                                    "
                                >
                                    Candidate #{result.candidate_id}
                                </p>

                            </div>

                        </div>


                        <div
                            className="
                                flex
                                flex-col
                                items-start
                                gap-3
                                sm:flex-row
                                sm:items-center
                            "
                        >

                            <div
                                className={`
                                    rounded-xl
                                    px-5
                                    py-3
                                    text-xl
                                    font-bold
                                    ${scoreStyle.badge}
                                `}
                            >
                                {matchScore}% Match
                            </div>


                            <Link
                                href={
                                    `/candidates/${result.candidate_id}`
                                }
                                className="
                                    inline-flex
                                    items-center
                                    gap-2
                                    rounded-xl
                                    border
                                    border-gray-200
                                    px-4
                                    py-3
                                    text-sm
                                    font-medium
                                    text-blue-600
                                    transition-colors
                                    hover:border-blue-200
                                    hover:bg-blue-50
                                "
                            >
                                View Profile
                                <ExternalLink size={16} />
                            </Link>

                        </div>

                    </div>


                    <div className="mt-7">

                        <div
                            className="
                                mb-2
                                flex
                                justify-between
                                text-sm
                                font-medium
                                text-gray-700
                            "
                        >
                            <span>
                                Job Match Score
                            </span>

                            <span>
                                {matchScore}/100
                            </span>
                        </div>


                        <div
                            className="
                                h-3
                                overflow-hidden
                                rounded-full
                                bg-gray-200
                            "
                            role="progressbar"
                            aria-label="Job match score"
                            aria-valuemin={0}
                            aria-valuemax={100}
                            aria-valuenow={
                                matchScore
                            }
                        >

                            <div
                                className={`
                                    h-full
                                    rounded-full
                                    transition-all
                                    duration-700
                                    ${scoreStyle.bar}
                                `}
                                style={{
                                    width: `${matchScore}%`,
                                }}
                            />

                        </div>

                    </div>


                    <div
                        className="
                            mt-8
                            grid
                            gap-6
                            xl:grid-cols-2
                        "
                    >

                        <ResultList
                            title="Strengths"
                            items={
                                result.strengths ?? []
                            }
                            variant="success"
                        />

                        <ResultList
                            title="Relevant Experience"
                            items={
                                result.relevant_experience
                                ?? []
                            }
                            variant="information"
                        />

                    </div>


                    <div
                        className="
                            mt-8
                            rounded-xl
                            border
                            border-gray-200
                            bg-gray-50
                            p-5
                        "
                    >

                        <div
                            className="
                                flex
                                items-center
                                gap-2
                            "
                        >
                            <Bot
                                size={19}
                                className="text-purple-600"
                            />

                            <h4
                                className="
                                    font-semibold
                                    text-gray-900
                                "
                            >
                                Recommendation Reason
                            </h4>
                        </div>

                        <p
                            className="
                                mt-3
                                whitespace-pre-line
                                leading-7
                                text-gray-700
                            "
                        >
                            {result.reason
                                || (
                                    "No recommendation explanation "
                                    + "was provided."
                                )}
                        </p>

                    </div>

                </section>

            )}

        </AppLayout>

    );

}


function ResultList({
    title,
    items,
    variant,
}: {
    title: string;
    items: string[];
    variant: "success" | "information";
}) {

    const classes = (
        variant === "success"
            ? (
                "border-green-100 "
                + "bg-green-50 "
                + "text-green-800"
            )
            : (
                "border-blue-100 "
                + "bg-blue-50 "
                + "text-blue-800"
            )
    );


    return (

        <div>

            <h4
                className="
                    font-semibold
                    text-gray-900
                "
            >
                {title}
            </h4>


            {items.length === 0 ? (

                <p
                    className="
                        mt-3
                        text-sm
                        text-gray-500
                    "
                >
                    No supported evidence was returned.
                </p>

            ) : (

                <ul className="mt-3 space-y-3">

                    {items.map((
                        item,
                        index
                    ) => (

                        <li
                            key={`${index}-${item}`}
                            className={`
                                flex
                                items-start
                                gap-3
                                rounded-xl
                                border
                                px-4
                                py-3
                                text-sm
                                leading-6
                                ${classes}
                            `}
                        >

                            <CheckCircle2
                                size={17}
                                className="
                                    mt-0.5
                                    shrink-0
                                "
                            />

                            <span>
                                {item}
                            </span>

                        </li>

                    ))}

                </ul>

            )}

        </div>

    );

}
