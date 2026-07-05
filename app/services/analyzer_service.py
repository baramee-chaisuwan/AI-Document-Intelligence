import json
import re
from datetime import datetime
import google.generativeai as genai

from app.core.config import GEMINI_API_KEY
from app.services.scoring_service import calculate_skill_score

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

RULE_WEIGHT = 0.8   
AI_WEIGHT = 0.2

ALLOWED_ROLES = [
    "Data Engineer",
    "AI/ML Engineer",
    "Backend Developer",
    "Software Engineer",
    "Machine Learning Engineer"
]


def safe_get(data, key):
    return data.get(key, []) if isinstance(data, dict) else []


def is_intern(exp):
    title = exp.get("title", "").lower()
    company = exp.get("company", "").lower()

    return (
        "intern" in title or
        "intern" in company or
        "trainee" in title or
        "trainee" in company
    )


def analyze_resume(resume_data):

    prompt = f"""
You are a senior recruiter at Google / Meta / Amazon.

Return ONLY valid JSON.

STRICT RULES:
- MUST choose roles ONLY from this list:
  {ALLOWED_ROLES}

- DO NOT include "Intern" in any form
- NEVER create custom job titles
- Be conservative and realistic
- Avoid over-claiming seniority

Schema:
{{
    "candidate_level": "",
    "ai_score": 0,
    "recommended_roles": [],
    "strengths": [],
    "improvement_areas": []
}}

Resume:
{json.dumps(resume_data, ensure_ascii=False)}
"""

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()

        match = re.search(r"\{.*\}", text, re.DOTALL)
        analysis = json.loads(match.group()) if match else {}

        analysis.setdefault("candidate_level", "Entry-Level")
        analysis.setdefault("ai_score", 0)
        analysis.setdefault("recommended_roles", [])
        analysis.setdefault("strengths", [])
        analysis.setdefault("improvement_areas", [])
        analysis["ai_status"] = "success"

        score_data = calculate_skill_score(resume_data)
        rule_score = score_data["skill_score"]

        try:
            ai_score = float(analysis.get("ai_score", rule_score))
        except:
            ai_score = rule_score

        ai_score = max(0, min(ai_score, 100))

        skill_score = round(
            (rule_score * RULE_WEIGHT) +
            (ai_score * AI_WEIGHT)
        )

        experiences = safe_get(resume_data, "experience")
        projects = safe_get(resume_data, "projects")

        internships = 0
        experience_months = 0

        for exp in experiences:
            if is_intern(exp):
                internships += 1
                continue

        experience_years = experience_months / 12

        if experience_years >= 5:
            level = "Senior"
        elif experience_years >= 2:
            level = "Mid-Level"
        elif internships >= 1:
            level = "Junior"
        else:
            level = "Entry-Level"

        clean_roles = []

        for role in analysis.get("recommended_roles", []):

            role = role.strip()

            if "intern" in role.lower():
                continue

            if any(allowed in role for allowed in ALLOWED_ROLES):
                clean_roles.append(role)

        if not clean_roles:
            clean_roles = ALLOWED_ROLES[:3]

        analysis["candidate_level"] = level
        analysis["rule_score"] = rule_score
        analysis["ai_score"] = ai_score
        analysis["skill_score"] = skill_score
        analysis["score_breakdown"] = score_data.get("score_breakdown", {})
        analysis["project_count"] = len(projects)
        analysis["recommended_roles"] = clean_roles

        return analysis

    except Exception as e:
        print("ANALYSIS ERROR:", e)

        score_data = calculate_skill_score(resume_data)

        return {
            "candidate_level": "Entry-Level",
            "rule_score": score_data["skill_score"],
            "ai_score": 0,
            "skill_score": score_data["skill_score"],
            "score_breakdown": score_data.get("score_breakdown", {}),
            "project_count": 0,
            "ai_status": "fallback",
            "recommended_roles": [],
            "strengths": [],
            "improvement_areas": []
        }