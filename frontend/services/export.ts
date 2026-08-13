import axios from "axios";

import { api } from "./api";
import { resolveExportFilename } from "../lib/export-download";


const EXCEL_CONTENT_TYPE =
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet";


export async function exportCandidatesExcel(): Promise<void> {

    try {

        const response = await api.get(
            "/export/xlsx",
            {
                responseType: "blob",
            }
        );


        const disposition =
            response.headers["content-disposition"];

        const filename = resolveExportFilename(
            disposition
        );


        const blob = new Blob(
            [response.data],
            {
                type: EXCEL_CONTENT_TYPE,
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
