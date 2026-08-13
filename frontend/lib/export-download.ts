export function resolveExportFilename(
    disposition?: string,
): string {

    const fallback = "ATS_Candidates.xlsx";
    const match = disposition?.match(
        /filename\*?=(?:UTF-8''|\")?([^";]+)/i
    );

    if (!match?.[1]) {
        return fallback;
    }

    try {
        return decodeURIComponent(match[1].trim());
    } catch {
        return match[1].trim();
    }

}
