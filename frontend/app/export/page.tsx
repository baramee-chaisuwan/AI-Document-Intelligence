"use client";

import AppLayout from "@/components/layout/AppLayout";
import { exportCandidatesCSV } from "@/services/export";
import { Download } from "lucide-react";


export default function ExportPage() {


    async function handleExport() {

        await exportCandidatesCSV();

    }


    return (

        <AppLayout

            title="Export"

            description="Export ATS candidate data"

        >

            <div
                className="
                    mt-8
                    rounded-xl
                    border
                    bg-white
                    p-8
                    shadow-sm
                "
            >

                <h2
                    className="
                        text-xl
                        font-semibold
                        text-gray-900
                    "
                >
                    Export Candidates
                </h2>


                <p
                    className="
                        mt-2
                        text-sm
                        text-gray-500
                    "
                >
                    Download candidate data as CSV file.
                </p>


                <button

                    onClick={handleExport}

                    className="
                        mt-6
                        inline-flex
                        items-center
                        gap-2
                        rounded-lg
                        bg-blue-600
                        px-5
                        py-3
                        font-medium
                        text-white
                        transition
                        hover:bg-blue-700
                    "

                >

                    <Download size={18} />

                    Export CSV


                </button>


            </div>


        </AppLayout>

    );

}