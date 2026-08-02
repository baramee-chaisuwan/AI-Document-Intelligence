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


export default async function AnalyticsPage() {


    const [
        summary,
        levelDistribution,
        scoreDistribution,
        topCandidates,
    ] = await Promise.all([

        getDashboardSummary(),

        getLevelDistribution(),

        getScoreDistribution(),

        getTopCandidates(),

    ]);


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
                    value={summary.top_candidate}
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