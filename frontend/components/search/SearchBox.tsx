"use client";

import { useState } from "react";
import { searchCandidates } from "@/services/search";
import Link from "next/link";

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

export default function SearchBox() {

    const [query, setQuery] = useState("");
    const [results, setResults] = useState<SearchResult[]>([]);
    const [loading, setLoading] = useState(false);

    async function handleSearch() {

        if (!query.trim()) {
            return;
        }

        try {

            setLoading(true);

            const data = await searchCandidates(
                query
            );

            setResults(
                (data.results ?? [])
                    .filter(
                        (candidate: SearchResult) =>
                            candidate.name
                    )
            );

        } catch (error) {

            console.error(error);
            setResults([]);

        } finally {

            setLoading(false);

        }
    }

    return (
        <div className="mt-6 rounded-lg bg-white p-6 shadow">

            <h2 className="text-xl font-bold">
                AI Candidate Search
            </h2>

            <div className="mt-4 flex gap-3">

                <input
                    value={query}
                    onChange={(e) =>
                        setQuery(e.target.value)
                    }
                    placeholder="Search candidate skills..."
                    className="flex-1 rounded-lg border px-4 py-2"
                    onKeyDown={(e) => {
                        if (e.key === "Enter") {
                            handleSearch();
                        }
                    }}
                />

                <button
                    onClick={handleSearch}
                    disabled={loading}
                    className="rounded-lg bg-blue-600 px-5 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
                >
                    {
                        loading
                            ? "Searching..."
                            : "Search"
                    }
                </button>

            </div>

            <div className="mt-6 space-y-4">


                {
                    !loading &&
                    results.length === 0 &&
                    query &&
                    (
                        <p className="text-gray-500">
                            No matching candidates found.
                        </p>
                    )
                }


                {results.map((candidate) => (

                    <div
                        key={candidate.id}
                        className="rounded-lg border p-5 hover:bg-slate-50"
                    >

                        <div className="flex justify-between">

                            <h3 className="text-lg font-bold">
                                {candidate.name}
                            </h3>


                            <span className="rounded bg-blue-100 px-3 py-1 text-sm">
                                {candidate.candidate_level}
                            </span>

                        </div>


                        <div className="mt-4 grid grid-cols-4 gap-4 text-sm">


                            <div>
                                <p className="text-gray-500">
                                    Skill Score
                                </p>

                                <p className="font-semibold">
                                    {candidate.skill_score}
                                </p>
                            </div>


                            <div>
                                <p className="text-gray-500">
                                    Rule Score
                                </p>

                                <p className="font-semibold">
                                    {candidate.rule_score}
                                </p>
                            </div>


                            <div>
                                <p className="text-gray-500">
                                    AI Score
                                </p>

                                <p className="font-semibold">
                                    {candidate.ai_score}
                                </p>
                            </div>


                            <div>
                                <p className="text-gray-500">
                                    Semantic Distance
                                </p>

                                <p className="font-semibold">
                                    {candidate.distance.toFixed(2)}
                                </p>
                            </div>


                        </div>


                        <p className="mt-4 line-clamp-3 text-sm text-gray-600">
                            {candidate.summary}
                        </p>


                        <div className="mt-4">

                            <Link
                                href={`/candidates/${candidate.id}`}
                                className="text-blue-600 hover:underline"
                            >
                                View Candidate →
                            </Link>

                        </div>

                    </div>

                ))}

            </div>

        </div>
    );
}