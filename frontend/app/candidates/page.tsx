import Link from "next/link";

import {
    Plus,
    Users,
} from "lucide-react";

import AppLayout from "@/components/layout/AppLayout";
import CandidateTable from "@/components/candidates/CandidateTable";

import { getCandidates } from "@/services/candidate";


export const dynamic = "force-dynamic";


export default async function CandidatesPage() {

    const candidates = await getCandidates(
        0,
        50
    );


    return (

        <AppLayout
            title="Candidates"
            description="Manage and review candidates in the ATS"
        >

            <div
                className="
                    mb-6
                    flex
                    flex-col
                    gap-4
                    sm:flex-row
                    sm:items-center
                    sm:justify-between
                "
            >

                <div>

                    <div
                        className="
                            flex
                            items-center
                            gap-2
                        "
                    >

                        <Users
                            size={22}
                            className="text-blue-600"
                        />

                        <h3
                            className="
                                text-xl
                                font-semibold
                                text-slate-900
                            "
                        >
                            Candidate List
                        </h3>

                    </div>


                    <p
                        className="
                            mt-2
                            text-sm
                            text-gray-500
                        "
                    >
                        Showing{" "}

                        <span
                            className="
                                font-semibold
                                text-blue-600
                            "
                        >
                            {candidates.length}
                        </span>

                        {" "}candidate
                        {candidates.length === 1 ? "" : "s"}
                    </p>

                </div>


                <Link
                    href="/upload"
                    className="
                        inline-flex
                        items-center
                        justify-center
                        gap-2
                        rounded-lg
                        bg-blue-600
                        px-4
                        py-2.5
                        text-sm
                        font-medium
                        text-white
                        transition-colors
                        hover:bg-blue-700
                    "
                >
                    <Plus size={18} />
                    Upload Resume
                </Link>

            </div>


            <CandidateTable
                candidates={candidates}
            />

        </AppLayout>

    );

}