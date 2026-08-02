import { api } from "./api";


export async function exportCandidatesCSV() {

    const response = await api.get(
        "/export/csv",
        {
            responseType: "blob",
        }
    );


    const blob = new Blob(
        [response.data],
        {
            type: "text/csv",
        }
    );


    const url = window.URL.createObjectURL(
        blob
    );


    const link = document.createElement(
        "a"
    );

    link.href = url;

    link.download = "candidates.csv";

    document.body.appendChild(link);

    link.click();


    link.remove();

    window.URL.revokeObjectURL(url);

}