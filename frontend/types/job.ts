export interface JobRequirements {
    required_skills: string[];
    preferred_skills: string[];
    experience_requirements: string[];
    responsibilities: string[];
}


export interface Job {
    id: number;
    title: string;
    description: string;
    extracted_requirements: JobRequirements;
    created_by: number;
    created_at: string;
}


export interface CreateJobPayload {
    title: string;
    description: string;
}


export interface JobMatchScoreBreakdown {
    semantic_score: number;
    required_skill_score: number;
    preferred_skill_score: number;
}


export interface JobMatchResult {
    candidate_id: number;
    candidate_name: string;
    match_score: number;
    score_breakdown: JobMatchScoreBreakdown;
    matched_skills: string[];
    missing_skills: string[];
}
