import AppLayout from "@/components/layout/AppLayout";
import CandidateTable from "@/components/candidates/CandidateTable";

import { getCandidates } from "@/services/candidate";

export const dynamic = "force-dynamic";


export default async function CandidatesPage() {


    const candidates = await getCandidates();



    return (

        <AppLayout
            title="Candidates"
            description="Manage and review all candidates in the ATS"
        >


            <div
                className="
                    mb-6
                    flex
                    flex-col
                    gap-4
                    md:flex-row
                    md:items-center
                    md:justify-between
                "
            >

                <div>

                    <h3 className="text-xl font-semibold text-slate-900">
                        Candidate List
                    </h3>


                    <p className="mt-1 text-sm text-gray-500">

                        Total Candidates :{" "}

                        <span className="font-semibold text-blue-600">
                            {candidates.length}
                        </span>

                    </p>


                </div>


            </div>



            {
                candidates.length === 0 ? (

                    <div
                        className="
                            rounded-xl
                            border
                            border-dashed
                            bg-white
                            p-16
                            text-center
                            shadow-sm
                        "
                    >

                        <h3 className="text-xl font-semibold">
                            No Candidates Found
                        </h3>


                        <p className="mt-2 text-gray-500">
                            Upload a resume to start building your ATS database.
                        </p>


                    </div>


                ) : (

                    <CandidateTable
                        candidates={candidates}
                    />

                )
            }



        </AppLayout>

    );

}