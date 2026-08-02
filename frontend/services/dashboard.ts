import { api } from "./api";

export async function getDashboardSummary() {

    const response = await api.get(
        "/dashboard/summary"
    );

    return response.data;

}

export async function getTopCandidates() {

    const response = await api.get(
        "/dashboard/top-candidates"
    );

    return response.data ?? [];

}

export async function getRecentCandidates() {

    const response = await api.get(
        "/dashboard/recent-candidates"
    );

    return response.data ?? [];

}

export async function getLevelDistribution() {

    const response = await api.get(
        "/dashboard/level-distribution"
    );

    return response.data ?? [];

}

export async function getScoreDistribution() {

    const response = await api.get(
        "/dashboard/score-distribution"
    );

    return response.data ?? [];

}