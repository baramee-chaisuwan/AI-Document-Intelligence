import axios from "axios";

import { api } from "./api";


export type SearchResult = {
    id: number;
    name: string;
    summary: string;
    candidate_level: string;
    skill_score: number;
    rule_score: number;
    ai_score: number;
    distance: number;
};


export type SearchResponse = {
    results: SearchResult[];
};


export async function searchCandidates(
    query: string
): Promise<SearchResponse> {

    try {

        const response = await api.post<SearchResponse>(
            "/search/",
            {
                query,
            }
        );

        return {
            results: response.data.results ?? [],
        };

    } catch (error) {

        if (axios.isAxiosError(error)) {

            throw new Error(
                error.response?.data?.detail
                ?? "Candidate search failed."
            );

        }

        throw error;

    }

}