import { api } from "./api";

export async function getCandidates() {

    const response = await api.get(
        "/candidates/"
    );

    return response.data;

}

export async function getCandidateById(
    id: number
) {

    const response = await api.get(
        `/candidates/${id}`
    );

    return response.data;

}

export async function deleteCandidate(
    id: number
) {

    await api.delete(
        `/candidates/${id}`
    );

}

export async function updateCandidate(
    id: number,
    payload: object
) {

    const response = await api.put(
        `/candidates/${id}`,
        payload
    );

    return response.data;

}