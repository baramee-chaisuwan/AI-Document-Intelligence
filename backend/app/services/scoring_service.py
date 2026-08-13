import re


PROFILE_SCORE_VERSION = "profile_v2"

PROFILE_CATEGORY_MAXIMUMS = {
    "professional_experience": 25,
    "achievements": 20,
    "competencies": 20,
    "certifications": 10,
    "education": 10,
    "leadership": 10,
    "evidence_quality": 5,
}

AI_KEYWORDS = [
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "large language model",
    "llm",
    "llm integration",
    "prompt engineering",
    "rag",
    "retrieval augmented generation",
    "embedding",
    "embeddings",
    "vector database",
    "fine tuning",
    "fine-tuning",
    "nlp",
    "natural language processing",
    "computer vision",
    "ocr",
    "object detection",
    "image classification",
    "tensorflow",
    "keras",
    "pytorch",
    "scikit",
    "scikit-learn",
    "xgboost",
    "lightgbm",
    "cnn",
    "rnn",
    "lstm",
    "transformer",
    "bert",
    "yolo",
    "autoencoder",
    "autoencoders",
    "tf-idf",
    "word2vec",
    "sentence transformer",
    "sentence-transformers",
    "smote",
    "gridsearchcv"
]


BACKEND_KEYWORDS = [
    "fastapi",
    "django",
    "flask",
    "spring",
    "spring boot",
    "express",
    "express.js",
    "nestjs",
    ".net",
    "asp.net",
    "laravel",
    "sqlalchemy",
    "typeorm",
    "hibernate",
    "microservice",
    "microservices",
    "grpc",
    "graphql"
]


DATABASE_KEYWORDS = [
    "sql",
    "postgres",
    "postgresql",
    "mysql",
    "mariadb",
    "sqlite",
    "sql server",
    "oracle",
    "mongodb",
    "redis"
]


DEVOPS_KEYWORDS = [
    "docker",
    "docker compose",
    "docker-compose",
    "kubernetes",
    "helm",
    "terraform",
    "ansible",
    "jenkins",
    "github actions",
    "gitlab ci",
    "azure devops"
]


DATA_ENGINEERING_KEYWORDS = [
    "etl",
    "elt",
    "data pipeline",
    "data pipelines",
    "ssis",
    "data engineering",
    "data warehouse",
    "data mart",
    "airflow",
    "prefect",
    "dbt",
    "spark",
    "hadoop",
    "kafka",
    "hive",
    "snowflake",
    "bigquery",
    "redshift"
]


CLOUD_KEYWORDS = [
    "aws",
    "amazon web services",
    "azure",
    "gcp",
    "google cloud",
    "render",
    "railway",
    "vercel"
]


def normalize_text(
    value
):

    return str(
        value or ""
    ).strip().lower()


def normalize_list(
    value
):

    if not isinstance(
        value,
        list
    ):
        return []

    result = []

    for item in value:

        text = normalize_text(
            item
        )

        if text:
            result.append(
                text
            )

    return result

def keyword_exists(
    search_text,
    keyword
):

    keyword = normalize_text(
        keyword
    )

    if not keyword:
        return False

    pattern = (
        r"(?<![a-z0-9])"
        + re.escape(keyword)
        + r"(?![a-z0-9])"
    )

    return (
        re.search(
            pattern,
            search_text,
            re.IGNORECASE
        )
        is not None
    )


def has_keyword(
    search_text,
    keywords
):

    for keyword in keywords:

        if keyword_exists(
            search_text,
            keyword
        ):
            return True

    return False

def has_meaningful_experience(
    experience
):

    if not isinstance(
        experience,
        dict
    ):
        return False

    title = normalize_text(
        experience.get(
            "title"
        )
    )

    company = normalize_text(
        experience.get(
            "company"
        )
    )

    description = normalize_list(
        experience.get(
            "description"
        )
    )

    return bool(
        title
        or company
        or description
    )

def is_internship(
    experience
):

    title = normalize_text(
        experience.get(
            "title"
        )
    )

    company = normalize_text(
        experience.get(
            "company"
        )
    )

    internship_keywords = [
        "intern",
        "internship",
        "trainee",
        "co-op",
        "coop"
    ]

    combined_text = (
        title
        + " "
        + company
    )

    return has_keyword(
        combined_text,
        internship_keywords
    )

def has_meaningful_project(
    project
):

    if not isinstance(
        project,
        dict
    ):
        return False

    name = normalize_text(
        project.get(
            "name"
        )
    )

    description = normalize_list(
        project.get(
            "description"
        )
    )

    technologies = normalize_list(
        project.get(
            "technologies"
        )
    )

    return bool(
        name
        or description
        or technologies
    )

