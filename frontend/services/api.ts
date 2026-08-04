import axios from "axios";

import {
    clearAccessToken,
    getAccessToken,
} from "@/lib/token-storage";

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


api.interceptors.request.use(
    (config) => {

        const token = getAccessToken();

        if (token) {

            config.headers.Authorization = (
                `Bearer ${token}`
            );

        }

        return config;

    }
);


api.interceptors.response.use(
    (response) => response,
    (error) => {

        if (
            axios.isAxiosError(error)
            && error.response?.status === 401
        ) {

            clearAccessToken();

            if (
                typeof window !== "undefined"
                && window.location.pathname
                !== "/login"
            ) {

                window.location.replace(
                    "/login"
                );

            }

        }

        return Promise.reject(error);

    }
);
