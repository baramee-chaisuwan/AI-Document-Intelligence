export const AI_ANALYSIS_SCORE_LABEL = "AI Analysis Score";
export const JOB_MATCH_SCORE_LABEL = "Job Match Score";

export type ScoreVersion = "technical_v1" | "profile_v2";


export function scoreVersion(
    breakdown: Record<string, unknown> | null | undefined
): ScoreVersion {
    return breakdown?.score_version === "profile_v2"
        ? "profile_v2"
        : "technical_v1";
}


export function scoreLabels(
    breakdown: Record<string, unknown> | null | undefined
) {
    return scoreVersion(breakdown) === "profile_v2"
        ? {
            profile: "Candidate Profile Score",
            rule: "Profile Rule Score",
            breakdown: "Profile Score Breakdown",
        }
        : {
            profile: "Legacy Technical Profile Score",
            rule: "Legacy Technical Rule Score",
            breakdown: "Legacy Technical Score Breakdown",
        };
}
