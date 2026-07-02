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

    # normalize
    skills_lower = [
        skill.lower().strip()
        for skill in skills
    ]

    # helper function (robust matching)
    def has_skill(keywords):
        return any(
            any(keyword in skill for keyword in keywords)
            for skill in skills_lower
        )

    python_keywords = ["python"]
    sql_keywords = ["sql", "mysql", "postgres", "postgresql"]
    ml_keywords = ["machine learning", "ml", "deep learning", "data science", "ai"]
    etl_keywords = ["etl", "airflow", "data pipeline", "data engineering"]

    if has_skill(python_keywords):
        breakdown["python"] = 15
        score += 15

    if has_skill(sql_keywords):
        breakdown["sql"] = 15
        score += 15

    if has_skill(ml_keywords):
        breakdown["machine_learning"] = 15
        score += 15

    if has_skill(etl_keywords):
        breakdown["etl"] = 15
        score += 15

    experience_score = min(len(experience) * 5, 20)
    breakdown["experience"] = experience_score
    score += experience_score

    return {
        "skill_score": score,
        "score_breakdown": breakdown
    }