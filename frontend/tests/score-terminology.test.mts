import assert from "node:assert/strict";
import test from "node:test";

import {
    AI_ANALYSIS_SCORE_LABEL,
    JOB_MATCH_SCORE_LABEL,
    TECHNICAL_PROFILE_SCORE_LABEL,
    TECHNICAL_RULE_SCORE_LABEL,
} from "../lib/score-labels.ts";


test("standalone technical scores are distinct from job match score", () => {
    assert.equal(TECHNICAL_PROFILE_SCORE_LABEL, "Technical Profile Score");
    assert.equal(TECHNICAL_RULE_SCORE_LABEL, "Technical Rule Score");
    assert.equal(AI_ANALYSIS_SCORE_LABEL, "AI Analysis Score");
    assert.equal(JOB_MATCH_SCORE_LABEL, "Job Match Score");
    assert.notEqual(TECHNICAL_PROFILE_SCORE_LABEL, JOB_MATCH_SCORE_LABEL);
});
