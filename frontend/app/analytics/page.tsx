"use client";

import {
    useEffect,
    useState,
} from "react";

import AppLayout from "@/components/layout/AppLayout";

import Card from "@/components/ui/Card";

import LevelChart from "@/components/dashboard/LevelChart";
import ScoreChart from "@/components/dashboard/ScoreChart";
import TopCandidates from "@/components/dashboard/TopCandidates";

import {
    getDashboardSummary,
    getLevelDistribution,
    getScoreDistribution,
    getTopCandidates,
} from "@/services/dashboard";


type AnalyticsData = {
    summary: Awaited<ReturnType<
        typeof getDashboardSummary
    >>;
    levelDistribution: Awaited<ReturnType<
        typeof getLevelDistribution
    >>;
    scoreDistribution: Awaited<ReturnType<
        typeof getScoreDistribution
    >>;
    topCandidates: Awaited<ReturnType<
        typeof getTopCandidates
    >>;
};


export default function AnalyticsPage() {

    const [data, setData] = (
        useState<AnalyticsData | null>(null)
    );

    const [error, setError] = useState("");


    useEffect(() => {

        let active = true;

        Promise.all([
            getDashboardSummary(),
            getLevelDistribution(),
            getScoreDistribution(),
            getTopCandidates(),
        ])
            .then(([
                summary,
                levelDistribution,
                scoreDistribution,
                topCandidates,
            ]) => {

                if (active) {
                    setData({
                        summary,
                        levelDistribution,
                        scoreDistribution,
                        topCandidates,
                    });
                }

            })
            .catch((loadError: unknown) => {

                if (active) {
                    setError(
                        loadError instanceof Error
                            ? loadError.message
                            : "Could not load analytics."
                    );
                }

            });

        return () => {
            active = false;
        };

    }, []);


    if (!data) {

        return (
            <AppLayout
                title="Analytics"
                description="AI recruitment insights and candidate performance analysis"
            >
                <div
                    className={`mt-8 rounded-xl border bg-white p-8 text-sm shadow-sm ${error ? "border-red-200 text-red-700" : "border-gray-200 text-gray-500"}`}
                    role={error ? "alert" : "status"}
                >
                    {error || "Loading analytics..."}
                </div>
            </AppLayout>
        );

    }

    const {
        summary,
        levelDistribution,
        scoreDistribution,
        topCandidates,
    } = data;


    return (

        <AppLayout
            title="Analytics"
            description="AI recruitment insights and candidate performance analysis"
        >

            <div
                className="
                    mt-8
                    grid
                    grid-cols-1
                    gap-6
                    md:grid-cols-2
                    xl:grid-cols-4
                "
            >

                <Card
                    title="Total Candidates"
                    value={summary.total_candidates}
                />

                <Card
                    title="Average AI Score"
                    value={summary.average_score}
                />

                <Card
                    title="Highest AI Score"
                    value={summary.top_score}
                />

                <Card
                    title="Top Candidate"
                    value={
                        summary.top_candidate
                        ?? "No candidates"
                    }
                />

            </div>


            <div
                className="
                    mt-8
                    grid
                    grid-cols-1
                    gap-6
                    xl:grid-cols-2
                "
            >

                <LevelChart
                    data={levelDistribution ?? []}
                />

                <ScoreChart
                    data={scoreDistribution ?? []}
                />

            </div>


            <div className="mt-8">

                <TopCandidates
                    candidates={topCandidates ?? []}
                />

            </div>

        </AppLayout>

    );

}
