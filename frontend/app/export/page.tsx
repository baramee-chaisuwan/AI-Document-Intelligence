"use client";

import {
    useState,
} from "react";

import {
    CheckCircle2,
    Download,
    FileSpreadsheet,
    Loader2,
} from "lucide-react";

import AppLayout from "@/components/layout/AppLayout";

import {
    exportCandidatesCSV,
} from "@/services/export";


export default function ExportPage() {

    const [
        loading,
        setLoading,
    ] = useState(false);

    const [
        message,
        setMessage,
    ] = useState("");

    const [
        error,
        setError,
    ] = useState("");


    async function handleExport() {

        try {

            setLoading(true);
            setMessage("");
            setError("");


            await exportCandidatesCSV();


            setMessage(
                "Candidate CSV exported successfully."
            );

        } catch (error) {

            setError(
                error instanceof Error
                    ? error.message
                    : "Failed to export candidates."
            );

        } finally {

            setLoading(false);

        }

    }


    return (

        <AppLayout
            title="Export"
            description="Download ATS candidate data as a CSV report"
        >

            <section
                className="
                    mt-8
                    rounded-2xl
                    border
                    border-gray-200
                    bg-white
                    p-6
                    shadow-sm
                    sm:p-8
                "
            >

                <div
                    className="
                        flex
                        items-start
                        gap-4
                    "
                >

                    <div
                        className="
                            flex
                            h-12
                            w-12
                            shrink-0
                            items-center
                            justify-center
                            rounded-xl
                            bg-blue-50
                        "
                    >
                        <FileSpreadsheet
                            size={24}
                            className="text-blue-600"
                        />
                    </div>


                    <div>

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
                                mt-1
                                max-w-2xl
                                text-sm
                                leading-6
                                text-gray-500
                            "
                        >
                            Download candidate names, levels,
                            scores, summaries, AI status, and
                            timestamps in UTF-8 CSV format.
                        </p>

                    </div>

                </div>


                <div
                    className="
                        mt-7
                        rounded-xl
                        border
                        border-gray-200
                        bg-gray-50
                        p-5
                    "
                >

                    <p
                        className="
                            text-sm
                            font-medium
                            text-gray-900
                        "
                    >
                        CSV export includes
                    </p>

                    <ul
                        className="
                            mt-3
                            grid
                            gap-2
                            text-sm
                            text-gray-600
                            sm:grid-cols-2
                        "
                    >
                        <li>• Candidate identity and level</li>
                        <li>• Final, rule, and AI scores</li>
                        <li>• AI processing status</li>
                        <li>• Candidate summary</li>
                        <li>• Created and updated timestamps</li>
                        <li>• UTF-8 support for Thai text</li>
                    </ul>

                </div>


                <button
                    type="button"
                    onClick={handleExport}
                    disabled={loading}
                    className="
                        mt-6
                        inline-flex
                        items-center
                        justify-center
                        gap-2
                        rounded-xl
                        bg-blue-600
                        px-5
                        py-3
                        font-medium
                        text-white
                        transition-colors
                        hover:bg-blue-700
                        disabled:cursor-not-allowed
                        disabled:opacity-50
                    "
                >

                    {loading ? (

                        <>
                            <Loader2
                                size={18}
                                className="animate-spin"
                            />
                            Preparing CSV...
                        </>

                    ) : (

                        <>
                            <Download size={18} />
                            Export CSV
                        </>

                    )}

                </button>


                {message && (

                    <div
                        role="status"
                        className="
                            mt-6
                            flex
                            items-start
                            gap-3
                            rounded-xl
                            border
                            border-green-200
                            bg-green-50
                            p-4
                            text-sm
                            text-green-700
                        "
                    >
                        <CheckCircle2
                            size={19}
                            className="mt-0.5 shrink-0"
                        />

                        <span>
                            {message}
                        </span>
                    </div>

                )}


                {error && (

                    <div
                        role="alert"
                        className="
                            mt-6
                            rounded-xl
                            border
                            border-red-200
                            bg-red-50
                            p-4
                            text-sm
                            text-red-700
                        "
                    >
                        {error}
                    </div>

                )}

            </section>

        </AppLayout>

    );

}