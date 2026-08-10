import axios from "axios";

import { api } from "./api";

import type {
    CreateJobPayload,
    Job,
    JobMatchResult,
} from "@/types/job";


function jobErrorMessage(
    error: unknown,
    fallback: string
): string {

    if (!axios.isAxiosError(error)) {
        return fallback;
    }

    switch (error.response?.status) {
        case 403:
            return "You do not have permission to perform this action.";
        case 404:
            return "The selected job could not be found.";
        case 409:
            return "This job is not ready for candidate matching.";
        default:
            return fallback;
    }
}


export async function createJob(
    payload: CreateJobPayload
): Promise<Job> {

    try {
        const response = await api.post<Job>(
            "/jobs",
            payload
        );

        return response.data;
    } catch (error) {
        throw new Error(
            jobErrorMessage(
                error,
                "Could not create the job. Please try again."
            )
        );
    }
}


export async function getJobs(): Promise<Job[]> {

    try {
        const response = await api.get<Job[]>(
            "/jobs"
        );

        return response.data;
    } catch (error) {
        throw new Error(
            jobErrorMessage(
                error,
                "Could not load jobs. Please try again."
            )
        );
    }
}


export async function matchJobCandidates(
    jobId: number
): Promise<JobMatchResult[]> {

    try {
        const response = await api.post<
            JobMatchResult[]
        >(`/jobs/${jobId}/match`);

        return response.data;
    } catch (error) {
        throw new Error(
            jobErrorMessage(
                error,
                "Could not match candidates. Please try again."
            )
        );
    }
}
