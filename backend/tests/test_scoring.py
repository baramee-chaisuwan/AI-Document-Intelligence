from app.services.scoring_service import (
    calculate_skill_score
)

def test_calculate_skill_score_ai_engineer():

    resume_data = {
        "skills": [
            "Python",
            "FastAPI",
            "Docker",
            "Machine Learning",
            "LLM"
        ],
        "experience": [
            {
                "title": "AI Engineer Intern",
                "description": [
                    "Developed AI applications",
                    "Built REST API using FastAPI"
                ]
            }
        ],
        "projects": [
            {
                "name": (
                    "AI Document Intelligence "
                    "ATS Resume Screening System"
                ),
                "description": [
                    "Built AI-powered ATS system",
                    "Integrated Google Gemini",
                    "Implemented hybrid candidate scoring"
                ],
                "technologies": [
                    "FastAPI",
                    "PostgreSQL",
                    "Docker",
                    "LLM"
                ]
            }
        ]
    }


    result = calculate_skill_score(
        resume_data
    )


    assert result["skill_score"] >= 0
    assert result["skill_score"] <= 100

    assert "score_breakdown" in result


    breakdown = result["score_breakdown"]


    assert breakdown["python"] == 8
    assert breakdown["sql"] == 8
    assert breakdown["backend"] == 7
    assert breakdown["devops"] == 7
    assert breakdown["ai_domain"] == 8
    assert breakdown["backend_domain"] == 5

    assert breakdown["experience"] > 0
    assert breakdown["projects"] > 0

    assert result["skill_score"] == sum(
        breakdown.values()
    )