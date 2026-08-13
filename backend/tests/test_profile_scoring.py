import copy
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.repositories import candidate_repository
from app.models.search_model import SearchResponse
from app.services import analyzer_service, search_service
from app.services.scoring_service import (
    PROFILE_SCORE_VERSION,
    calculate_legacy_technical_score,
    calculate_skill_score,
)
from tests.fixtures.cross_domain_resumes import (
    CROSS_DOMAIN_RESUMES,
    SENIOR_HR_RESUME,
)


@pytest.mark.parametrize(
    "resume",
    [*CROSS_DOMAIN_RESUMES.values(), SENIOR_HR_RESUME],
)
def test_universal_profile_score_is_bounded_versioned_and_deterministic(resume):
    first = calculate_skill_score(copy.deepcopy(resume))
    second = calculate_skill_score(copy.deepcopy(resume))

    assert first == second
    assert 0 <= first["skill_score"] <= 100
    assert first["score_breakdown"]["score_version"] == PROFILE_SCORE_VERSION
    assert first["skill_score"] == sum(
        value
        for key, value in first["score_breakdown"].items()
        if key != "score_version"
    )


def test_strong_hr_profile_is_not_penalized_for_missing_software_keywords():
    profile = calculate_skill_score(SENIOR_HR_RESUME)
    legacy = calculate_legacy_technical_score(SENIOR_HR_RESUME)

    assert profile["skill_score"] >= 70
    assert profile["skill_score"] > legacy["skill_score"] + 30


@pytest.mark.parametrize(
    "domain",
    [
        "ai_engineer",
        "network_engineer",
        "project_manager",
        "marketing_manager",
        "accountant",
    ],
)
def test_cross_domain_profiles_receive_evidence_based_scores(domain):
    result = calculate_skill_score(CROSS_DOMAIN_RESUMES[domain])

    assert result["skill_score"] >= 40
    assert result["score_breakdown"]["professional_experience"] > 0
    assert result["score_breakdown"]["competencies"] > 0


def test_profile_score_and_ai_analysis_keep_existing_composition(monkeypatch):
    model = Mock()
    model.generate_content.return_value = Mock(text=json.dumps({
        "ai_score": 92,
        "recommended_roles": ["Senior Human Resources Manager"],
        "strengths": ["Reduced time to hire by 35%"],
        "improvement_areas": [],
    }))
    monkeypatch.setattr(analyzer_service, "model", model)

    result = analyzer_service.analyze_resume(SENIOR_HR_RESUME)

    assert result["rule_score"] == 74
    assert result["ai_score"] == 92
    assert result["skill_score"] == round(74 * 0.8 + 92 * 0.2)
    assert result["score_breakdown"]["score_version"] == PROFILE_SCORE_VERSION


def test_certifications_achievements_and_leadership_contribute_neutrally():
    complete = calculate_skill_score(SENIOR_HR_RESUME)["score_breakdown"]
    sparse = copy.deepcopy(SENIOR_HR_RESUME)
    sparse["certifications"] = []
    sparse["achievements"] = []
    sparse["leadership_experience"] = []
    reduced = calculate_skill_score(sparse)["score_breakdown"]

    assert complete["certifications"] > reduced["certifications"]
    assert complete["achievements"] > reduced["achievements"]
    assert complete["leadership"] > reduced["leadership"]


def test_missing_evidence_does_not_create_points():
    result = calculate_skill_score({})

    assert result["skill_score"] == 0
    assert all(
        value == 0
        for key, value in result["score_breakdown"].items()
        if key != "score_version"
    )


def test_legacy_technical_formula_remains_available_and_unchanged():
    resume = {
        "skills": ["Python", "FastAPI", "Docker", "Machine Learning", "LLM"],
        "experience": [{
            "title": "AI Engineer Intern",
            "description": ["Developed AI applications", "Built REST API using FastAPI"],
        }],
        "projects": [{
            "name": "AI Document Intelligence ATS Resume Screening System",
            "description": [
                "Built AI-powered ATS system",
                "Integrated Google Gemini",
                "Implemented hybrid candidate scoring",
            ],
            "technologies": ["FastAPI", "PostgreSQL", "Docker", "LLM"],
        }],
    }

    assert calculate_legacy_technical_score(resume)["skill_score"] == 59


def test_dashboard_distribution_remains_ai_analysis_only():
    db = Mock()
    query = Mock()
    db.query.return_value = query
    query.all.return_value = [SimpleNamespace(ai_score=75)]

    result = candidate_repository.get_score_distribution(db)

    selected_field = db.query.call_args.args[0]
    assert str(selected_field) == "Candidate.ai_score"
    assert result == [{"score_range": "61-80", "count": 1}]


def test_search_preserves_score_version_for_compatible_labels(monkeypatch):
    monkeypatch.setattr(
        search_service,
        "search_documents",
        lambda _query: {
            "metadatas": [[{"candidate_id": "7"}]],
            "distances": [[0.12]],
        },
    )
    candidate = SimpleNamespace(
        id=7,
        name="Taylor Morgan",
        summary="Senior HR leader",
        candidate_level="Senior",
        skill_score=78,
        rule_score=74,
        ai_score=92,
        score_breakdown={"score_version": PROFILE_SCORE_VERSION},
    )
    db = Mock()
    db.query.return_value.filter.return_value.first.return_value = candidate

    results = search_service.semantic_search("HR leader", db)

    response = SearchResponse.model_validate({"results": results})
    assert response.results[0].score_breakdown == {
        "score_version": PROFILE_SCORE_VERSION,
    }
