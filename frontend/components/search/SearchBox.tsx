"use client";

import { useState } from "react";
import Link from "next/link";

import { searchCandidates } from "@/services/search";

type SearchResult = {
    id: number;
    name: string;
    summary: string;
    candidate_level: string;
    skill_score: number;
    rule_score: number;
    ai_score: number;
    distance: number;
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

export default function SearchBox() {

    const [query, setQuery] = useState("");

    const [results, setResults] = useState<SearchResult[]>([]);

    const [loading, setLoading] = useState(false);

    async function handleSearch() {

        if (!query.trim())
            return;

        try {

            setLoading(true);

            const data = await searchCandidates(query);

            setResults(
                (data.results ?? []).filter(
                    (candidate: SearchResult) =>
                        candidate.name
                )
            );

        }

        catch (error) {

            console.error(error);

            setResults([]);

        }

        finally {

            setLoading(false);

        }

    }

    return (

        <div className="mt-8">

            <div className="rounded-xl border bg-white p-8 shadow-sm">

                <h2 className="text-2xl font-bold">
                    AI Candidate Search
                </h2>

                <p className="mt-2 text-gray-500">
                    Search candidates by skills, technologies or job requirements.
                </p>

                <div className="mt-6 flex gap-3">

                    <input
                        value={query}
                        onChange={(e) =>
                            setQuery(e.target.value)
                        }
                        onKeyDown={(e) => {

                            if (e.key === "Enter")
                                handleSearch();

                        }}
                        placeholder="Example: Python, Machine Learning, FastAPI..."
                        className="flex-1 rounded-xl border border-gray-300 px-5 py-3 outline-none focus:border-blue-500"
                    />

                    <button
                        onClick={handleSearch}
                        disabled={loading}
                        className="rounded-xl bg-blue-600 px-8 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:opacity-50"
                    >
                        {
                            loading
                                ? "Searching..."
                                : "Search"
                        }
                    </button>

                </div>

            </div>

            {
                !loading &&
                results.length === 0 &&
                query &&
                (
                    <div className="mt-6 rounded-xl border bg-white p-8 text-center shadow-sm">

                        <p className="text-gray-500">
                            No matching candidates found.
                        </p>

                    </div>
                )
            }

            <div className="mt-6 space-y-5">

                {results.map((candidate) => (

                    <div
                        key={candidate.id}
                        className="rounded-xl border bg-white p-6 shadow-sm transition hover:shadow-md"
                    >

                        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">

                            <div>

                                <h3 className="text-2xl font-bold">

                                    {candidate.name}

                                </h3>

                                <div className="mt-3 flex gap-2">

                                    <span
                                        className={`rounded-full px-3 py-1 text-sm font-semibold ${levelColor(candidate.candidate_level)}`}
                                    >
                                        {candidate.candidate_level}
                                    </span>

                                    <span
                                        className={`rounded-full px-3 py-1 text-sm font-semibold ${scoreColor(candidate.ai_score)}`}
                                    >
                                        AI Score {candidate.ai_score}
                                    </span>

                                </div>

                            </div>

                            <div className="text-right">

                                <p className="text-sm text-gray-500">
                                    Semantic Distance
                                </p>

                                <p className="text-lg font-bold">

                                    {candidate.distance.toFixed(2)}

                                </p>

                            </div>

                        </div>

                        <div className="mt-6 grid gap-4 md:grid-cols-2">

                            <div className="rounded-lg bg-gray-50 p-4">

                                <p className="text-sm text-gray-500">
                                    Skill Score
                                </p>

                                <p className="mt-2 text-3xl font-bold">
                                    {candidate.skill_score}
                                </p>

                            </div>

                            <div className="rounded-lg bg-gray-50 p-4">

                                <p className="text-sm text-gray-500">
                                    Rule Score
                                </p>

                                <p className="mt-2 text-3xl font-bold">
                                    {candidate.rule_score}
                                </p>

                            </div>

                        </div>

                        <div className="mt-6">

                            <p className="text-sm font-semibold text-gray-500">
                                AI Summary
                            </p>

                            <p className="mt-2 whitespace-pre-line leading-7 text-gray-700">

                                {candidate.summary}

                            </p>

                        </div>

                        <div className="mt-6">

                            <Link
                                href={`/candidates/${candidate.id}`}
                                className="rounded-lg bg-blue-600 px-5 py-2 font-semibold text-white transition hover:bg-blue-700"
                            >
                                View Candidate
                            </Link>

                        </div>

                    </div>

                ))}

            </div>

        </div>

    );

}