def calculate_legacy_technical_score(
    resume_data
):

    if not isinstance(
        resume_data,
        dict
    ):

        return {
            "skill_score": 0,
            "score_breakdown": {}
        }

    experience = resume_data.get(
        "experience",
        []
    )

    projects = resume_data.get(
        "projects",
        []
    )

    if not isinstance(
        experience,
        list
    ):
        experience = []


    if not isinstance(
        projects,
        list
    ):
        projects = []


    search_pool = []


    search_pool.extend(
        normalize_list(
            resume_data.get(
                "skills",
                []
            )
        )
    )

    for exp in experience:

        if not isinstance(
            exp,
            dict
        ):
            continue

        search_pool.append(
            normalize_text(
                exp.get(
                    "title"
                )
            )
        )

        search_pool.append(
            normalize_text(
                exp.get(
                    "company"
                )
            )
        )

        search_pool.extend(
            normalize_list(
                exp.get(
                    "description",
                    []
                )
            )
        )

    for project in projects:

        if not isinstance(
            project,
            dict
        ):
            continue

        search_pool.append(
            normalize_text(
                project.get(
                    "name"
                )
            )
        )

        search_pool.extend(
            normalize_list(
                project.get(
                    "description",
                    []
                )
            )
        )

        search_pool.extend(
            normalize_list(
                project.get(
                    "technologies",
                    []
                )
            )
        )


    search_text = " ".join(
        item
        for item in search_pool
        if item
    )


    breakdown = {}


    core = 0


    if has_keyword(
        search_text,
        ["python"]
    ):

        core += 8
        breakdown["python"] = 8

    else:

        breakdown["python"] = 0


    if has_keyword(
        search_text,
        DATABASE_KEYWORDS
    ):

        core += 8
        breakdown["sql"] = 8

    else:

        breakdown["sql"] = 0


    if has_keyword(
        search_text,
        BACKEND_KEYWORDS
    ):

        core += 7
        breakdown["backend"] = 7

    else:

        breakdown["backend"] = 0


    if has_keyword(
        search_text,
        DEVOPS_KEYWORDS
    ):

        core += 7
        breakdown["devops"] = 7

    else:

        breakdown["devops"] = 0


    domain = 0


    if has_keyword(
        search_text,
        AI_KEYWORDS
    ):

        domain += 8
        breakdown["ai_domain"] = 8

    else:

        breakdown["ai_domain"] = 0


    if has_keyword(
        search_text,
        DATA_ENGINEERING_KEYWORDS
    ):

        domain += 7
        breakdown["data_domain"] = 7

    else:

        breakdown["data_domain"] = 0


    if has_keyword(
        search_text,
        BACKEND_KEYWORDS
    ):

        domain += 5
        breakdown["backend_domain"] = 5

    else:

        breakdown["backend_domain"] = 0


    exp_score = 0


    for exp in experience:

        if not has_meaningful_experience(
            exp
        ):
            continue


        description = normalize_list(
            exp.get(
                "description",
                []
            )
        )


        if is_internship(
            exp
        ):

            exp_score += 4
            exp_score += min(
                len(description),
                3
            )

        else:

            exp_score += 8
            exp_score += min(
                len(description),
                5
            )


    exp_score = min(
        exp_score,
        20
    )

    breakdown["experience"] = (
        exp_score
    )


    project_score = 0


    for project in projects:

        if not has_meaningful_project(
            project
        ):
            continue


        description_list = normalize_list(
            project.get(
                "description",
                []
            )
        )

        technology_list = normalize_list(
            project.get(
                "technologies",
                []
            )
        )


        project_text = " ".join(
            technology_list
            + description_list
        )


        score = 2


        if has_keyword(
            project_text,
            AI_KEYWORDS
        ):

            score += 2


        if (
            has_keyword(
                project_text,
                BACKEND_KEYWORDS
            )
            or has_keyword(
                project_text,
                DATABASE_KEYWORDS
            )
            or has_keyword(
                project_text,
                DEVOPS_KEYWORDS
            )
            or has_keyword(
                project_text,
                CLOUD_KEYWORDS
            )
        ):

            score += 2


        if len(
            description_list
        ) >= 3:

            score += 1


        project_score += score


    project_score = min(
        project_score,
        20
    )

    breakdown["projects"] = (
        project_score
    )


    signal = 0


    if has_keyword(
        search_text,
        [
            "git",
            "github"
        ]
    ):

        signal += 2


    if has_keyword(
        search_text,
        [
            "github actions",
            "gitlab ci",
            "azure devops",
            "ci/cd",
            "continuous integration",
            "continuous deployment"
        ]
    ):

        signal += 3


    if has_keyword(
        search_text,
        [
            "pytest",
            "testing",
            "unit test",
            "unit tests",
            "integration test",
            "integration tests"
        ]
    ):

        signal += 2


    if has_keyword(
        search_text,
        [
            "docker",
            "docker compose",
            "docker-compose"
        ]
    ):

        signal += 3


    signal = min(
        signal,
        10
    )

    breakdown[
        "engineering_signal"
    ] = signal


    total = (
        core
        + domain
        + exp_score
        + project_score
        + signal
    )


    total = min(
        round(total),
        100
    )


    return {
        "skill_score": total,
        "score_breakdown": breakdown
    }


