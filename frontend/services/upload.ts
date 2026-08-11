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
