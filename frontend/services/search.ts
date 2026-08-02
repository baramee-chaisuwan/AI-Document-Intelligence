import { api } from "./api";

export async function searchCandidates(
    query: string
) {
    const response = await api.post(
        "/search/",
        {
            query,
        }
    );

    return response.data;
}