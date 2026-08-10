import pytest

from app.repositories.job_match_repository import (
    CandidateMatchData
)
from app.services.job_matching_service import (
    calculate_semantic_score,
    calculate_skill_coverage,
    rank_candidates,
    skill_is_present
)


def candidate_data(
    candidate_id: int,
    distances,
    resume_text: str
) -> CandidateMatchData:

    return CandidateMatchData(
        candidate_id=candidate_id,
        candidate_name=f"Candidate {candidate_id}",
        cosine_distances=distances,
        resume_text=resume_text
    )


def test_semantic_score_uses_top_three_weights():

    score = calculate_semantic_score(
        [0.1, 0.3, 0.5, 0.0]
    )

    assert score == pytest.approx(76.0)


def test_semantic_score_renormalizes_fewer_chunks():

    score = calculate_semantic_score(
        [0.2, 0.4]
    )

    assert score == pytest.approx(72.5)


def test_invalid_distance_keeps_original_rank_weights():

    score = calculate_semantic_score(
        [0.1, float("nan"), 0.5]
    )

    assert score == pytest.approx(
        78.5714285714
    )


@pytest.mark.parametrize(
    ("distance", "expected"),
    [
        (-0.5, 100.0),
        (2.0, 0.0)
    ]
)
def test_semantic_score_is_clamped(
    distance,
    expected
):

    assert calculate_semantic_score(
        [distance]
    ) == expected


def test_required_skill_coverage_and_missing_skills():

    score, matched, missing = (
        calculate_skill_coverage(
            ["Python", "PostgreSQL"],
            "Built APIs using python."
        )
    )

    assert score == 50.0
    assert matched == ["Python"]
    assert missing == ["PostgreSQL"]


def test_empty_skill_category_scores_one_hundred():

    assert calculate_skill_coverage(
        [],
        ""
    ) == (100.0, [], [])


def test_skill_matching_is_case_insensitive():

    assert skill_is_present(
        "FastAPI",
        "built services with FASTAPI"
    ) is True


def test_skill_matching_avoids_loose_substrings():

    assert skill_is_present(
        "R",
        "Experienced recruiter and researcher"
    ) is False
    assert skill_is_present(
        "C",
        "Production C++ development"
    ) is False


def test_final_score_and_explainability_follow_formula():

    results = rank_candidates(
        [
            candidate_data(
                1,
                [0.2],
                "Python and FastAPI"
            )
        ],
        {
            "required_skills": [
                "Python",
                "PostgreSQL"
            ],
            "preferred_skills": [
                "FastAPI",
                "Python"
            ]
        }
    )

    assert len(results) == 1
    result = results[0]
    assert result.match_score == 71.5
    assert result.score_breakdown.semantic_score == 80.0
    assert (
        result.score_breakdown.required_skill_score
        == 50.0
    )
    assert (
        result.score_breakdown.preferred_skill_score
        == 100.0
    )
    assert result.matched_skills == [
        "Python",
        "FastAPI"
    ]
    assert result.missing_skills == [
        "PostgreSQL"
    ]


def test_ranking_uses_candidate_id_as_tie_breaker():

    results = rank_candidates(
        [
            candidate_data(2, [0.2], "Python"),
            candidate_data(1, [0.2], "Python")
        ],
        {
            "required_skills": ["Python"],
            "preferred_skills": []
        }
    )

    assert [
        result.candidate_id
        for result in results
    ] == [1, 2]


def test_candidate_without_usable_chunks_is_excluded():

    results = rank_candidates(
        [
            candidate_data(
                1,
                [],
                "Python"
            ),
            candidate_data(
                2,
                [float("nan")],
                "Python"
            )
        ],
        {
            "required_skills": ["Python"],
            "preferred_skills": []
        }
    )

    assert results == []
