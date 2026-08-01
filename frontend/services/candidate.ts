import { api } from "./api";

export async function getCandidates() {
    const response = await api.get("/candidates/");
    return response.data;
}

export async function getCandidateById(id: number) {
    const response = await api.get(`/candidates/${id}`);
    return response.data;
}