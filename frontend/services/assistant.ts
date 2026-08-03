import axios from "axios";

import { api } from "./api";


export type AssistantResponse = {
    answer: string;
};


export async function askAssistant(
    question: string
): Promise<AssistantResponse> {

    try {

        const response = await api.post<AssistantResponse>(
            "/assistant/",
            {
                question,
            }
        );

        return response.data;

    } catch (error) {

        if (axios.isAxiosError(error)) {

            throw new Error(
                error.response?.data?.detail
                ?? "AI assistant is unavailable."
            );

        }

        throw error;

    }

}