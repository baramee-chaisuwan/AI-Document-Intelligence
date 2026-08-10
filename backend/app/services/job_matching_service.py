import math
import re

from sqlalchemy.orm import Session

from app.core.exceptions import (
    ConflictError,
    NotFoundError
)
from app.models.job_model import (
    JobCandidateMatchResponse,
    JobMatchScoreBreakdown
)
from app.rag.embedding_service import (
    normalize_embedding
)
from app.repositories import (
    job_match_repository,
    job_repository
)
from app.repositories.job_match_repository import (
    CandidateMatchData
)


SEMANTIC_WEIGHTS = (0.5, 0.3, 0.2)
SEMANTIC_SCORE_WEIGHT = 0.55
REQUIRED_SKILL_SCORE_WEIGHT = 0.35
PREFERRED_SKILL_SCORE_WEIGHT = 0.10
SKILL_BOUNDARY_CHARACTERS = r"\w+#"


def match_job_candidates(
    db: Session,
    job_id: int
) -> list[JobCandidateMatchResponse]:

    job = job_repository.get_job_by_id(
        db,
        job_id
    )

    if not job:
        raise NotFoundError("Job not found")

    if job.embedding is None:
        raise ConflictError(
            "Job embedding is unavailable"
        )

    try:
        job_embedding = normalize_embedding(
            job.embedding
        )

    except ValueError as error:
        raise ConflictError(
            "Job embedding is unavailable"
        ) from error

    candidate_data = (
        job_match_repository
        .get_candidate_match_data(
            db,
            job_embedding
        )
    )

    return rank_candidates(
        candidate_data,
        job.extracted_requirements
    )


def rank_candidates(
    candidate_data: list[CandidateMatchData],
    extracted_requirements
) -> list[JobCandidateMatchResponse]:

    requirements = (
        extracted_requirements
        if isinstance(
            extracted_requirements,
            dict
        )
        else {}
    )
    required_skills = normalize_skills(
        requirements.get("required_skills")
    )
    preferred_skills = normalize_skills(
        requirements.get("preferred_skills")
    )

    results = []

    for candidate in candidate_data:
        semantic_score = calculate_semantic_score(
            candidate.cosine_distances
        )

        if semantic_score is None:
            continue

        (
            required_skill_score,
            matched_required,
            missing_required
        ) = calculate_skill_coverage(
            required_skills,
            candidate.resume_text
        )
        (
            preferred_skill_score,
            matched_preferred,
            _
        ) = calculate_skill_coverage(
            preferred_skills,
            candidate.resume_text
        )

        final_score = clamp_score(
            semantic_score
            * SEMANTIC_SCORE_WEIGHT
            + required_skill_score
            * REQUIRED_SKILL_SCORE_WEIGHT
            + preferred_skill_score
            * PREFERRED_SKILL_SCORE_WEIGHT
        )

        results.append(
            JobCandidateMatchResponse(
                candidate_id=(
                    candidate.candidate_id
                ),
                candidate_name=(
                    candidate.candidate_name
                ),
                match_score=round(
                    final_score,
                    1
                ),
                score_breakdown=(
                    JobMatchScoreBreakdown(
                        semantic_score=round(
                            semantic_score,
                            1
                        ),
                        required_skill_score=(
                            round(
                                required_skill_score,
                                1
                            )
                        ),
                        preferred_skill_score=(
                            round(
                                preferred_skill_score,
                                1
                            )
                        )
                    )
                ),
                matched_skills=(
                    deduplicate_skills(
                        matched_required
                        + matched_preferred
                    )
                ),
                missing_skills=(
                    missing_required
                )
            )
        )

    return sorted(
        results,
        key=lambda result: (
            -result.match_score,
            result.candidate_id
        )
    )


def calculate_semantic_score(
    cosine_distances
) -> float | None:

    weighted_similarities = []

    for distance, weight in zip(
        list(cosine_distances or [])[:3],
        SEMANTIC_WEIGHTS
    ):
        if (
            isinstance(distance, bool)
            or not isinstance(
                distance,
                (int, float)
            )
            or not math.isfinite(float(distance))
        ):
            continue

        weighted_similarities.append(
            (
                1.0 - float(distance),
                weight
            )
        )

    if not weighted_similarities:
        return None

    weight_total = sum(
        weight
        for _, weight in weighted_similarities
    )
    weighted_similarity = sum(
        similarity * weight
        for similarity, weight
        in weighted_similarities
    ) / weight_total

    return clamp_score(
        weighted_similarity * 100.0
    )


def calculate_skill_coverage(
    skills: list[str],
    resume_text: str
) -> tuple[float, list[str], list[str]]:

    if not skills:
        return 100.0, [], []

    evidence = normalize_text(resume_text)
    matched = []
    missing = []

    for skill in skills:
        if skill_is_present(skill, evidence):
            matched.append(skill)
        else:
            missing.append(skill)

    score = (
        len(matched)
        / len(skills)
        * 100.0
    )

    return clamp_score(score), matched, missing


def normalize_skills(value) -> list[str]:

    if not isinstance(value, list):
        return []

    skills = []

    for item in value:
        if not isinstance(item, str):
            continue

        normalized = " ".join(item.split())

        if normalized:
            skills.append(normalized)

    return deduplicate_skills(skills)


def deduplicate_skills(
    skills: list[str]
) -> list[str]:

    result = []
    seen = set()

    for skill in skills:
        comparison_key = skill.casefold()

        if comparison_key in seen:
            continue

        seen.add(comparison_key)
        result.append(skill)

    return result


def normalize_text(value) -> str:

    if not isinstance(value, str):
        return ""

    return " ".join(
        value.casefold().split()
    )


def skill_is_present(
    skill: str,
    evidence: str
) -> bool:

    normalized_skill = normalize_text(skill)
    normalized_evidence = normalize_text(
        evidence
    )

    if (
        not normalized_skill
        or not normalized_evidence
    ):
        return False

    pattern = (
        f"(?<![{SKILL_BOUNDARY_CHARACTERS}])"
        f"{re.escape(normalized_skill)}"
        f"(?![{SKILL_BOUNDARY_CHARACTERS}])"
    )

    return re.search(
        pattern,
        normalized_evidence
    ) is not None


def clamp_score(value: float) -> float:

    return max(
        0.0,
        min(100.0, float(value))
    )
