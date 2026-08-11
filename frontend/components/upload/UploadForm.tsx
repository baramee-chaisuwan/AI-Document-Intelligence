"use client";

import {
    ChangeEvent,
    DragEvent,
    useEffect,
    useRef,
    useState,
} from "react";

import {
    FileText,
    Loader2,
    UploadCloud,
    X,
} from "lucide-react";

import ProcessingStatus, {
    UploadProgressState,
} from "@/components/upload/ProcessingStatus";
import {
    getProcessingJob,
    ResumeUploadApiError,
    uploadResumeAsync,
} from "@/services/upload";


const MAX_FILE_SIZE_MB = 10;
const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
const POLLING_INTERVAL_MS = 2500;
const POLLING_TIMEOUT_MS = 5 * 60 * 1000;
const MAX_CONSECUTIVE_POLL_FAILURES = 4;


export default function UploadForm() {

    const fileInputRef = useRef<HTMLInputElement | null>(null);
    const pollControllerRef = useRef<AbortController | null>(null);
    const submissionInFlightRef = useRef(false);

    const [file, setFile] = useState<File | null>(null);
    const [submitting, setSubmitting] = useState(false);
    const [dragging, setDragging] = useState(false);
    const [progressState, setProgressState] = (
        useState<UploadProgressState>("idle")
    );
    const [message, setMessage] = useState("");
    const [processingJobId, setProcessingJobId] = (
        useState<number | null>(null)
    );
    const [candidateId, setCandidateId] = (
        useState<number | null>(null)
    );

    useEffect(() => {
        return () => {
            pollControllerRef.current?.abort();
        };
    }, []);

    const processingActive = (
        progressState === "queued"
        || progressState === "processing"
        || progressState === "polling_error"
        || progressState === "timed_out"
    );

    function stopPolling() {
        pollControllerRef.current?.abort();
        pollControllerRef.current = null;
    }

    function resetProcessingState() {
        stopPolling();
        setProcessingJobId(null);
        setCandidateId(null);
        setProgressState("idle");
        setMessage("");
    }

    function validateFile(selectedFile: File) {
        const filename = selectedFile.name.trim().toLowerCase();

        if (!filename.endsWith(".pdf")) {
            throw new Error("Only PDF files are allowed.");
        }

        if (selectedFile.size === 0) {
            throw new Error("The selected file is empty.");
        }

        if (selectedFile.size > MAX_FILE_SIZE_BYTES) {
            throw new Error(
                `PDF size must not exceed ${MAX_FILE_SIZE_MB} MB.`
            );
        }
    }

    function selectFile(selectedFile: File | null) {
        resetProcessingState();

        if (!selectedFile) {
            setFile(null);
            return;
        }

        try {
            validateFile(selectedFile);
            setFile(selectedFile);
        } catch (error) {
            setFile(null);
            setProgressState("failed");
            setMessage(
                error instanceof Error
                    ? error.message
                    : "Invalid file."
            );

            if (fileInputRef.current) {
                fileInputRef.current.value = "";
            }
        }
    }

    function handleFileChange(
        event: ChangeEvent<HTMLInputElement>
    ) {
        selectFile(event.target.files?.[0] ?? null);
    }

    function handleDragOver(event: DragEvent<HTMLDivElement>) {
        event.preventDefault();

        if (!submitting) {
            setDragging(true);
        }
    }

    function handleDragLeave(event: DragEvent<HTMLDivElement>) {
        event.preventDefault();
        setDragging(false);
    }

    function handleDrop(event: DragEvent<HTMLDivElement>) {
        event.preventDefault();
        setDragging(false);

        if (submitting) {
            return;
        }

        selectFile(event.dataTransfer.files?.[0] ?? null);
    }

    function removeFile() {
        setFile(null);
        resetProcessingState();

        if (fileInputRef.current) {
            fileInputRef.current.value = "";
        }
    }

    async function pollProcessingJob(jobId: number) {
        stopPolling();

        const controller = new AbortController();
        pollControllerRef.current = controller;
        const deadline = Date.now() + POLLING_TIMEOUT_MS;
        let consecutiveFailures = 0;

        while (!controller.signal.aborted) {
            if (Date.now() >= deadline) {
                setProgressState("timed_out");
                setMessage(
                    "Processing is taking longer than expected. "
                    + "You can check the same job again."
                );
                break;
            }

            try {
                const job = await getProcessingJob(
                    jobId,
                    controller.signal
                );

                consecutiveFailures = 0;

                if (job.status === "PENDING") {
                    setProgressState("queued");
                    setMessage("Queued for AI processing.");
                } else if (job.status === "PROCESSING") {
                    setProgressState("processing");
                    setMessage("AI is processing the resume.");
                } else if (job.status === "COMPLETED") {
                    if (job.candidate_id === null) {
                        setProgressState("failed");
                        setMessage(
                            "Processing completed, but the candidate "
                            + "record is unavailable."
                        );
                    } else {
                        setCandidateId(job.candidate_id);
                        setProgressState("completed");
                        setMessage("Resume processing completed.");
                        setFile(null);

                        if (fileInputRef.current) {
                            fileInputRef.current.value = "";
                        }
                    }

                    break;
                } else if (job.status === "FAILED") {
                    setProgressState("failed");
                    setMessage(
                        job.error_message?.trim()
                        || "Resume processing failed. Please try again."
                    );
                    break;
                }
            } catch (error) {
                if (controller.signal.aborted) {
                    return;
                }

                if (error instanceof ResumeUploadApiError) {
                    if (error.status === 404) {
                        setProgressState("failed");
                        setMessage(
                            "The processing job could not be found. "
                            + "Please start another upload."
                        );
                        break;
                    }

                    if (error.status === 403) {
                        setProgressState("failed");
                        setMessage(
                            "You do not have permission to view "
                            + "this processing job."
                        );
                        break;
                    }

                    if (error.status === 401) {
                        setProgressState("failed");
                        setMessage("Your session has expired.");
                        break;
                    }
                }

                consecutiveFailures += 1;

                if (
                    consecutiveFailures
                    >= MAX_CONSECUTIVE_POLL_FAILURES
                ) {
                    setProgressState("polling_error");
                    setMessage(
                        "Processing may still be running, but its status "
                        + "could not be confirmed."
                    );
                    break;
                }
            }

            await waitForNextPoll(controller.signal);
        }

        if (pollControllerRef.current === controller) {
            pollControllerRef.current = null;
        }
    }

    async function handleUpload() {
        if (submissionInFlightRef.current || processingActive) {
            return;
        }

        if (!file) {
            setProgressState("failed");
            setMessage("Please select a PDF file.");
            return;
        }

        try {
            submissionInFlightRef.current = true;
            validateFile(file);
            stopPolling();
            setSubmitting(true);
            setProcessingJobId(null);
            setCandidateId(null);
            setProgressState("uploading");
            setMessage("Uploading resume...");

            const result = await uploadResumeAsync(file);

            if (
                !Number.isInteger(result.processing_job_id)
                || result.processing_job_id <= 0
                || result.status !== "PENDING"
            ) {
                throw new Error(
                    "The processing job could not be started."
                );
            }

            setProcessingJobId(result.processing_job_id);
            setProgressState("queued");
            setMessage("Queued for AI processing.");
            void pollProcessingJob(result.processing_job_id);
        } catch (error) {
            setProgressState("failed");
            setMessage(
                error instanceof Error
                    ? error.message
                    : "Resume submission failed. Please try again."
            );
        } finally {
            submissionInFlightRef.current = false;
            setSubmitting(false);
        }
    }

    function retryPolling() {
        if (processingJobId === null) {
            return;
        }

        setProgressState("queued");
        setMessage("Checking processing status...");
        void pollProcessingJob(processingJobId);
    }

    return (
        <section className="mt-8 rounded-2xl border border-gray-200 bg-white p-6 shadow-sm sm:p-8">
            <div>
                <h2 className="text-2xl font-bold text-gray-900">
                    Upload Resume
                </h2>
                <p className="mt-2 text-gray-500">
                    Upload a PDF resume for secure background parsing,
                    scoring, indexing, and AI analysis.
                </p>
            </div>

            <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`mt-8 rounded-2xl border-2 border-dashed p-8 text-center transition-colors sm:p-12 ${
                    dragging
                        ? "border-blue-500 bg-blue-100"
                        : "border-blue-300 bg-blue-50"
                }`}
            >
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-white shadow-sm">
                    <UploadCloud size={34} className="text-blue-600" />
                </div>

                <h3 className="mt-5 text-xl font-semibold text-gray-900">
                    Drop your resume here
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                    Or choose a PDF from your device
                </p>
                <p className="mt-1 text-xs text-gray-400">
                    PDF only · Maximum {MAX_FILE_SIZE_MB} MB
                </p>

                <input
                    ref={fileInputRef}
                    id="resume-upload"
                    type="file"
                    accept=".pdf,application/pdf"
                    disabled={submitting}
                    className="sr-only"
                    onChange={handleFileChange}
                />

                <label
                    htmlFor="resume-upload"
                    className={`mt-7 inline-flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition-colors hover:bg-blue-700 ${
                        submitting
                            ? "pointer-events-none opacity-50"
                            : "cursor-pointer"
                    }`}
                >
                    <FileText size={19} />
                    Choose Resume
                </label>

                {file && (
                    <div className="mt-8 flex flex-col gap-4 rounded-xl border border-green-200 bg-white p-4 text-left sm:flex-row sm:items-center sm:justify-between">
                        <div className="flex min-w-0 items-center gap-3">
                            <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-lg bg-green-50">
                                <FileText
                                    size={22}
                                    className="text-green-600"
                                />
                            </div>
                            <div className="min-w-0">
                                <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                                    Selected File
                                </p>
                                <p
                                    title={file.name}
                                    className="mt-1 truncate font-semibold text-gray-900"
                                >
                                    {file.name}
                                </p>
                                <p className="mt-1 text-xs text-gray-500">
                                    {(file.size / 1024 / 1024).toFixed(2)} MB
                                </p>
                            </div>
                        </div>

                        <button
                            type="button"
                            onClick={removeFile}
                            disabled={submitting}
                            aria-label="Remove selected resume"
                            className="inline-flex items-center justify-center gap-1.5 rounded-lg border border-gray-200 px-3 py-2 text-sm font-medium text-gray-600 transition-colors hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50"
                        >
                            <X size={16} />
                            Remove
                        </button>
                    </div>
                )}
            </div>

            <button
                type="button"
                onClick={handleUpload}
                disabled={submitting || processingActive || !file}
                className="mt-8 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-6 py-4 text-lg font-semibold text-white transition-colors hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
                {submitting ? (
                    <>
                        <Loader2 size={21} className="animate-spin" />
                        Uploading resume...
                    </>
                ) : processingActive ? (
                    <>
                        <Loader2 size={21} className="animate-spin" />
                        Processing in progress
                    </>
                ) : (
                    <>
                        <UploadCloud size={21} />
                        Upload Resume
                    </>
                )}
            </button>

            <ProcessingStatus
                state={progressState}
                message={message}
                processingJobId={processingJobId}
                candidateId={candidateId}
                onRetryPolling={retryPolling}
            />
        </section>
    );
}


function waitForNextPoll(signal: AbortSignal): Promise<void> {
    return new Promise((resolve) => {
        if (signal.aborted) {
            resolve();
            return;
        }

        const timeoutId = window.setTimeout(
            finish,
            POLLING_INTERVAL_MS
        );

        function finish() {
            window.clearTimeout(timeoutId);
            signal.removeEventListener("abort", finish);
            resolve();
        }

        signal.addEventListener("abort", finish, { once: true });
    });
}
