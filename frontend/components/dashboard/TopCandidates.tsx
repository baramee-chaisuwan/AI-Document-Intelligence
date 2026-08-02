import Link from "next/link";

import {
    Trophy,
    Eye,
} from "lucide-react";


type Candidate = {
    id: number;
    name: string;
    ai_score: number;
};


type Props = {
    candidates: Candidate[];
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



function rankBadge(rank: number) {

    if (rank === 1)
        return "🥇";

    if (rank === 2)
        return "🥈";

    if (rank === 3)
        return "🥉";

    return `#${rank}`;

}



export default function TopCandidates({
    candidates,
}: Props) {


    return (

        <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">


            <div className="mb-5 flex items-center gap-2">

                <Trophy
                    size={22}
                    className="text-yellow-500"
                />

                <h3 className="text-lg font-semibold">
                    Top Candidates
                </h3>

            </div>



            <div className="overflow-x-auto">


                <table className="w-full">


                    <thead>

                        <tr className="border-b text-left text-sm text-gray-500">


                            <th className="pb-3">
                                Rank
                            </th>


                            <th className="pb-3">
                                Candidate
                            </th>


                            <th className="pb-3">
                                AI Score
                            </th>


                            <th className="pb-3 text-right">
                                Action
                            </th>


                        </tr>

                    </thead>



                    <tbody>


                        {candidates.map(
                            (candidate, index) => (

                                <tr
                                    key={candidate.id}
                                    className="
                                    border-b
                                    transition
                                    hover:bg-gray-50
                                "
                                >


                                    <td className="py-4 text-lg font-semibold">

                                        {rankBadge(index + 1)}

                                    </td>



                                    <td className="py-4 font-medium">

                                        {candidate.name}

                                    </td>



                                    <td className="py-4">

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

                                            {candidate.ai_score}

                                        </span>


                                    </td>



                                    <td className="py-4 text-right">


                                        <Link

                                            href={`/candidates/${candidate.id}`}

                                            className="
                                            inline-flex
                                            items-center
                                            gap-1
                                            rounded-lg
                                            border
                                            px-3
                                            py-1
                                            text-sm
                                            font-medium
                                            text-blue-600
                                            transition
                                            hover:bg-blue-50
                                        "

                                        >

                                            <Eye size={16} />

                                            View

                                        </Link>


                                    </td>


                                </tr>

                            ))}


                    </tbody>


                </table>


            </div>


        </div>

    );

}