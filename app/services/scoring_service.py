def calculate_skill_score(resume_data):

    skills = resume_data.get("skills", [])
    experience = resume_data.get("experience", [])

    score = 0

    breakdown = {
        "python": 0,
        "sql": 0,
        "machine_learning": 0,
        "etl": 0,
        "experience": 0
    }

    skills_lower = [
        skill.lower()
        for skill in skills
    ]

    if "python" in skills_lower:
        breakdown["python"] = 15
        score += 15

    if "sql" in skills_lower:
        breakdown["sql"] = 15
        score += 15

    if (
        "machine learning" in skills_lower
        or "ml" in skills_lower
    ):
        breakdown["machine_learning"] = 15
        score += 15

    if "etl" in skills_lower:
        breakdown["etl"] = 15
        score += 15

    experience_score = min(
        len(experience) * 5,
        20
    )

    breakdown["experience"] = experience_score

    score += experience_score

    return {
        "skill_score": score,
        "score_breakdown": breakdown
    }