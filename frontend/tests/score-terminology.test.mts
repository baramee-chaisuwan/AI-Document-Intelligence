import assert from "node:assert/strict";
import test from "node:test";

import {
    AI_ANALYSIS_SCORE_LABEL,
    JOB_MATCH_SCORE_LABEL,
    scoreLabels,
} from "../lib/score-labels.ts";


test("versioned profile scores remain distinct from job match score", () => {
    const legacy = scoreLabels({ python: 8 });
    const profile = scoreLabels({ score_version: "profile_v2" });

    assert.equal(legacy.profile, "Legacy Technical Profile Score");
    assert.equal(legacy.rule, "Legacy Technical Rule Score");
    assert.equal(profile.profile, "Candidate Profile Score");
    assert.equal(profile.rule, "Profile Rule Score");
    assert.equal(AI_ANALYSIS_SCORE_LABEL, "AI Analysis Score");
    assert.equal(JOB_MATCH_SCORE_LABEL, "Job Match Score");
    assert.notEqual(profile.profile, JOB_MATCH_SCORE_LABEL);
});
