import axios from "axios";

import { api } from "./api";


export async function exportCandidatesCSV(): Promise<void> {

    try {

        const response = await api.get(
            "/export/csv",
            {
                responseType: "blob",
            }
        );


        const disposition =
            response.headers["content-disposition"];

        let filename = "candidates.csv";


        const match =
            disposition?.match(
                /filename="?([^"]+)"?/
            );

        if (match?.[1]) {

            filename = match[1];

        }


        const blob = new Blob(
            [response.data],
            {
                type: "text/csv",
            }
        );


        const url =
            window.URL.createObjectURL(
                blob
            );


        const link =
            document.createElement("a");

        link.href = url;
        link.download = filename;

        document.body.appendChild(link);

        link.click();

        link.remove();

        window.URL.revokeObjectURL(url);

    } catch (error) {

        if (axios.isAxiosError(error)) {

            throw new Error(
                error.response?.data?.detail
                ?? "Failed to export candidates."
            );

        }

        throw error;

    }

}