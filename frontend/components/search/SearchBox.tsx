"use client";

import Link from "next/link";

import {
    FormEvent,
    useState,
} from "react";

import {
    ExternalLink,
    Loader2,
    Search,
    SearchX,
    Sparkles,
} from "lucide-react";

import {
    searchCandidates,
} from "@/services/search";

import type {
    SearchResult,
} from "@/services/search";
import { scoreLabels } from "@/lib/score-labels";


const MAX_QUERY_LENGTH = 500;


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


function normalizeDistance(
    distance: unknown
) {

    const numericDistance = Number(
        distance
    );


    if (!Number.isFinite(
        numericDistance
    )) {

        return null;

    }


    return numericDistance;

}


export default function SearchBox() {

    const [
        query,
        setQuery,
    ] = useState("");

    const [
        searchedQuery,
        setSearchedQuery,
    ] = useState("");

    const [
        results,
        setResults,
    ] = useState<SearchResult[]>([]);

    const [
        loading,
        setLoading,
    ] = useState(false);

    const [
        error,
        setError,
    ] = useState("");

    const [
        hasSearched,
        setHasSearched,
    ] = useState(false);


    const normalizedQuery = (
        query.trim()
    );


    const canSearch = (
        normalizedQuery.length > 0
        && normalizedQuery.length
        <= MAX_QUERY_LENGTH
        && !loading
    );


    async function handleSearch() {

        if (!normalizedQuery) {

            setError(
                "Please enter a search query."
            );

            return;

        }


        if (
            normalizedQuery.length
            > MAX_QUERY_LENGTH
        ) {

            setError(
                `Search query must not exceed `
                + `${MAX_QUERY_LENGTH} characters.`
            );

            return;

        }


        try {

            setLoading(true);
            setError("");
            setHasSearched(true);
            setSearchedQuery(
                normalizedQuery
            );
            setResults([]);


            const data = await searchCandidates(
                normalizedQuery
            );


            const validResults = (
                data.results ?? []
            ).filter(
                (candidate) => (
                    candidate
                    && candidate.id
                    && candidate.name?.trim()
                )
            );


            setResults(
                validResults
            );

        } catch (error) {

            setResults([]);

            setError(
                error instanceof Error
                    ? error.message
                    : "Candidate search failed."
            );

        } finally {

            setLoading(false);

        }

    }


    function handleSubmit(
        event: FormEvent<HTMLFormElement>
    ) {

        event.preventDefault();

        handleSearch();

    }


    return (

        <div className="mt-8">

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
                        <Sparkles
                            size={24}
                            className="text-blue-600"
                        />
                    </div>


                    <div>

                        <h2
                            className="
                                text-2xl
                                font-bold
                                text-gray-900
                            "
                        >
                            AI Candidate Search
                        </h2>

                        <p
                            className="
                                mt-2
                                max-w-2xl
                                text-sm
                                leading-6
                                text-gray-500
                            "
                        >
                            Search candidates by competencies,
                            experience, achievements, certifications, or
                            complete job requirements across domains.
                        </p>

                    </div>

                </div>


                <form
                    onSubmit={
                        handleSubmit
                    }
                    className="
                        mt-7
                        flex
                        flex-col
                        gap-3
                        sm:flex-row
                    "
                >

                    <div className="min-w-0 flex-1">

                        <label
                            htmlFor="candidate-search"
                            className="sr-only"
                        >
                            Candidate search query
                        </label>


                        <input
                            id="candidate-search"
                            value={query}
                            maxLength={
                                MAX_QUERY_LENGTH
                            }
                            disabled={loading}
                            onChange={(event) => {

                                setQuery(
                                    event.target.value
                                );

                                setError("");

                            }}
                            placeholder={
                                "Example: stakeholder management, CCNP, "
                                + "GAAP, campaign strategy, or Python"
                            }
                            className="
                                w-full
                                rounded-xl
                                border
                                border-gray-300
                                px-5
                                py-3
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
                                mt-1
                                flex
                                justify-end
                                text-xs
                                text-gray-400
                            "
                        >
                            {query.length}/{MAX_QUERY_LENGTH}
                        </div>

                    </div>


                    <button
                        type="submit"
                        disabled={
                            !canSearch
                        }
                        className="
                            inline-flex
                            items-center
                            justify-center
                            gap-2
                            rounded-xl
                            bg-blue-600
                            px-7
                            py-3
                            font-semibold
                            text-white
                            transition-colors
                            hover:bg-blue-700
                            disabled:cursor-not-allowed
                            disabled:opacity-50
                        "
                    >

                        {loading ? (

                            <>
                                <Loader2
                                    size={19}
                                    className="animate-spin"
                                />

                                Searching...
                            </>

                        ) : (

                            <>
                                <Search size={19} />
                                Search
                            </>

                        )}

                    </button>

                </form>

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


            {!loading
                && hasSearched
                && !error
                && results.length === 0
                && (

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

                        <SearchX
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
                            No Matching Candidates Found
                        </h3>

                        <p
                            className="
                                mt-2
                                text-sm
                                text-gray-500
                            "
                        >
                            No candidate matched “{searchedQuery}”.
                            Try fewer keywords or a broader requirement.
                        </p>

                    </section>

                )}


            {!loading
                && results.length > 0
                && (

                    <div className="mt-6">

                        <div className="mb-4">

                            <h3
                                className="
                                    text-lg
                                    font-semibold
                                    text-gray-900
                                "
                            >
                                Search Results
                            </h3>

                            <p
                                className="
                                    mt-1
                                    text-sm
                                    text-gray-500
                                "
                            >
                                Found {results.length} candidate
                                {results.length === 1 ? "" : "s"}
                                {" "}for “{searchedQuery}”
                            </p>

                        </div>


                        <div className="space-y-5">

                            {results.map((candidate) => {

                                const distance = (
                                    normalizeDistance(
                                        candidate.distance
                                    )
                                );
                                const labels = scoreLabels(
                                    candidate.score_breakdown
                                );


                                return (

                                    <article
                                        key={candidate.id}
                                        className="
                                            rounded-2xl
                                            border
                                            border-gray-200
                                            bg-white
                                            p-6
                                            shadow-sm
                                            transition-all
                                            hover:-translate-y-0.5
                                            hover:shadow-md
                                        "
                                    >

                                        <div
                                            className="
                                                flex
                                                flex-col
                                                justify-between
                                                gap-5
                                                md:flex-row
                                                md:items-start
                                            "
                                        >

                                            <div className="min-w-0">

                                                <h3
                                                    title={
                                                        candidate.name
                                                    }
                                                    className="
                                                        truncate
                                                        text-2xl
                                                        font-bold
                                                        text-gray-900
                                                    "
                                                >
                                                    {candidate.name}
                                                </h3>


                                                <div
                                                    className="
                                                        mt-3
                                                        flex
                                                        flex-wrap
                                                        gap-2
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
                                                        {
                                                            candidate
                                                                .candidate_level
                                                        }
                                                    </span>


                                                    <span
                                                        className={`
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
                                                        AI Analysis Score{" "}
                                                        {candidate.ai_score}
                                                    </span>

                                                </div>

                                            </div>


                                            <div
                                                className="
                                                    rounded-xl
                                                    bg-gray-50
                                                    px-4
                                                    py-3
                                                    text-left
                                                    md:text-right
                                                "
                                            >

                                                <p
                                                    className="
                                                        text-xs
                                                        font-medium
                                                        uppercase
                                                        tracking-wide
                                                        text-gray-500
                                                    "
                                                >
                                                    Vector Distance
                                                </p>

                                                <p
                                                    className="
                                                        mt-1
                                                        text-lg
                                                        font-bold
                                                        text-gray-900
                                                    "
                                                >
                                                    {
                                                        distance === null
                                                            ? "N/A"
                                                            : distance.toFixed(3)
                                                    }
                                                </p>

                                                <p
                                                    className="
                                                        mt-1
                                                        text-xs
                                                        text-gray-400
                                                    "
                                                >
                                                    Lower is more similar
                                                </p>

                                            </div>

                                        </div>


                                        <div
                                            className="
                                                mt-6
                                                grid
                                                gap-4
                                                sm:grid-cols-2
                                            "
                                        >

                                            <ScoreMetric
                                                title={labels.profile}
                                                value={
                                                    candidate.skill_score
                                                }
                                            />

                                            <ScoreMetric
                                                title={labels.rule}
                                                value={
                                                    candidate.rule_score
                                                }
                                            />

                                        </div>


                                        <div className="mt-6">

                                            <p
                                                className="
                                                    text-sm
                                                    font-semibold
                                                    text-gray-500
                                                "
                                            >
                                                AI Summary
                                            </p>

                                            <p
                                                className="
                                                    mt-2
                                                    whitespace-pre-line
                                                    leading-7
                                                    text-gray-700
                                                "
                                            >
                                                {
                                                    candidate.summary
                                                    || (
                                                        "No AI summary "
                                                        + "is available."
                                                    )
                                                }
                                            </p>

                                        </div>


                                        <div className="mt-6">

                                            <Link
                                                href={
                                                    `/candidates/${candidate.id}`
                                                }
                                                className="
                                                    inline-flex
                                                    items-center
                                                    gap-2
                                                    rounded-lg
                                                    bg-blue-600
                                                    px-5
                                                    py-2.5
                                                    text-sm
                                                    font-semibold
                                                    text-white
                                                    transition-colors
                                                    hover:bg-blue-700
                                                "
                                            >
                                                View Candidate
                                                <ExternalLink size={16} />
                                            </Link>

                                        </div>

                                    </article>

                                );

                            })}

                        </div>

                    </div>

                )}

        </div>

    );

}


function ScoreMetric({
    title,
    value,
}: {
    title: string;
    value: number;
}) {

    const numericValue = Number(
        value
    );

    const normalizedValue = (
        Number.isFinite(
            numericValue
        )
            ? Math.min(
                Math.max(
                    numericValue,
                    0
                ),
                100
            )
            : 0
    );


    return (

        <div
            className="
                rounded-xl
                border
                border-gray-100
                bg-gray-50
                p-4
            "
        >

            <p
                className="
                    text-sm
                    text-gray-500
                "
            >
                {title}
            </p>

            <div
                className="
                    mt-2
                    flex
                    items-end
                    gap-1
                "
            >

                <p
                    className="
                        text-3xl
                        font-bold
                        text-gray-900
                    "
                >
                    {normalizedValue}
                </p>

                <span
                    className="
                        pb-1
                        text-xs
                        text-gray-400
                    "
                >
                    /100
                </span>

            </div>

        </div>

    );

}
