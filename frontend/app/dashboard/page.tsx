"use client";

import {
    useEffect,
    useState,
} from "react";

import AppLayout from "@/components/layout/AppLayout";
import Card from "@/components/ui/Card";

import RecentCandidates from "@/components/dashboard/RecentCandidates";
import TopCandidates from "@/components/dashboard/TopCandidates";
import LevelChart from "@/components/dashboard/LevelChart";
import ScoreChart from "@/components/dashboard/ScoreChart";

import {
    getDashboardSummary,
    getLevelDistribution,
    getScoreDistribution,
    getTopCandidates,
    getRecentCandidates,
} from "@/services/dashboard";


type DashboardData = {
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
    recentCandidates: Awaited<ReturnType<
        typeof getRecentCandidates
    >>;
    hasDashboardError: boolean;
};


export default function DashboardPage() {

    const [data, setData] = (
        useState<DashboardData | null>(null)
    );


    useEffect(() => {

        let active = true;

        async function loadDashboard() {

            const results = await Promise.allSettled([
                getDashboardSummary(),
                getLevelDistribution(),
                getScoreDistribution(),
                getTopCandidates(),
                getRecentCandidates(),
            ]);

            if (!active) {
                return;
            }

            setData({
                summary: (
                    results[0].status === "fulfilled"
                        ? results[0].value
                        : {
                            total_candidates: 0,
                            average_score: 0,
                            top_candidate: null,
                            top_score: 0,
                            junior_count: 0,
                            mid_count: 0,
                            senior_count: 0,
                        }
                ),
                levelDistribution: (
                    results[1].status === "fulfilled"
                        ? results[1].value
                        : []
                ),
                scoreDistribution: (
                    results[2].status === "fulfilled"
                        ? results[2].value
                        : []
                ),
                topCandidates: (
                    results[3].status === "fulfilled"
                        ? results[3].value
                        : []
                ),
                recentCandidates: (
                    results[4].status === "fulfilled"
                        ? results[4].value
                        : []
                ),
                hasDashboardError: results.some(
                    (result) => (
                        result.status === "rejected"
                    )
                ),
            });

        }

        void loadDashboard();

        return () => {
            active = false;
        };

    }, []);


    if (!data) {

        return (
            <AppLayout
                title="Dashboard"
                description="Welcome to AI Document Intelligence ATS"
            >
                <div className="mt-8 rounded-xl border border-gray-200 bg-white p-8 text-sm text-gray-500 shadow-sm">
                    Loading dashboard...
                </div>
            </AppLayout>
        );

    }

    const {
        summary,
        levelDistribution,
        scoreDistribution,
        topCandidates,
        recentCandidates,
        hasDashboardError,
    } = data;


    const dashboardStats = [
        {
            title: "Total Candidates",
            value: summary.total_candidates,
        },
        {
            title: "Average AI Score",
            value: summary.average_score,
        },
        {
            title: "Top Candidate",
            value: (
                summary.top_candidate
                ?? "No candidates"
            ),
        },
        {
            title: "Top AI Score",
            value: summary.top_score,
        },
    ];


    return (

        <AppLayout
            title="Dashboard"
            description="Welcome to AI Document Intelligence ATS"
        >

            {hasDashboardError && (

                <div
                    role="alert"
                    className="
                        mt-8
                        rounded-xl
                        border
                        border-amber-200
                        bg-amber-50
                        px-5
                        py-4
                        text-sm
                        text-amber-800
                    "
                >
                    Some dashboard information could not be loaded.
                    The available data is still shown below.
                </div>

            )}


            <div
                className="
                    mt-8
                    grid
                    grid-cols-1
                    gap-6
                    sm:grid-cols-2
                    xl:grid-cols-4
                "
            >

                {dashboardStats.map((stat) => (

                    <Card
                        key={stat.title}
                        title={stat.title}
                        value={stat.value}
                    />

                ))}

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

                <RecentCandidates
                    candidates={recentCandidates}
                />

                <TopCandidates
                    candidates={topCandidates}
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
                    data={levelDistribution}
                />

                <ScoreChart
                    data={scoreDistribution}
                />

            </div>

        </AppLayout>

    );

}
