"use client";

import {
    useEffect,
    useState,
} from "react";
import Link from "next/link";

import {
    Plus,
    Users,
} from "lucide-react";

import AppLayout from "@/components/layout/AppLayout";
import CandidateTable from "@/components/candidates/CandidateTable";

import {
    Candidate,
    getCandidates,
} from "@/services/candidate";


export default function CandidatesPage() {

    const [candidates, setCandidates] = (
        useState<Candidate[]>([])
    );

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");


    useEffect(() => {

        let active = true;

        getCandidates(0, 50)
            .then((result) => {

                if (active) {
                    setCandidates(result);
                }

            })
            .catch((loadError: unknown) => {

                if (active) {
                    setError(
                        loadError instanceof Error
                            ? loadError.message
                            : "Could not load candidates."
                    );
                }

            })
            .finally(() => {

                if (active) {
                    setLoading(false);
                }

            });

        return () => {
            active = false;
        };

    }, []);


    function handleCandidateDeleted(
        candidateId: number
    ) {

        setCandidates((current) => (
            current.filter(
                (candidate) => (
                    candidate.id !== candidateId
                )
            )
        ));

    }


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


            {loading ? (

                <div className="mt-6 rounded-xl border border-gray-200 bg-white p-8 text-sm text-gray-500 shadow-sm">
                    Loading candidates...
                </div>

            ) : error ? (

                <div
                    role="alert"
                    className="mt-6 rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-700"
                >
                    {error}
                </div>

            ) : (

                <CandidateTable
                    candidates={candidates}
                    onCandidateDeleted={
                        handleCandidateDeleted
                    }
                />

            )}

        </AppLayout>

    );

}
