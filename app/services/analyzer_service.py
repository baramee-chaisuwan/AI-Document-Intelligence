import json
import re
from datetime import datetime
import google.generativeai as genai

from app.core.config import GEMINI_API_KEY
from app.services.scoring_service import calculate_skill_score

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

RULE_WEIGHT = 0.7
AI_WEIGHT = 0.3


MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}


def parse_date(date_str):

    if not date_str:
        return None

    date_str = date_str.strip().lower()

    if date_str in ["present", "current"]:
        return datetime.now()

    try:
        month, year = date_str.split()
        return datetime(int(year), MONTHS[month], 1)
    except:
        return None


def analyze_resume(resume_data):

    prompt = f"""
You are a senior technical recruiter.

Evaluate ONLY the candidate's resume.

Return ONLY valid JSON.

Schema:

{{
    "candidate_level": "",
    "ai_score": 0,
    "recommended_roles": [],
    "strengths": [],
    "improvement_areas": []
}}

Evaluation Rules

ai_score represents employability, NOT intelligence.

Scoring Guide:

90-100
Exceptional candidate with 5+ years of strong professional experience,
leadership, production systems and measurable business impact.

80-89
Strong Junior or Mid-Level candidate with excellent internships,
multiple production-quality projects and highly competitive profile.

70-79
Good Junior candidate ready for industry.
Has internships, practical projects and relevant technical skills.

60-69
Average graduate with relevant coursework and several projects.

40-59
Limited practical experience.

0-39
Weak resume.

Seniority Rules

Entry-Level
- Student or graduate
- No internship

Junior
- Internship(s) OR strong personal projects
- Less than 2 years FULL-TIME experience

Mid-Level
- 2-5 years FULL-TIME experience

Senior
- 5+ years FULL-TIME experience

IMPORTANT

Internships are NOT full-time.

Academic projects are NOT work experience.

Competitions, hackathons and university activities are NOT work experience.

Do NOT inflate scores.

Recent graduates should rarely receive above 80.

Resume:

{json.dumps(resume_data, ensure_ascii=False)}
"""

    try:

        response = model.generate_content(prompt)

        text = response.text.strip()

        json_match = re.search(r"\{.*\}", text, re.DOTALL)

        if json_match:
            analysis = json.loads(json_match.group())
        else:
            analysis = {}

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
            rule_score * RULE_WEIGHT +
            ai_score * AI_WEIGHT
        )

        experiences = resume_data.get("experience", [])

        internships = 0
        fulltime_months = 0

        for exp in experiences:

            title = exp.get("title", "").lower()
            company = exp.get("company", "").lower()

            if "intern" in title:
                internships += 1
                continue

            if any(keyword in company for keyword in [
                "academic",
                "project",
                "university",
                "college",
                "institute"
            ]):
                continue

            if company == "":
                continue

            start = parse_date(exp.get("start_date", ""))
            end = parse_date(exp.get("end_date", ""))

            if start and end:

                months = (
                    (end.year - start.year) * 12 +
                    (end.month - start.month)
                )

                if months > 0:
                    fulltime_months += months

        fulltime_years = fulltime_months / 12

        if fulltime_years >= 5:

            level = "Senior"

        elif fulltime_years >= 2:

            level = "Mid-Level"

        elif internships >= 1 or fulltime_years > 0:

            level = "Junior"

        else:

            level = "Entry-Level"

        analysis["candidate_level"] = level
        analysis["rule_score"] = rule_score
        analysis["ai_score"] = ai_score
        analysis["skill_score"] = skill_score
        analysis["score_breakdown"] = score_data["score_breakdown"]

        return analysis

    except Exception as e:

        print("ANALYSIS ERROR:", e)

        score_data = calculate_skill_score(resume_data)

        return {
            "candidate_level": "Entry-Level",
            "rule_score": score_data["skill_score"],
            "ai_score": 0,
            "skill_score": score_data["skill_score"],
            "score_breakdown": score_data["score_breakdown"],
            "ai_status": "fallback",
            "recommended_roles": [],
            "strengths": [],
            "improvement_areas": []
        }