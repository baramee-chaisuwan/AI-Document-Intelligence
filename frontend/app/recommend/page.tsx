"use client";

import { useState } from "react";

import {
    getRecommendation,
    RecommendationResponse,
} from "@/services/recommend";

import AppLayout from "@/components/layout/AppLayout";

export default function RecommendPage() {

    const [question, setQuestion] =
        useState("");


    const [result, setResult] =
        useState<RecommendationResponse | null>(null);


    const [loading, setLoading] =
        useState(false);


    const [error, setError] =
        useState("");

    async function handleRecommend() {


        if (!question.trim())
            return;


        try {

            setLoading(true);

            setError("");

            setResult(null);


            const data =
                await getRecommendation(
                    question
                );


            setResult(data);


        } catch (error) {

            console.error(error);


            setError(
                "Unable to generate recommendation"
            );


        } finally {

            setLoading(false);

        }

    }

    return (

        <AppLayout

            title="Recommendation"

            description="AI powered candidate recommendation"

        >

            {/* Search Section */}

            <div
                className="
                    mt-8
                    rounded-xl
                    border
                    bg-white
                    p-6
                    shadow-sm
                "
            >

                <h2 className="text-xl font-semibold text-gray-900">

                    Find Best Candidate

                </h2>


                <p className="mt-1 text-sm text-gray-500">

                    Describe the job requirement and let AI find the best matching candidate.

                </p>

                <textarea

                    value={question}

                    onChange={(e) =>
                        setQuestion(
                            e.target.value
                        )
                    }

                    placeholder="
                    Example:
                    Need Python FastAPI AI Engineer with Machine Learning experience
                    "


                    className="
                        mt-4
                        w-full
                        rounded-lg
                        border
                        p-4
                        outline-none
                        focus:ring-2
                        focus:ring-blue-500
                    "


                    rows={5}

                />

                <button

                    onClick={handleRecommend}

                    disabled={loading}


                    className="
                        mt-4
                        rounded-lg
                        bg-blue-600
                        px-6
                        py-2
                        font-medium
                        text-white
                        transition
                        hover:bg-blue-700
                        disabled:opacity-50
                    "

                >

                    {
                        loading
                            ? "Analyzing..."
                            : "Recommend"
                    }


                </button>



            </div>


            {
                error && (

                    <div
                        className="
                            mt-6
                            rounded-xl
                            bg-red-100
                            p-4
                            text-red-700
                        "
                    >

                        {error}

                    </div>

                )
            }

            {
                result && (

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

                        <div
                            className="
                                flex
                                flex-col
                                justify-between
                                gap-4
                                md:flex-row
                                md:items-center
                            "
                        >

                            <div>


                                <h3 className="text-2xl font-bold text-gray-900">

                                    {result.candidate_name}

                                </h3>


                                <p className="mt-1 text-sm text-gray-500">

                                    Candidate ID #{result.candidate_id}

                                </p>


                            </div>

                            <div
                                className="
                                    rounded-xl
                                    bg-green-100
                                    px-5
                                    py-3
                                    text-xl
                                    font-bold
                                    text-green-700
                                "
                            >

                                {result.match_score}%

                            </div>


                        </div>

                        {/* Match Score */}

                        <div className="mt-6">


                            <div
                                className="
                                    mb-2
                                    flex
                                    justify-between
                                    text-sm
                                    font-medium
                                "
                            >

                                <span>
                                    Match Score
                                </span>


                                <span>
                                    {result.match_score}/100
                                </span>


                            </div>

                            <div
                                className="
                                    h-3
                                    overflow-hidden
                                    rounded-full
                                    bg-gray-200
                                "
                            >

                                <div

                                    className="
                                        h-full
                                        rounded-full
                                        bg-green-500
                                        transition-all
                                    "


                                    style={{
                                        width:
                                            `${result.match_score}%`,
                                    }}

                                />


                            </div>


                        </div>

                        {/* Strengths */}

                        <div className="mt-6">


                            <h4 className="font-semibold">

                                Strengths

                            </h4>

                            <ul className="mt-3 space-y-2">

                                {
                                    (result.strengths ?? [])
                                        .map(
                                            (item) => (

                                                <li
                                                    key={item}
                                                    className="
                                                    rounded-lg
                                                    bg-green-50
                                                    px-3
                                                    py-2
                                                    text-sm
                                                    text-green-700
                                                "
                                                >

                                                    ✓ {item}

                                                </li>

                                            )
                                        )
                                }


                            </ul>


                        </div>

                        {/* Experience */}

                        <div className="mt-6">


                            <h4 className="font-semibold">

                                Relevant Experience

                            </h4>

                            <ul className="mt-3 space-y-2">

                                {
                                    (
                                        result.relevant_experience
                                        ?? []
                                    )
                                        .map(
                                            (item) => (

                                                <li

                                                    key={item}

                                                    className="
                                                    rounded-lg
                                                    bg-blue-50
                                                    px-3
                                                    py-2
                                                    text-sm
                                                    text-blue-700
                                                "

                                                >

                                                    • {item}

                                                </li>

                                            )
                                        )
                                }


                            </ul>

                        </div>

                        {/* Reason */}

                        <div className="mt-6">


                            <h4 className="font-semibold">

                                AI Reason

                            </h4>


                            <p
                                className="
                                    mt-2
                                    leading-7
                                    text-gray-700
                                "
                            >

                                {result.reason}

                            </p>


                        </div>



                    </div>

                )
            }

        </AppLayout>

    );

}