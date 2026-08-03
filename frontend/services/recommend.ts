import axios from "axios";

import { api } from "./api";

export type RecommendationResponse = {
    candidate_id: string;
    candidate_name: string;
    match_score: number;
    strengths: string[];
    relevant_experience: string[];
    reason: string;
};

export async function getRecommendation(
    question: string
): Promise<RecommendationResponse> {

    try {

        const response = await api.post<RecommendationResponse>(
            "/recommend/",
            {
                question,
            }
        );

        return response.data;

    } catch (error) {

        if (axios.isAxiosError(error)) {

            throw new Error(
                error.response?.data?.detail
                ?? "Unable to generate recommendation."
            );

        }

        throw error;

    }

}