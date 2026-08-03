import axios from "axios";

import { api } from "./api";


export interface DashboardSummary {
    total_candidates: number;
    average_score: number;
    top_candidate: string | null;
    top_score: number;
    junior_count: number;
    mid_count: number;
    senior_count: number;
}


export interface TopCandidate {
    id: number;
    name: string;
    ai_score: number;
}


export interface RecentCandidate {
    id: number;
    name: string;
    candidate_level: string;
    ai_score: number;
    created_at: string;
}


export interface LevelDistribution {
    level: string;
    count: number;
}


export interface ScoreDistribution {
    score_range: string;
    count: number;
}


function getErrorMessage(
    error: unknown,
    fallbackMessage: string
) {

    if (axios.isAxiosError(error)) {

        return (
            error.response?.data?.detail
            ?? fallbackMessage
        );

    }

    return fallbackMessage;

}


export async function getDashboardSummary():
    Promise<DashboardSummary> {

    try {

        const response = await api.get<DashboardSummary>(
            "/dashboard/summary"
        );

        return response.data;

    } catch (error) {

        throw new Error(
            getErrorMessage(
                error,
                "Could not load dashboard summary."
            )
        );

    }

}


export async function getTopCandidates(
    limit = 5
): Promise<TopCandidate[]> {

    try {

        const response = await api.get<TopCandidate[]>(
            "/dashboard/top-candidates",
            {
                params: {
                    limit,
                },
            }
        );

        return response.data ?? [];

    } catch (error) {

        throw new Error(
            getErrorMessage(
                error,
                "Could not load top candidates."
            )
        );

    }

}


export async function getRecentCandidates(
    limit = 5
): Promise<RecentCandidate[]> {

    try {

        const response = await api.get<RecentCandidate[]>(
            "/dashboard/recent-candidates",
            {
                params: {
                    limit,
                },
            }
        );

        return response.data ?? [];

    } catch (error) {

        throw new Error(
            getErrorMessage(
                error,
                "Could not load recent candidates."
            )
        );

    }

}


export async function getLevelDistribution():
    Promise<LevelDistribution[]> {

    try {

        const response = await api.get<LevelDistribution[]>(
            "/dashboard/level-distribution"
        );

        return response.data ?? [];

    } catch (error) {

        throw new Error(
            getErrorMessage(
                error,
                "Could not load candidate levels."
            )
        );

    }

}


export async function getScoreDistribution():
    Promise<ScoreDistribution[]> {

    try {

        const response = await api.get<ScoreDistribution[]>(
            "/dashboard/score-distribution"
        );

        return response.data ?? [];

    } catch (error) {

        throw new Error(
            getErrorMessage(
                error,
                "Could not load score distribution."
            )
        );

    }

}