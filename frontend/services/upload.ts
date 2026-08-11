import axios from "axios";

import { api } from "./api";


export type ProcessingJobStatus = (
    "PENDING"
    | "PROCESSING"
    | "COMPLETED"
    | "FAILED"
);


export interface AsyncResumeSubmissionResponse {
    processing_job_id: number;
    status: "PENDING";
}


export interface ExactDuplicateResumeResponse {
    status: "duplicate";
    message: string;
    candidate_id: number | null;
}


export interface ProcessingJob {
    id: number;
    candidate_id: number | null;
    status: ProcessingJobStatus;
    error_message: string | null;
    created_at: string;
    started_at: string | null;
    completed_at: string | null;
    updated_at: string;
}


export class ResumeUploadApiError extends Error {

    status: number | undefined;

    constructor(
        message: string,
        status?: number
    ) {
        super(message);
        this.name = "ResumeUploadApiError";
        this.status = status;
    }
}


export class DuplicateResumeUploadError extends ResumeUploadApiError {

    candidateId: number | null;

    constructor(candidateId: number | null) {
        super("This exact resume has already been uploaded.", 409);
        this.name = "DuplicateResumeUploadError";
        this.candidateId = candidateId;
    }
}

export async function uploadResume(
    file: File
) {

    const formData = new FormData();

    formData.append(
        "file",
        file
    );

    try {

        const response = await api.post(
            "/upload/",
            formData,
            {
                timeout: 120000,
            }
        );

        return response.data;

    } catch (error) {

        if (
            axios.isAxiosError(error)
        ) {

            throw new Error(
                error.response?.data?.detail ??
                "Resume upload failed."
            );
        }

        throw error;
    }
}


export async function uploadResumeAsync(
    file: File,
    signal?: AbortSignal
): Promise<AsyncResumeSubmissionResponse> {

    const formData = new FormData();

    formData.append("file", file);

    try {
        const response = await api.post<AsyncResumeSubmissionResponse>(
            "/upload/async",
            formData,
            {
                timeout: 120000,
                signal,
            }
        );

        return response.data;
    } catch (error) {
        throwUploadApiError(
            error,
            "Resume submission failed. Please try again."
        );
    }
}


export async function getProcessingJob(
    processingJobId: number,
    signal?: AbortSignal
): Promise<ProcessingJob> {

    try {
        const response = await api.get<ProcessingJob>(
            `/processing-jobs/${processingJobId}`,
            { signal }
        );

        return response.data;
    } catch (error) {
        throwUploadApiError(
            error,
            "Could not confirm resume processing status."
        );
    }
}


function throwUploadApiError(
    error: unknown,
    fallbackMessage: string
): never {

    if (axios.isCancel(error)) {
        throw error;
    }

    if (axios.isAxiosError(error)) {
        if (error.response?.status === 409) {
            const duplicate = parseDuplicateResponse(
                error.response.data
            );

            throw new DuplicateResumeUploadError(
                duplicate?.candidate_id ?? null
            );
        }

        const detail = error.response?.data?.detail;

        throw new ResumeUploadApiError(
            typeof detail === "string"
                ? detail
                : fallbackMessage,
            error.response?.status
        );
    }

    throw new ResumeUploadApiError(
        fallbackMessage
    );
}


function parseDuplicateResponse(
    value: unknown
): ExactDuplicateResumeResponse | null {

    if (
        typeof value !== "object"
        || value === null
        || !("status" in value)
        || value.status !== "duplicate"
        || !("message" in value)
        || typeof value.message !== "string"
        || !("candidate_id" in value)
    ) {
        return null;
    }

    const candidateId = value.candidate_id;

    if (
        candidateId !== null
        && (
            typeof candidateId !== "number"
            || !Number.isInteger(candidateId)
            || candidateId <= 0
        )
    ) {
        return null;
    }

    return {
        status: "duplicate",
        message: value.message,
        candidate_id: candidateId,
    };
}
