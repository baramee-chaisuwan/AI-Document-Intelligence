import axios from "axios";

import { api } from "./api";

import type {
    AccessTokenResponse,
    AuthUser,
    LoginCredentials,
    RegisterCredentials,
} from "@/types/auth";


function validationErrorMessage(
    detail: unknown
): string | null {

    if (!Array.isArray(detail)) {
        return null;
    }

    const messages = detail.flatMap((item) => {

        if (
            typeof item !== "object"
            || item === null
        ) {
            return [];
        }

        const validationError = item as {
            loc?: unknown;
            msg?: unknown;
        };

        if (typeof validationError.msg !== "string") {
            return [];
        }

        const location = Array.isArray(
            validationError.loc
        )
            ? validationError.loc
            : [];

        const rawField = location.at(-1);

        const field = typeof rawField === "string"
            ? rawField.replaceAll("_", " ")
            : "Request";

        const label = (
            field.charAt(0).toUpperCase()
            + field.slice(1)
        );

        const message = validationError.msg.replace(
            /^Value error,\s*/,
            ""
        );

        return [`${label}: ${message}`];

    });

    return messages.length > 0
        ? messages.join(" ")
        : null;

}


function authErrorMessage(
    error: unknown,
    fallback: string
): string {

    if (axios.isAxiosError(error)) {

        const detail = error.response?.data?.detail;

        if (typeof detail === "string") {
            return detail;
        }

        const validationMessage = (
            validationErrorMessage(detail)
        );

        if (validationMessage) {
            return validationMessage;
        }

    }

    return fallback;

}


export async function registerUser(
    credentials: RegisterCredentials
): Promise<AuthUser> {

    try {

        const response = await api.post<AuthUser>(
            "/auth/register",
            credentials
        );

        return response.data;

    } catch (error) {

        throw new Error(
            authErrorMessage(
                error,
                "Unable to create your account."
            )
        );

    }

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
