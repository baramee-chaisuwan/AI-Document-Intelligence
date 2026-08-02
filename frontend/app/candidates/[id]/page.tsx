import AppLayout from "@/components/layout/AppLayout";
import ScoreBreakdown from "@/components/candidates/ScoreBreakdown";
import { getCandidateById } from "@/services/candidate";

export const dynamic = "force-dynamic";

type Props = {
    params: Promise<{
        id: string;
    }>;
};

export default async function CandidateDetailPage({
    params,
}: Props) {

    const { id } = await params;

    const candidate = await getCandidateById(
        Number(id)
    );

    return (
        <AppLayout
            title="Candidate Detail"
            description="View candidate information"
        >
            <div className="mt-6 rounded-lg bg-white p-6 shadow">

                <h3 className="text-2xl font-bold">
                    {candidate.name}
                </h3>

                <div className="mt-4 grid gap-4 md:grid-cols-2">

                    <div>
                        <p className="text-gray-500">
                            Level
                        </p>

                        <p className="font-semibold">
                            {candidate.candidate_level}
                        </p>
                    </div>

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

                </div>

                <div className="mt-6">

                    <p className="text-gray-500">
                        AI Status
                    </p>

                    <p className="font-semibold">
                        {candidate.ai_status}
                    </p>

                </div>

                <div className="mt-6">

                    <p className="text-gray-500">
                        Summary
                    </p>

                    <p className="mt-2 text-gray-700">
                        {candidate.summary}
                    </p>

                </div>

            </div>

            <ScoreBreakdown
                breakdown={
                    candidate.score_breakdown
                }
            />

        </AppLayout>
    );
}