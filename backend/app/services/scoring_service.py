def calculate_skill_score(resume_data):

    experience = resume_data.get("experience", [])
    projects = resume_data.get("projects", [])

    search_pool = []

    search_pool.extend(resume_data.get("skills", []))

    for exp in experience:
        search_pool.append(exp.get("title", ""))
        search_pool.extend(exp.get("description", []))

    for project in projects:
        search_pool.append(project.get("name", ""))
        search_pool.extend(project.get("description", []))
        search_pool.extend(project.get("technologies", []))

    search_text = " ".join(search_pool).lower()

    def has(*keywords):
        return any(keyword.lower() in search_text for keyword in keywords)

    breakdown = {}

    core = 0

    if has("python"):
        core += 8
        breakdown["python"] = 8
    else:
        breakdown["python"] = 0

    if has(
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
    ):
        core += 8
        breakdown["sql"] = 8
    else:
        breakdown["sql"] = 0

    if has(
        "fastapi",
        "django",
        "flask",
        "spring",
        "spring boot",
        "express",
        "nestjs",
        ".net",
        "asp.net",
        "laravel"
    ):
        core += 7
        breakdown["backend"] = 7
    else:
        breakdown["backend"] = 0

    if has(
        "docker",
        "docker compose",
        "kubernetes",
        "helm",
        "terraform",
        "ansible",
        "jenkins",
        "github actions",
        "gitlab ci",
        "azure devops"
    ):
        core += 7
        breakdown["devops"] = 7
    else:
        breakdown["devops"] = 0

    domain = 0

    if has(
        "artificial intelligence",
        "ai",
        "machine learning",
        "deep learning",
        "llm",
        "large language model",
        "llm integration",
        "prompt engineering",
        "rag",
        "embedding",
        "vector database",
        "fine tuning",
        "nlp",
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
        "smote",
        "gridsearchcv"
    ):
        domain += 8
        breakdown["ai_domain"] = 8
    else:
        breakdown["ai_domain"] = 0

    if has(
        "etl",
        "elt",
        "pipeline",
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
    ):
        domain += 7
        breakdown["data_domain"] = 7
    else:
        breakdown["data_domain"] = 0

    if has(
        "fastapi",
        "django",
        "flask",
        "spring",
        "spring boot",
        "express",
        "nestjs",
        "asp.net",
        "laravel",
        "sqlalchemy",
        "typeorm",
        "hibernate",
        "microservice",
        "grpc",
        "graphql"
    ):
        domain += 5
        breakdown["backend_domain"] = 5
    else:
        breakdown["backend_domain"] = 0

    exp_score = 0

    for exp in experience:

        title = exp.get("title", "").lower()
        desc = len(exp.get("description", []))

        if "intern" in title or "trainee" in title:
            exp_score += 4
            exp_score += min(desc, 3)
        else:
            exp_score += 10
            exp_score += min(desc, 5)

    exp_score = min(exp_score, 20)
    breakdown["experience"] = exp_score

    project_score = 0

    for p in projects:

        tech = " ".join(p.get("technologies", [])).lower()
        desc = " ".join(p.get("description", [])).lower()

        score = 2

        if any(x in tech or x in desc for x in [
            "ai",
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "llm",
            "large language model",
            "prompt engineering",
            "rag",
            "tensorflow",
            "keras",
            "pytorch",
            "scikit",
            "cnn",
            "rnn",
            "lstm",
            "transformer",
            "bert",
            "yolo",
            "autoencoder",
            "autoencoders",
            "nlp",
            "computer vision",
            "tf-idf",
            "smote"
        ]):
            score += 2

        if any(x in tech or x in desc for x in [
            "fastapi",
            "django",
            "flask",
            "spring",
            "express",
            "docker",
            "kubernetes",
            "postgres",
            "postgresql",
            "mysql",
            "mongodb",
            "sqlalchemy",
            "typeorm",
            "hibernate",
            "aws",
            "azure",
            "gcp",
            "render",
            "railway",
            "vercel"
        ]):
            score += 2

        if len(p.get("description", [])) >= 3:
            score += 1

        project_score += score

    project_score = min(project_score, 20)
    breakdown["projects"] = project_score

    signal = 0

    if has("git", "github"):
        signal += 2

    if has(
        "github actions",
        "gitlab ci",
        "azure devops",
        "ci/cd"
    ):
        signal += 3

    if has("pytest", "testing", "unit test"):
        signal += 2

    if has("docker"):
        signal += 3

    signal = min(signal, 10)
    breakdown["engineering_signal"] = signal

    total = (
        core +
        domain +
        exp_score +
        project_score +
        signal
    )

    total = min(round(total), 100)

    return {
        "skill_score": total,
        "score_breakdown": breakdown
    }