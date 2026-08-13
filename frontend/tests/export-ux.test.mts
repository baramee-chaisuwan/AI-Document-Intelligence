import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

import { resolveExportFilename } from "../lib/export-download.ts";


test("Excel export uses the backend attachment filename", () => {
    assert.equal(
        resolveExportFilename(
            'attachment; filename="ATS_Candidates_2026-08-14_12-30.xlsx"'
        ),
        "ATS_Candidates_2026-08-14_12-30.xlsx",
    );
    assert.equal(
        resolveExportFilename(undefined),
        "ATS_Candidates.xlsx",
    );
});


test("export page presents Excel loading, success, and error UX", () => {
    const page = fs.readFileSync(
        path.resolve(process.cwd(), "app/export/page.tsx"),
        "utf8",
    );

    assert.match(page, /Export Candidates \(\.xlsx\)/);
    assert.match(page, /Preparing Excel\.\.\./);
    assert.match(page, /Excel report exported successfully/);
    assert.match(page, /role="alert"/);
    assert.doesNotMatch(page, /Export CSV/);
});


test("export service requests a blob and completes browser download cleanup", () => {
    const service = fs.readFileSync(
        path.resolve(process.cwd(), "services/export.ts"),
        "utf8",
    );

    assert.match(service, /\/export\/xlsx/);
    assert.match(service, /responseType: "blob"/);
    assert.match(service, /link\.download = filename/);
    assert.match(service, /revokeObjectURL/);
});
