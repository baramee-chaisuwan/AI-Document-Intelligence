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

    const [
        summary,
        levelDistribution,
        scoreDistribution,
        topCandidates,
        recentCandidates,
    ] = await Promise.all([

        getDashboardSummary(),

        getLevelDistribution(),

        getScoreDistribution(),

        getTopCandidates(),

        getRecentCandidates(),

    ]);

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
            value: summary.top_candidate,
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

                {dashboardStats.map((stat) => (

                    <Card

                        key={stat.title}

                        title={stat.title}

                        value={stat.value}

                    />

                ))}

            </div>

            <RecentCandidates

                candidates={recentCandidates}

            />

            <TopCandidates

                candidates={topCandidates}

            />

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