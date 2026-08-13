import json
from unittest.mock import Mock

import pytest

from app.rag.prompt import recommendation_prompt, resume_summary_prompt
from app.repositories.job_match_repository import CandidateMatchData
from app.services import analyzer_service, extraction_service, gemini_service
from app.services.job_matching_service import rank_candidates
from app.services.scoring_service import calculate_skill_score
from tests.fixtures.cross_domain_resumes import (
    CROSS_DOMAIN_JOB_CASES,
    CROSS_DOMAIN_RESUMES,
)


@pytest.mark.parametrize("domain", CROSS_DOMAIN_RESUMES)
def test_cross_domain_evidence_survives_normalization(domain):
    source = CROSS_DOMAIN_RESUMES[domain]

    normalized = extraction_service.normalize_resume_data(source)

    for field in (
        "skills",
        "tools",
        "certifications",
        "achievements",
        "responsibilities",
        "domain_expertise",
        "leadership_experience",
    ):
        assert normalized[field] == source[field]


def test_ai_engineer_existing_fields_remain_compatible():
    source = CROSS_DOMAIN_RESUMES["ai_engineer"]

    normalized = extraction_service.normalize_resume_data(source)

    assert normalized["skills"] == ["Python", "Machine Learning", "RAG"]
    assert normalized["projects"] == source["projects"]
    assert normalized["languages"] == ["English"]


def test_legacy_extraction_payload_receives_safe_empty_extensions():
    normalized = extraction_service.normalize_resume_data({
        "name": "Legacy Candidate",
        "skills": ["Python"],
        "languages": [],
        "education": [],
        "experience": [],
        "projects": [],
    })

    for field in (
        "tools",
        "certifications",
        "achievements",
        "responsibilities",
        "domain_expertise",
        "leadership_experience",
    ):
        assert normalized[field] == []


def test_resume_extraction_prompt_is_domain_neutral(monkeypatch):
    response = Mock(text=json.dumps(CROSS_DOMAIN_RESUMES["project_manager"]))
    model = Mock()
    model.generate_content.return_value = response
    monkeypatch.setattr(extraction_service, "model", model)

    result = extraction_service.extract_resume_data("Synthetic resume evidence")

    prompt = model.generate_content.call_args.args[0]
    assert "only concrete technical skills" not in prompt
    assert "technical project" not in prompt
    assert "certifications" in prompt
    assert "measurable achievements" in prompt
    assert result["certifications"] == ["PMP"]


def test_analysis_accepts_evidence_supported_cross_domain_roles(monkeypatch):
    model = Mock()
    model.generate_content.return_value = Mock(text=json.dumps({
        "ai_score": 82,
        "recommended_roles": ["Project Manager", "Program Manager"],
        "strengths": ["Program delivery"],
        "improvement_areas": [],
    }))
    monkeypatch.setattr(analyzer_service, "model", model)
    monkeypatch.setattr(
        analyzer_service,
        "calculate_skill_score",
        lambda _resume: {"skill_score": 20, "score_breakdown": {}},
    )

    result = analyzer_service.analyze_resume(
        CROSS_DOMAIN_RESUMES["project_manager"]
    )

    prompt = model.generate_content.call_args.args[0]
    assert "technical recruiter" not in prompt
    assert "Choose recommended roles only from this list" not in prompt
    assert "Project Manager" in result["recommended_roles"]


@pytest.mark.parametrize(
    "role",
    [
        "AI Engineer",
        "Network Engineer",
        "Project Manager",
        "Marketing Manager",
        "Accountant",
        "HR Specialist",
        "Sales Manager",
    ],
)
def test_role_normalization_has_no_fixed_technical_whitelist(role):
    assert analyzer_service.clean_recommended_roles([role]) == [role]


def test_summary_and_legacy_recommendation_prompts_are_neutral(monkeypatch):
    model = Mock()
    model.generate_content.return_value = Mock(text="Evidence-based summary")
    monkeypatch.setattr(gemini_service, "get_model", lambda: model)

    gemini_service.summarize_document("Synthetic accounting resume")
    summary_prompt = model.generate_content.call_args.args[0]

    assert "MUST mention projects" not in summary_prompt
    assert "Technical skills" not in resume_summary_prompt.template
    assert "Required technical skills" not in recommendation_prompt.template
    assert "Backend, cloud, deployment" not in recommendation_prompt.template
    assert "role-specific" in recommendation_prompt.template


def test_legacy_technical_rule_score_numeric_behavior_is_unchanged():
    resume = {
        "skills": ["Python", "FastAPI", "Docker", "Machine Learning", "LLM"],
        "experience": [{
            "title": "AI Engineer Intern",
            "description": [
                "Developed AI applications",
                "Built REST API using FastAPI",
            ],
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

    assert calculate_skill_score(resume)["skill_score"] == 59


@pytest.mark.parametrize(
    ("domain", "required_skills", "matching_resume"),
    CROSS_DOMAIN_JOB_CASES,
)
def test_existing_job_matching_ranks_cross_domain_candidate_first(
    domain,
    required_skills,
    matching_resume,
):
    target = CandidateMatchData(
        candidate_id=1,
        candidate_name=domain,
        cosine_distances=[0.2],
        resume_text=matching_resume,
    )
    closer_but_unqualified = CandidateMatchData(
        candidate_id=2,
        candidate_name="Unqualified candidate",
        cosine_distances=[0.1],
        resume_text="General professional experience without the stated requirements",
    )

    ranked = rank_candidates(
        [closer_but_unqualified, target],
        {
            "required_skills": required_skills,
            "preferred_skills": [required_skills[0]],
        },
    )

    assert ranked[0].candidate_id == target.candidate_id
    assert ranked[0].missing_skills == []
    assert required_skills[0] in ranked[0].matched_skills
