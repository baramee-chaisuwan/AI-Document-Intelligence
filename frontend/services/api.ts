import axios from "axios";

const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL;

if (!apiBaseUrl) {
    throw new Error(
        "NEXT_PUBLIC_API_URL is not configured"
    );
}

export const api = axios.create({
    baseURL: apiBaseUrl,
    timeout: 30000,
    headers: {
        Accept: "application/json",
    },
});