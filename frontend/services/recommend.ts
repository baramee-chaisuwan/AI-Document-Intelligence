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
) {

    const response = await api.post(
        "/recommend/",
        {
            question,
        }
    );


    return response.data as RecommendationResponse;

}