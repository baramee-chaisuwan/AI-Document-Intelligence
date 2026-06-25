import json
import google.generativeai as genai

from app.core.config import GEMINI_API_KEY
from app.services.scoring_service import calculate_skill_score

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def analyze_resume(resume_data):

    prompt = f"""
    Analyze this candidate resume.

    Return JSON only.

    Rules:
    - candidate_level = Entry-Level, Junior, Mid-Level, Senior
    - ai_score = 0-100
    - Evaluate overall resume quality
    - recommended_roles = maximum 3 items
    - strengths = maximum 3 items
    - improvement_areas = maximum 3 items
    - Keep every item short (1 sentence)

    Evaluation Guidelines:
    - Multiple internships can qualify as Junior level
    - Strong practical projects can increase candidate level
    - Data Engineering, AI, ETL, ML, LLM projects should be considered as professional-level experience
    - Do not classify every internship candidate as Entry-Level

    {{
        "candidate_level": "",
        "ai_score": 0,
        "recommended_roles": [],
        "strengths": [],
        "improvement_areas": []
    }}

    Resume Data:

    {resume_data}
    """

    try:

        response = model.generate_content(prompt)

        result = response.text

        result = result.replace(
            "```json",
            ""
        )

        result = result.replace(
            "```",
            ""
        )

        result = result.strip()

        analysis = json.loads(result)

        analysis["ai_status"] = "success"

        score_data = calculate_skill_score(resume_data)

        rule_score = score_data["skill_score"]

        experience_count = len(resume_data.get("experience", []))

        if (  analysis["candidate_level"] == "Entry-Level" 
            and experience_count >= 2 
            and rule_score >= 75 ):

            analysis["candidate_level"] = "Junior"

        ai_score = analysis.get(
            "ai_score",
            rule_score
        )

        ai_score = max(
            0,
            min(ai_score, 100)
        )

        final_score = round(
            (rule_score * 0.7)
            +
            (ai_score * 0.3)
        )

        analysis["rule_score"] = rule_score

        analysis["ai_score"] = ai_score

        analysis["skill_score"] = final_score

        analysis["score_breakdown"] = (score_data["score_breakdown"])

        return analysis

    except Exception as e:

        print("ANALYSIS ERROR:", e)

        if "429" in str(e):
            ai_status = "rate_limit"

        elif "API key" in str(e):
            ai_status = "invalid_key"

        else:
            ai_status = "failed"

        score_data = calculate_skill_score(
            resume_data
        )

        return {
            "candidate_level": "Unknown",
            "rule_score": score_data["skill_score"],
            "ai_score": 0,
            "skill_score": score_data["skill_score"],
            "score_breakdown": score_data["score_breakdown"],
            "ai_status": ai_status,
            "recommended_roles": [],
            "strengths": [],
            "improvement_areas": []
        }