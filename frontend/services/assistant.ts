import { api } from "./api";


export async function askAssistant(
    question: string
) {

    const response = await api.post(
        "/assistant/",
        {
            question,
        }
    );

    return response.data;

}