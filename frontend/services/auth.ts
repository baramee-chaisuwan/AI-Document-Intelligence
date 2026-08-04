import axios from "axios";

import { api } from "./api";

import type {
    AccessTokenResponse,
    AuthUser,
    LoginCredentials,
} from "@/types/auth";


function authErrorMessage(
    error: unknown,
    fallback: string
): string {

    if (axios.isAxiosError(error)) {

        const detail = error.response?.data?.detail;

        if (typeof detail === "string") {
            return detail;
        }

    }

    return fallback;

}


export async function loginUser(
    credentials: LoginCredentials
): Promise<AccessTokenResponse> {

    try {

        const response = (
            await api.post<AccessTokenResponse>(
                "/auth/login",
                credentials
            )
        );

        return response.data;

    } catch (error) {

        throw new Error(
            authErrorMessage(
                error,
                "Unable to sign in."
            )
        );

    }

}


export async function getCurrentUser():
    Promise<AuthUser> {

    try {

        const response = await api.get<AuthUser>(
            "/auth/me"
        );

        return response.data;

    } catch (error) {

        throw new Error(
            authErrorMessage(
                error,
                "Unable to load your account."
            )
        );

    }

}
