"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { deleteCandidate } from "@/services/candidate";


type Candidate = {
    id: number;
    name: string;
    candidate_level: string;
    ai_score: number;
    ai_status: string;
};


type CandidateTableProps = {
    candidates: Candidate[];
};



function levelBadge(level: string) {

    switch (level) {

        case "Senior":
            return "bg-purple-100 text-purple-700";

        case "Mid-Level":
            return "bg-blue-100 text-blue-700";

        case "Junior":
            return "bg-green-100 text-green-700";

        default:
            return "bg-yellow-100 text-yellow-700";

    }

}



function scoreBadge(score: number) {

    if (score >= 80)
        return "bg-green-100 text-green-700";

    if (score >= 60)
        return "bg-blue-100 text-blue-700";

    if (score >= 40)
        return "bg-yellow-100 text-yellow-700";

    return "bg-red-100 text-red-700";

}



function statusBadge(status?: string) {

    switch (status?.toLowerCase()) {

        case "completed":
            return "bg-green-100 text-green-700";

        case "processing":
            return "bg-yellow-100 text-yellow-700";

        case "failed":
            return "bg-red-100 text-red-700";

        default:
            return "bg-gray-100 text-gray-700";

    }

}



export default function CandidateTable({
    candidates,
}: CandidateTableProps) {


    const router = useRouter();

    const [deletingId, setDeletingId] = useState<number | null>(null);



    async function handleDelete(id: number) {


        const confirmDelete = window.confirm(
            "Are you sure you want to delete this candidate?"
        );


        if (!confirmDelete)
            return;



        try {

            setDeletingId(id);


            await deleteCandidate(id);


            router.refresh();


        } catch (error) {

            console.error(error);

            alert(
                "Failed to delete candidate"
            );


        } finally {

            setDeletingId(null);

        }

    }



    if (!candidates || candidates.length === 0) {

        return (

            <div
                className="
                    mt-6
                    rounded-xl
                    border
                    bg-white
                    p-10
                    text-center
                    shadow-sm
                "
            >

                <h3 className="text-lg font-semibold text-gray-800">
                    No Candidates Found
                </h3>

                <p className="mt-2 text-sm text-gray-500">
                    Upload resumes to start AI candidate evaluation.
                </p>

            </div>

        );

    }



    return (

        <div
            className="
                mt-6
                overflow-hidden
                rounded-xl
                border
                bg-white
                shadow-sm
            "
        >

            <div className="overflow-x-auto">

                <table className="min-w-full">


                    <thead className="bg-gray-50">

                        <tr>

                            <th className="px-6 py-4 text-left text-sm font-semibold">
                                Candidate
                            </th>

                            <th className="px-6 py-4 text-left text-sm font-semibold">
                                Level
                            </th>

                            <th className="px-6 py-4 text-left text-sm font-semibold">
                                AI Score
                            </th>

                            <th className="px-6 py-4 text-left text-sm font-semibold">
                                Status
                            </th>

                            <th className="px-6 py-4 text-center text-sm font-semibold">
                                Action
                            </th>

                        </tr>

                    </thead>


                    <tbody>

                        {candidates.map((candidate) => (

                            <tr
                                key={candidate.id}
                                className="border-t hover:bg-gray-50"
                            >

                                <td className="px-6 py-4">

                                    <p className="font-medium">
                                        {candidate.name}
                                    </p>

                                    <p className="text-xs text-gray-500">
                                        ID #{candidate.id}
                                    </p>

                                </td>


                                <td className="px-6 py-4">

                                    <span
                                        className={`rounded-full px-3 py-1 text-sm font-semibold ${levelBadge(candidate.candidate_level)}`}
                                    >
                                        {candidate.candidate_level}
                                    </span>

                                </td>


                                <td className="px-6 py-4">

                                    <span
                                        className={`rounded-full px-3 py-1 text-sm font-bold ${scoreBadge(candidate.ai_score)}`}
                                    >
                                        {candidate.ai_score}
                                    </span>

                                </td>


                                <td className="px-6 py-4">

                                    <span
                                        className={`rounded-full px-3 py-1 text-sm ${statusBadge(candidate.ai_status)}`}
                                    >
                                        {candidate.ai_status}
                                    </span>

                                </td>


                                <td className="px-6 py-4">

                                    <div className="flex justify-center gap-2">


                                        <Link
                                            href={`/candidates/${candidate.id}`}
                                            className="
                                                rounded-lg
                                                bg-blue-600
                                                px-4
                                                py-2
                                                text-sm
                                                text-white
                                                hover:bg-blue-700
                                            "
                                        >
                                            View
                                        </Link>



                                        <button

                                            onClick={() =>
                                                handleDelete(candidate.id)
                                            }

                                            disabled={
                                                deletingId === candidate.id
                                            }

                                            className="
                                                rounded-lg
                                                bg-red-600
                                                px-4
                                                py-2
                                                text-sm
                                                text-white
                                                hover:bg-red-700
                                                disabled:opacity-50
                                            "

                                        >

                                            {
                                                deletingId === candidate.id
                                                    ? "Deleting..."
                                                    : "Delete"
                                            }

                                        </button>


                                    </div>

                                </td>


                            </tr>

                        ))}

                    </tbody>


                </table>

            </div>

        </div>

    );

}