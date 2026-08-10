import axios from "axios";

import { api } from "./api";


export interface ScoreBreakdown {
    python: number;
    sql: number;
    backend: number;
    devops: number;
    ai_domain: number;
    data_domain: number;
    backend_domain: number;
    experience: number;
    projects: number;
    engineering_signal: number;
}


export type CandidateStage = (
    | "APPLIED"
    | "SCREENING"
    | "INTERVIEW"
    | "OFFER"
    | "REJECTED"
);


export interface Candidate {
    id: number;
    name: string;
    summary: string;
    candidate_level: string;
    candidate_stage: CandidateStage;
    skill_score: number;
    rule_score: number;
    ai_score: number;
    ai_status: string;
    score_breakdown: ScoreBreakdown;
    created_at: string;
    updated_at?: string;
}


export interface CandidateUpdate {
    name?: string;
    summary?: string;
    candidate_level?: string;
    skill_score?: number;
    rule_score?: number;
    ai_score?: number;
    ai_status?: string;
    score_breakdown?: Partial<ScoreBreakdown>;
}


export interface DeleteCandidateResponse {
    message: string;
}


export async function getCandidates(
    skip = 0,
    limit = 10
): Promise<Candidate[]> {

    try {

        const response = await api.get<Candidate[]>(
            "/candidates/",
            {
                params: {
                    skip,
                    limit,
                },
            }
        );

        return response.data;

    } catch (error) {

        if (axios.isAxiosError(error)) {

            throw new Error(
                error.response?.data?.detail
                ?? "Could not load candidates."
            );

        }

        throw error;

    }

}


export async function getCandidateById(
    id: number
): Promise<Candidate> {

    try {

        const response = await api.get<Candidate>(
            `/candidates/${id}`
        );

        return response.data;

    } catch (error) {

        if (axios.isAxiosError(error)) {

            throw new Error(
                error.response?.data?.detail
                ?? "Could not load candidate."
            );

        }

        throw error;

    }

}


export async function deleteCandidate(
    id: number
): Promise<DeleteCandidateResponse> {

    try {

        const response = await api.delete<DeleteCandidateResponse>(
            `/candidates/${id}`
        );

        return response.data;

    } catch (error) {

        if (axios.isAxiosError(error)) {

            throw new Error(
                error.response?.data?.detail
                ?? "Could not delete candidate."
            );

        }

        throw error;

    }

}


export async function updateCandidate(
    id: number,
    payload: CandidateUpdate
): Promise<Candidate> {

    try {

        const response = await api.put<Candidate>(
            `/candidates/${id}`,
            payload
        );

        return response.data;

    } catch (error) {

        if (axios.isAxiosError(error)) {

            throw new Error(
                error.response?.data?.detail
                ?? "Could not update candidate."
            );

        }

        throw error;

    }

}


export async function updateCandidateStage(
    candidateId: number,
    candidateStage: CandidateStage
): Promise<Candidate> {

    try {

        const response = await api.put<Candidate>(
            `/candidates/${candidateId}/stage`,
            {
                candidate_stage: candidateStage,
            }
        );

        return response.data;

    } catch (error) {

        if (axios.isAxiosError(error)) {

            switch (error.response?.status) {
                case 403:
                    throw new Error(
                        "You do not have permission to move candidates."
                    );
                case 404:
                    throw new Error(
                        "This candidate could not be found."
                    );
                default:
                    throw new Error(
                        "Could not update the candidate stage. Please try again."
                    );
            }

        }

        throw new Error(
            "Could not update the candidate stage. Please try again."
        );

    }

}