def calculate_skill_score(
    resume_data
):
    """Calculate the domain-neutral deterministic profile_v2 score."""

    if not isinstance(resume_data, dict):
        return _profile_score_result({})

    experience = _dictionary_list(
        resume_data.get("experience")
    )
    responsibilities = _unique_evidence(
        resume_data.get("responsibilities")
    )
    achievements = _unique_evidence(
        resume_data.get("achievements")
    )
    skills = _unique_evidence(
        resume_data.get("skills")
    )
    tools = _unique_evidence(
        resume_data.get("tools")
    )
    domain_expertise = _unique_evidence(
        resume_data.get("domain_expertise")
    )
    certifications = _unique_evidence(
        resume_data.get("certifications")
    )
    education = _dictionary_list(
        resume_data.get("education")
    )
    leadership = _unique_evidence(
        resume_data.get("leadership_experience")
    )

    meaningful_experience = [
        item
        for item in experience
        if has_meaningful_experience(item)
    ]
    description_count = sum(
        len(normalize_list(item.get("description")))
        for item in meaningful_experience
    )
    date_evidence_count = sum(
        bool(normalize_text(item.get(field)))
        for item in meaningful_experience
        for field in ("start_date", "end_date")
    )

    professional_experience = min(
        len(meaningful_experience) * 5,
        10,
    )
    professional_experience += min(
        description_count,
        5,
    )
    professional_experience += min(
        len(responsibilities) * 2,
        5,
    )
    professional_experience += min(
        date_evidence_count,
        5,
    )

    achievement_score = min(
        len(achievements) * 4,
        16,
    )
    if any(_contains_quantified_evidence(item) for item in achievements):
        achievement_score += 4
    achievement_score = min(achievement_score, 20)

    competencies = min(
        len(skills) * 2
        + len(domain_expertise) * 2
        + len(tools),
        20,
    )
    certification_score = min(
        len(certifications) * 5,
        10,
    )
    education_score = min(
        sum(
            5
            for item in education
            if normalize_text(item.get("institution"))
            or normalize_text(item.get("degree"))
        ),
        10,
    )
    leadership_score = min(
        len(leadership) * 5,
        10,
    )

    evidence_signals = (
        bool(meaningful_experience and description_count),
        bool(achievements),
        bool(skills or tools or domain_expertise),
        bool(certifications or education),
        bool(leadership or responsibilities),
    )
    evidence_quality = sum(evidence_signals)

    return _profile_score_result({
        "professional_experience": professional_experience,
        "achievements": achievement_score,
        "competencies": competencies,
        "certifications": certification_score,
        "education": education_score,
        "leadership": leadership_score,
        "evidence_quality": evidence_quality,
    })


def _profile_score_result(categories):
    breakdown = {
        "score_version": PROFILE_SCORE_VERSION,
        **{
            category: min(
                max(int(categories.get(category, 0)), 0),
                maximum,
            )
            for category, maximum
            in PROFILE_CATEGORY_MAXIMUMS.items()
        },
    }
    total = sum(
        breakdown[category]
        for category in PROFILE_CATEGORY_MAXIMUMS
    )

    return {
        "skill_score": min(total, 100),
        "score_breakdown": breakdown,
    }


def _dictionary_list(value):
    if not isinstance(value, list):
        return []

    return [item for item in value if isinstance(item, dict)]


def _unique_evidence(value):
    if not isinstance(value, list):
        return []

    result = []
    seen = set()

    for item in value:
        text = " ".join(str(item or "").split())
        key = text.casefold()

        if not text or key in seen:
            continue

        seen.add(key)
        result.append(text)

    return result


def _contains_quantified_evidence(value):
    text = str(value or "")
    patterns = (
        r"\b\d+(?:\.\d+)?\s*%",
        r"(?:\$|USD|EUR|GBP)\s*\d",
        r"\b\d+(?:\.\d+)?\s*(?:million|billion)\b",
    )

    return any(
        re.search(pattern, text, re.IGNORECASE)
        for pattern in patterns
    )
