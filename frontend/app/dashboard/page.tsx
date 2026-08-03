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


export default async function DashboardPage() {

    const results = await Promise.allSettled([
        getDashboardSummary(),
        getLevelDistribution(),
        getScoreDistribution(),
        getTopCandidates(),
        getRecentCandidates(),
    ]);


    const summary = (
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
    );


    const levelDistribution = (
        results[1].status === "fulfilled"
            ? results[1].value
            : []
    );


    const scoreDistribution = (
        results[2].status === "fulfilled"
            ? results[2].value
            : []
    );


    const topCandidates = (
        results[3].status === "fulfilled"
            ? results[3].value
            : []
    );


    const recentCandidates = (
        results[4].status === "fulfilled"
            ? results[4].value
            : []
    );


    const hasDashboardError = results.some(
        (result) => result.status === "rejected"
    );


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