"use client";

import {
    ChangeEvent,
    DragEvent,
    useRef,
    useState,
} from "react";

import { useRouter } from "next/navigation";

import {
    CheckCircle2,
    FileText,
    Loader2,
    UploadCloud,
    X,
} from "lucide-react";

import { uploadResume } from "@/services/upload";


const MAX_FILE_SIZE_MB = 10;

const MAX_FILE_SIZE_BYTES = (
    MAX_FILE_SIZE_MB
    * 1024
    * 1024
);


type MessageType = (
    "success"
    | "duplicate"
    | "error"
    | ""
);


export default function UploadForm() {

    const router = useRouter();

    const fileInputRef = (
        useRef<HTMLInputElement | null>(
            null
        )
    );

    const [
        file,
        setFile,
    ] = useState<File | null>(
        null
    );

    const [
        loading,
        setLoading,
    ] = useState(false);

    const [
        dragging,
        setDragging,
    ] = useState(false);

    const [
        message,
        setMessage,
    ] = useState("");

    const [
        messageType,
        setMessageType,
    ] = useState<MessageType>("");

    const [
        duplicateId,
        setDuplicateId,
    ] = useState<number | null>(
        null
    );


    function resetMessage() {

        setMessage("");
        setMessageType("");
        setDuplicateId(null);

    }


    function validateFile(
        selectedFile: File
    ) {

        const filename = (
            selectedFile.name
                .trim()
                .toLowerCase()
        );


        if (!filename.endsWith(".pdf")) {

            throw new Error(
                "Only PDF files are allowed."
            );

        }


        if (selectedFile.size === 0) {

            throw new Error(
                "The selected file is empty."
            );

        }


        if (
            selectedFile.size
            > MAX_FILE_SIZE_BYTES
        ) {

            throw new Error(
                `PDF size must not exceed ${MAX_FILE_SIZE_MB} MB.`
            );

        }

    }


    function selectFile(
        selectedFile: File | null
    ) {

        resetMessage();


        if (!selectedFile) {

            setFile(null);
            return;

        }


        try {

            validateFile(
                selectedFile
            );

            setFile(
                selectedFile
            );

        } catch (error) {

            setFile(null);

            setMessageType(
                "error"
            );

            setMessage(
                error instanceof Error
                    ? error.message
                    : "Invalid file."
            );


            if (
                fileInputRef.current
            ) {

                fileInputRef.current.value = "";

            }

        }

    }


    function handleFileChange(
        event: ChangeEvent<HTMLInputElement>
    ) {

        selectFile(
            event.target.files?.[0]
            ?? null
        );

    }


    function handleDragOver(
        event: DragEvent<HTMLDivElement>
    ) {

        event.preventDefault();

        if (!loading) {

            setDragging(true);

        }

    }


    function handleDragLeave(
        event: DragEvent<HTMLDivElement>
    ) {

        event.preventDefault();

        setDragging(false);

    }


    function handleDrop(
        event: DragEvent<HTMLDivElement>
    ) {

        event.preventDefault();

        setDragging(false);


        if (loading) {
            return;
        }


        selectFile(
            event.dataTransfer.files?.[0]
            ?? null
        );

    }


    function removeFile() {

        setFile(null);
        resetMessage();


        if (
            fileInputRef.current
        ) {

            fileInputRef.current.value = "";

        }

    }


    async function handleUpload() {

        if (!file) {

            setMessageType(
                "error"
            );

            setMessage(
                "Please select a PDF file."
            );

            return;

        }


        try {

            validateFile(
                file
            );

            setLoading(true);
            resetMessage();


            const result = await uploadResume(
                file
            );


            if (
                result.status
                === "duplicate"
            ) {

                setMessageType(
                    "duplicate"
                );

                setMessage(
                    "This candidate already exists."
                );

                setDuplicateId(
                    result.existing_id
                );

                return;

            }


            if (!result.candidate_id) {

                throw new Error(
                    "Upload completed without a candidate ID."
                );

            }


            setMessageType(
                "success"
            );

            setMessage(
                "Resume uploaded and indexed successfully."
            );


            setFile(null);


            if (
                fileInputRef.current
            ) {

                fileInputRef.current.value = "";

            }


            window.setTimeout(
                () => {

                    router.push(
                        `/candidates/${result.candidate_id}`
                    );

                },
                800
            );

        } catch (error) {

            setMessageType(
                "error"
            );

            setMessage(
                error instanceof Error
                    ? error.message
                    : "Resume upload failed."
            );

        } finally {

            setLoading(false);

        }

    }


    const messageClassName = {

        success: (
            "border-green-200 "
            + "bg-green-50 "
            + "text-green-700"
        ),

        duplicate: (
            "border-amber-200 "
            + "bg-amber-50 "
            + "text-amber-800"
        ),

        error: (
            "border-red-200 "
            + "bg-red-50 "
            + "text-red-700"
        ),

        "": (
            "border-gray-200 "
            + "bg-gray-50 "
            + "text-gray-700"
        ),

    }[messageType];


    return (

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

            <div>

                <h2
                    className="
                        text-2xl
                        font-bold
                        text-gray-900
                    "
                >
                    Upload Resume
                </h2>

                <p
                    className="
                        mt-2
                        text-gray-500
                    "
                >
                    Upload a PDF resume for parsing,
                    scoring, indexing, and AI analysis.
                </p>

            </div>


            <div
                onDragOver={
                    handleDragOver
                }
                onDragLeave={
                    handleDragLeave
                }
                onDrop={
                    handleDrop
                }
                className={`
                    mt-8
                    rounded-2xl
                    border-2
                    border-dashed
                    p-8
                    text-center
                    transition-colors
                    sm:p-12
                    ${dragging
                        ? (
                            "border-blue-500 "
                            + "bg-blue-100"
                        )
                        : (
                            "border-blue-300 "
                            + "bg-blue-50"
                        )
                    }
                `}
            >

                <div
                    className="
                        mx-auto
                        flex
                        h-16
                        w-16
                        items-center
                        justify-center
                        rounded-2xl
                        bg-white
                        shadow-sm
                    "
                >

                    <UploadCloud
                        size={34}
                        className="text-blue-600"
                    />

                </div>


                <h3
                    className="
                        mt-5
                        text-xl
                        font-semibold
                        text-gray-900
                    "
                >
                    Drop your resume here
                </h3>

                <p
                    className="
                        mt-2
                        text-sm
                        text-gray-500
                    "
                >
                    Or choose a PDF from your device
                </p>

                <p
                    className="
                        mt-1
                        text-xs
                        text-gray-400
                    "
                >
                    PDF only · Maximum {MAX_FILE_SIZE_MB} MB
                </p>


                <input
                    ref={
                        fileInputRef
                    }
                    id="resume-upload"
                    type="file"
                    accept=".pdf,application/pdf"
                    disabled={
                        loading
                    }
                    className="sr-only"
                    onChange={
                        handleFileChange
                    }
                />


                <label
                    htmlFor="resume-upload"
                    className={`
                        mt-7
                        inline-flex
                        items-center
                        gap-2
                        rounded-xl
                        bg-blue-600
                        px-6
                        py-3
                        font-semibold
                        text-white
                        transition-colors
                        hover:bg-blue-700
                        ${loading
                            ? (
                                "pointer-events-none "
                                + "opacity-50"
                            )
                            : "cursor-pointer"
                        }
                    `}
                >
                    <FileText size={19} />
                    Choose Resume
                </label>


                {file && (

                    <div
                        className="
                            mt-8
                            flex
                            flex-col
                            gap-4
                            rounded-xl
                            border
                            border-green-200
                            bg-white
                            p-4
                            text-left
                            sm:flex-row
                            sm:items-center
                            sm:justify-between
                        "
                    >

                        <div
                            className="
                                flex
                                min-w-0
                                items-center
                                gap-3
                            "
                        >

                            <div
                                className="
                                    flex
                                    h-11
                                    w-11
                                    shrink-0
                                    items-center
                                    justify-center
                                    rounded-lg
                                    bg-green-50
                                "
                            >

                                <FileText
                                    size={22}
                                    className="text-green-600"
                                />

                            </div>


                            <div className="min-w-0">

                                <p
                                    className="
                                        text-xs
                                        font-medium
                                        uppercase
                                        tracking-wide
                                        text-gray-500
                                    "
                                >
                                    Selected File
                                </p>

                                <p
                                    title={
                                        file.name
                                    }
                                    className="
                                        mt-1
                                        truncate
                                        font-semibold
                                        text-gray-900
                                    "
                                >
                                    {file.name}
                                </p>

                                <p
                                    className="
                                        mt-1
                                        text-xs
                                        text-gray-500
                                    "
                                >
                                    {
                                        (
                                            file.size
                                            / 1024
                                            / 1024
                                        ).toFixed(2)
                                    } MB
                                </p>

                            </div>

                        </div>


                        <button
                            type="button"
                            onClick={
                                removeFile
                            }
                            disabled={
                                loading
                            }
                            aria-label="Remove selected resume"
                            className="
                                inline-flex
                                items-center
                                justify-center
                                gap-1.5
                                rounded-lg
                                border
                                border-gray-200
                                px-3
                                py-2
                                text-sm
                                font-medium
                                text-gray-600
                                transition-colors
                                hover:bg-gray-50
                                disabled:cursor-not-allowed
                                disabled:opacity-50
                            "
                        >
                            <X size={16} />
                            Remove
                        </button>

                    </div>

                )}

            </div>


            <button
                type="button"
                onClick={
                    handleUpload
                }
                disabled={
                    loading
                    || !file
                }
                className="
                    mt-8
                    inline-flex
                    w-full
                    items-center
                    justify-center
                    gap-2
                    rounded-xl
                    bg-blue-600
                    px-6
                    py-4
                    text-lg
                    font-semibold
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
                            size={21}
                            className="animate-spin"
                        />

                        Analyzing and indexing resume...
                    </>

                ) : (

                    <>
                        <UploadCloud size={21} />
                        Upload Resume
                    </>

                )}

            </button>


            {loading && (

                <p
                    className="
                        mt-3
                        text-center
                        text-sm
                        text-gray-500
                    "
                >
                    This may take a moment while the AI
                    extracts and evaluates the resume.
                </p>

            )}


            {message && (

                <div
                    role={
                        messageType === "error"
                            ? "alert"
                            : "status"
                    }
                    className={`
                        mt-6
                        rounded-xl
                        border
                        p-5
                        ${messageClassName}
                    `}
                >

                    <div
                        className="
                            flex
                            items-start
                            gap-3
                        "
                    >

                        {messageType === "success" && (

                            <CheckCircle2
                                size={21}
                                className="mt-0.5 shrink-0"
                            />

                        )}

                        <div>

                            <p className="font-medium">
                                {message}
                            </p>


                            {duplicateId && (

                                <button
                                    type="button"
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
                                        text-sm
                                        font-medium
                                        text-white
                                        transition-colors
                                        hover:bg-black
                                    "
                                >
                                    View Existing Candidate
                                </button>

                            )}

                        </div>

                    </div>

                </div>

            )}

        </section>

    );

}