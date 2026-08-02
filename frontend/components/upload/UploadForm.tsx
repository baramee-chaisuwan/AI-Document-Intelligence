"use client";

import { useState } from "react";
import { uploadResume } from "@/services/upload";
import { useRouter } from "next/navigation";

export default function UploadForm() {
    const router = useRouter();

    const [file, setFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState("");
    const [duplicateId, setDuplicateId] = useState<number | null>(null);

    async function handleUpload() {
        if (!file) {
            setMessage("Please select a PDF file");
            return;
        }

        try {
            setLoading(true);
            setMessage("");
            setDuplicateId(null);

            const result = await uploadResume(file);

            if (result.status === "duplicate") {
                setMessage(
                    "Candidate already exists"
                );

                setDuplicateId(
                    result.existing_id
                );

                return;
            }

            setMessage(
                "Upload successful"
            );

            if (result.candidate_id) {
                setTimeout(() => {
                    router.push(
                        `/candidates/${result.candidate_id}`
                    );
                }, 1000);

                return;
            }

            setTimeout(() => {
                router.push("/candidates");
            }, 1000);


        } catch (error) {
            console.error(error);

            setMessage(
                "Upload failed"
            );

        } finally {
            setLoading(false);
        }
    }


    return (
        <div className="mt-6 rounded-lg bg-white p-6 shadow">

            <h2 className="text-xl font-bold">
                Upload Resume
            </h2>

            <p className="mt-2 text-gray-500">
                Upload candidate resume PDF file.
            </p>


            <input
                type="file"
                accept=".pdf"
                className="mt-6 block"
                onChange={(e) => {
                    setFile(
                        e.target.files?.[0] ?? null
                    );

                    setMessage("");
                    setDuplicateId(null);
                }}
            />


            <button
                onClick={handleUpload}
                disabled={loading}
                className="mt-4 rounded-lg bg-blue-600 px-5 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
            >
                {loading
                    ? "Uploading..."
                    : "Upload"
                }
            </button>


            {message && (
                <div className="mt-4">

                    <p className="text-sm text-gray-600">
                        {message}
                    </p>


                    {duplicateId && (
                        <button
                            onClick={() =>
                                router.push(
                                    `/candidates/${duplicateId}`
                                )
                            }
                            className="mt-3 rounded-lg bg-gray-800 px-4 py-2 text-sm text-white hover:bg-gray-900"
                        >
                            View Candidate
                        </button>
                    )}

                </div>
            )}

        </div>
    );
}