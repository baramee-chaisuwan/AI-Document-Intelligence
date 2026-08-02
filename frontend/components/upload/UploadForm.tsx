"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { uploadResume } from "@/services/upload";

export default function UploadForm() {

    const router = useRouter();

    const [file, setFile] = useState<File | null>(null);

    const [loading, setLoading] = useState(false);

    const [message, setMessage] = useState("");

    const [duplicateId, setDuplicateId] = useState<number | null>(null);

    async function handleUpload() {

        if (!file) {

            setMessage("Please select a PDF file.");

            return;

        }

        try {

            setLoading(true);

            setMessage("");

            setDuplicateId(null);

            const result = await uploadResume(file);

            if (result.status === "duplicate") {

                setMessage("Candidate already exists.");

                setDuplicateId(result.existing_id);

                return;

            }

            setMessage("Resume uploaded successfully.");

            if (result.candidate_id) {

                setTimeout(() => {

                    router.push(
                        `/candidates/${result.candidate_id}`
                    );

                }, 1000);

            }

        }

        catch (error) {

            console.error(error);

            setMessage("Upload failed.");

        }

        finally {

            setLoading(false);

        }

    }

    return (

        <div className="mt-8 rounded-xl border border-gray-200 bg-white p-8 shadow-sm">

            <h2 className="text-2xl font-bold">
                Upload Resume
            </h2>

            <p className="mt-2 text-gray-500">
                Upload a candidate resume for AI analysis.
            </p>

            <div
                className="
                    mt-8
                    rounded-xl
                    border-2
                    border-dashed
                    border-blue-300
                    bg-blue-50
                    p-10
                    text-center
                "
            >

                <div className="text-5xl">
                    📄
                </div>

                <h3 className="mt-4 text-xl font-semibold">
                    Upload Resume PDF
                </h3>

                <p className="mt-2 text-sm text-gray-500">
                    PDF only • Maximum 10 MB
                </p>

                <input

                    id="resume-upload"

                    type="file"

                    accept=".pdf"

                    className="hidden"

                    onChange={(e) => {

                        setFile(
                            e.target.files?.[0] ?? null
                        );

                        setMessage("");

                        setDuplicateId(null);

                    }}

                />

                <label

                    htmlFor="resume-upload"

                    className="
                        mt-8
                        inline-flex
                        cursor-pointer
                        rounded-xl
                        bg-blue-600
                        px-8
                        py-3
                        font-semibold
                        text-white
                        transition
                        hover:bg-blue-700
                    "

                >

                    Choose Resume

                </label>

                {file && (

                    <div
                        className="
                            mt-8
                            rounded-xl
                            border
                            border-green-200
                            bg-green-50
                            p-4
                            text-left
                        "
                    >

                        <p className="text-sm text-gray-500">

                            Selected File

                        </p>

                        <p className="mt-2 font-semibold text-green-700">

                            📄 {file.name}

                        </p>

                    </div>

                )}

            </div>

            <button

                onClick={handleUpload}

                disabled={loading}

                className="
                    mt-8
                    w-full
                    rounded-xl
                    bg-blue-600
                    px-6
                    py-4
                    text-lg
                    font-semibold
                    text-white
                    transition
                    hover:bg-blue-700
                    disabled:cursor-not-allowed
                    disabled:opacity-50
                "

            >

                {loading

                    ? "Uploading Resume..."

                    : "Upload Resume"}

            </button>

            {message && (

                <div
                    className="
                        mt-6
                        rounded-xl
                        border
                        bg-gray-50
                        p-5
                    "
                >
                    <p className="font-medium">

                        {message}

                    </p>

                    {duplicateId && (

                        <button

                            onClick={() =>
                                router.push(
                                    `/candidates/${duplicateId}`
                                )
                            }

                            className="
                                mt-4
                                rounded-lg
                                bg-gray-900
                                px-5
                                py-2
                                text-white
                                transition
                                hover:bg-black
                            "
                        >

                            View Existing Candidate

                        </button>

                    )}

                </div>

            )}

        </div>

    );

}