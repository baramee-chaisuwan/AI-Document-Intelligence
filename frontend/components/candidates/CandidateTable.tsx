import Link from "next/link";

type Candidate = {
    id: number;
    name: string;
    candidate_level: string;
    skill_score: number;
    ai_status: string;
};

type CandidateTableProps = {
    candidates: Candidate[];
};

export default function CandidateTable({
    candidates,
}: CandidateTableProps) {
    return (
        <div className="mt-6 overflow-hidden rounded-lg bg-white shadow">
            <table className="min-w-full">
                <thead className="bg-slate-100">
                    <tr>
                        <th className="px-6 py-3 text-left text-sm font-semibold">
                            Candidate
                        </th>

                        <th className="px-6 py-3 text-left text-sm font-semibold">
                            Level
                        </th>

                        <th className="px-6 py-3 text-left text-sm font-semibold">
                            Skill Score
                        </th>

                        <th className="px-6 py-3 text-left text-sm font-semibold">
                            AI Status
                        </th>

                        <th className="px-6 py-3 text-left text-sm font-semibold">
                            Action
                        </th>
                    </tr>
                </thead>

                <tbody>
                    {candidates.map((candidate) => (
                        <tr
                            key={candidate.id}
                            className="border-t hover:bg-slate-50"
                        >
                            <td className="px-6 py-4">
                                {candidate.name}
                            </td>

                            <td className="px-6 py-4">
                                {candidate.candidate_level}
                            </td>

                            <td className="px-6 py-4 font-semibold">
                                {candidate.skill_score}
                            </td>

                            <td className="px-6 py-4">
                                {candidate.ai_status}
                            </td>

                            <td className="px-6 py-4">
                                <Link
                                    href={`/candidates/${candidate.id}`}
                                    className="text-blue-600 hover:underline"
                                >
                                    View
                                </Link>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}