import json
import re
import google.generativeai as genai
from app.core.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")


def extract_resume_data(text):
    prompt = f"""
You are a production-grade ATS Resume Parser.

Your ONLY task is to extract structured information exactly from the resume.

Never summarize.
Never rewrite.
Never hallucinate.
Never infer information that is not explicitly stated unless allowed below.

GENERAL RULES

- Return ONLY valid JSON.
- Do NOT wrap JSON in markdown.
- Do NOT include explanations.
- Preserve the original wording whenever possible.
- Preserve the original meaning.
- Do NOT omit any section found in the resume.
- If a field is missing, return "" or [].

EXPERIENCE EXTRACTION RULES

Extract EVERY work experience.

Experience includes:

- Full-time
- Part-time
- Internship
- Trainee
- Contract
- Freelance
- Research Assistant
- Teaching Assistant
- Technical Volunteer

Rules:

- Never merge different experiences.
- Never discard duplicated job titles.
- Preserve chronological order exactly as written.
- Return one object per experience.

For every experience extract:

- title
- company
- start_date
- end_date
- description

Description rules:

- Keep EVERY bullet point.
- Never summarize.
- Never rewrite.
- Preserve achievements.
- Preserve technical details.
- Preserve metrics.
- Return one bullet per array element.

PROJECT EXTRACTION RULES

Extract EVERY technical project mentioned anywhere in the resume.

A project DOES NOT need to appear under a section called "Projects".

Search the ENTIRE resume including:

- Projects
- Experience
- Education
- Activities
- Competitions
- Awards
- Leadership
- Research
- Startup
- Portfolio
- Publications
- Thesis
- Certifications
- Extracurricular Activities

Projects include but are NOT limited to:

- Academic Project
- Personal Project
- Research Project
- Internship Project
- Freelance Project
- Competition Project
- Hackathon Project
- Startup Project
- Capstone Project
- Graduation Project
- Thesis Project
- Open Source Project
- Portfolio Project
- Prototype
- MVP
- Innovation Project

Extract as a project whenever the candidate built, designed, developed, implemented, created, proposed, presented, or led any technical solution.

Examples include:

- AI application
- Machine Learning model
- Deep Learning model
- NLP model
- LLM application
- Backend system
- REST service
- Dashboard
- Website
- Mobile application
- Chatbot
- Software platform
- Desktop application
- Automation workflow
- ETL pipeline
- Data pipeline
- Data Warehouse
- Data Mart
- Database system
- Prototype
- Research prototype
- Competition submission
- Startup product
- Technical solution

If the candidate participated in a competition, startup, hackathon, innovation contest, research exhibition, or pitching event and contributed in a technical role (such as CTO, Developer, AI Engineer, Backend Developer, Data Engineer, Technical Lead, Software Engineer), extract it as a project.

If the project is mentioned under Awards, Activities, Leadership or Competitions, DO NOT ignore it.

Never skip a project because it is:

- academic
- unfinished
- experimental
- a prototype
- a competition entry
- a startup idea

If the same project appears multiple times:

- Merge all information into ONE project.

Do NOT merge different projects together.

For EVERY project extract:

- name
- description
- technologies

Description rules:

- Preserve EVERY bullet point.
- Never summarize.
- Never rewrite.
- Never remove achievements.
- Never remove technical details.
- Never remove metrics.
- Return one bullet per array element.

Technology rules inside projects:

- Extract only concrete technologies explicitly mentioned.
- If a technology is clearly stated inside the project description, include it.
- Do NOT invent technologies.
- Do NOT convert responsibilities into technologies.

TECHNOLOGY EXTRACTION RULES

Extract ALL concrete technologies explicitly mentioned.

Include ONLY real technologies such as:

- Programming Languages
- Frameworks
- Libraries
- Databases
- Cloud Platforms
- DevOps Tools
- Workflow Tools
- Deployment Platforms
- AI Models
- LLMs
- ML Frameworks
- APIs
- SDKs

Examples:

Python
C++
Java
FastAPI
Django
Flask
SQLAlchemy
Alembic
Docker
Docker Compose
Kubernetes
Git
GitHub
GitHub Actions
PostgreSQL
SQL Server
MySQL
MongoDB
SSIS
TensorFlow
PyTorch
scikit-learn
Google Gemini
OpenAI
Render
AWS
Azure
GCP
n8n
LINE Messaging API
Webhook

Do NOT extract responsibilities, methodologies, job duties, soft skills or generic concepts as technologies.

Examples of INVALID technologies:

- API
- REST API
- API Integration
- Backend Development
- Software Development
- Programming
- Development
- Technical Design
- System Design
- AI concepts
- Machine Learning concepts
- Deep Learning concepts
- CI
- UX/UI
- UX/UI Prototype
- Problem Solving
- Leadership
- Teamwork

If technologies are not explicitly listed,
infer ONLY technologies that are directly mentioned inside the project's description.

Never infer technologies from:

- Job titles
- Responsibilities
- Company names
- Generic wording

Never invent technologies.

Return only concrete software, frameworks, programming languages, databases, cloud services, libraries, APIs, SDKs and development tools.

SKILLS

Extract ONLY technical skills.

Examples:

Python
SQL
FastAPI
Docker
TensorFlow
PyTorch
Git
GitHub
PostgreSQL
SQL Server

Do NOT include spoken languages.

LANGUAGES

Extract ONLY spoken languages.

Examples:

Thai
English
Japanese
Chinese

OUTPUT

Return ONLY this JSON schema.

{{
    "name": "",
    "skills": [],
    "languages": [],
    "education": [
        {{
            "institution": "",
            "degree": "",
            "start_date": "",
            "end_date": ""
        }}
    ],
    "experience": [
        {{
            "title": "",
            "company": "",
            "start_date": "",
            "end_date": "",
            "description": []
        }}
    ],
    "projects": [
        {{
            "name": "",
            "description": [],
            "technologies": []
        }}
    ]
}}

Resume:

{text}
"""

    try:

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0,
                "top_p": 0.8,
                "top_k": 20,
                "response_mime_type": "application/json",
            },
        )

        match = re.search(r"\{.*\}", response.text, re.DOTALL)

        if not match:
            raise ValueError("No JSON returned")

        parsed = json.loads(match.group())

        parsed.setdefault("name", "")
        parsed.setdefault("skills", [])
        parsed.setdefault("languages", [])
        parsed.setdefault("education", [])
        parsed.setdefault("experience", [])
        parsed.setdefault("projects", [])

        if not isinstance(parsed["experience"], list):
            parsed["experience"] = []

        if not isinstance(parsed["projects"], list):
            parsed["projects"] = []

        return parsed

    except Exception as e:

        print("EXTRACTION ERROR:", e)

        return {
            "name": "",
            "skills": [],
            "languages": [],
            "education": [],
            "experience": [],
            "projects": []
        }