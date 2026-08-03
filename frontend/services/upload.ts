import axios from "axios";

import { api } from "./api";

export async function uploadResume(
    file: File
) {

    const formData = new FormData();

    formData.append(
        "file",
        file
    );

    try {

        const response = await api.post(
            "/upload/",
            formData,
            {
                timeout: 120000,
            }
        );

        return response.data;

    } catch (error) {

        if (
            axios.isAxiosError(error)
        ) {

            throw new Error(
                error.response?.data?.detail ??
                "Resume upload failed."
            );
        }

        throw error;
    }
}