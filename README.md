# AI-powered Resume Screening System (ATS) built with FastAPI, PostgreSQL, Gemini AI, Docker, SQLAlchemy, and GitHub Actions

AI-powered Resume Screening System built with FastAPI, Gemini AI, PostgreSQL, SQLAlchemy, and Docker.

This project is a lightweight Applicant Tracking System (ATS) that automates resume processing, extracts structured candidate data, and performs AI-assisted evaluation and ranking.

---

## Overview

The system automates resume processing and candidate evaluation through an AI pipeline:

* Upload PDF resumes
* Extract text from documents
* Generate AI summaries using Gemini
* Parse structured candidate data
* Analyze skills and experience
* Compute candidate scores (rule-based + AI hybrid)
* Store results in PostgreSQL
* Provide search, ranking, and analytics APIs

---

## AI Analysis

* Resume summarization using Gemini LLM
* Skill inference from unstructured text
* Candidate profiling (Junior / Mid / Senior)
* AI-based semantic evaluation

---

## Architecture

```text
Client
   ↓
FastAPI Router
   ↓
Service Layer (Business + AI)
   ↓
Repository Layer
   ↓
SQLAlchemy ORM
   ↓
PostgreSQL
```

## Architecture Diagram

![System Architecture](assets/screenshots/architecture.png)

---

## Processing Flow

```text
Upload Resume (PDF)
        ↓
Extract Text (PyMuPDF)
        ↓
Gemini AI Analysis
        ↓
Structured Data Extraction
        ↓
Duplicate Detection
        ↓
Rule-based Scoring
        ↓
AI Scoring
        ↓
Combined Skill Score
        ↓
Store in Database
        ↓
Expose via REST API
```

---

## Features

### Resume Processing

* Upload PDF resumes
* Extract text using PyMuPDF
* Gemini AI-based resume analysis
* Structured candidate extraction
* Duplicate detection during ingestion

### Candidate Management

* Get all candidates
* Get candidate by ID
* Update candidate information
* Delete candidate records
* Search candidates with filters (name, level, score)

### Search & Ranking

* Search candidates by name
* Filter by candidate level
* Filter by minimum skill score
* Ranking system based on skill score

### Dashboard Analytics

* Dashboard summary
* Top candidates
* Score distribution
* Level distribution
* Recent candidates

### Export

* Export candidate data as CSV

---

## Tech Stack

![Python](https://img.shields.io/badge/python-3.13-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-005571)
![Docker](https://img.shields.io/badge/docker-blue)

### Backend
* Python 3.13
* FastAPI (REST API Framework)
* SQLAlchemy (ORM)
* PostgreSQL (Relational Database)
* Pydantic (Data Validation)

### AI & Document Processing
* Google Gemini API (LLM-based Resume Analysis)
* PyMuPDF (PDF Text Extraction)

### Infrastructure & DevOps
* Docker (Containerization)
* Uvicorn (ASGI Server)
* GitHub Actions (Continuous Integration)
* Render (Cloud Deployment)
* Git / GitHub (Version Control)

---

## Project Structure

```text
AI-Document-Intelligence/
│
├── .github/
│   └── workflows/        # GitHub Actions (CI)
│
├── app/
│   ├── api/              # REST API endpoints
│   ├── core/             # config & exceptions
│   ├── database/         # DB connection & models
│   ├── models/           # Pydantic schemas
│   ├── repositories/     # data access layer
│   └── services/         # business logic + AI layer
│
├── alembic/             # database migrations
├── alembic.ini          # migration config
│
├── main.py              # FastAPI entry point
├── test/                # test cases (pytest)
├── pytest.ini           # test configuration
│
├── docker-compose.yml   # multi-container setup
├── Dockerfile           # container build
├── requirements.txt     # dependencies
│
└── .gitignore
```

---

## Quick Start

### 1.Clone project

```bash
git clone https://github.com/baramee-chaisuwan/AI-Document-Intelligence.git
cd AI-Document-Intelligence
```

### 2.Setup environment

```bash
cp .env.example .env
```

### .env example

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/resume_db
GEMINI_API_KEY=your_api_key_here
```

### 3.Start PostgreSQL (Docker)

This project requires Docker to run PostgreSQL database.

### Start database

```bash
docker compose up -d
```

or

```bash
docker run -d \
  --name resume-postgres \
  -p 5432:5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=resume_db \
  postgres
```

### 4.Run system (Docker recommended)

```bash
docker compose up --build
```

### OR Run Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

### 5.API documentation

```http
http://127.0.0.1:8000/docs
```

---

## Testing

This project includes automated testing using pytest.

### Run tests locally

```bash
pytest -v
```

### Test coverage includes:

* API endpoint validation
* Database operations
* Service layer logic
* Resume upload pipeline

---

## CI Pipeline (GitHub Actions)

The project includes a fully automated CI pipeline using GitHub Actions.

## CI Steps

### 1. PostgreSQL Service (Test DB)

```yaml
services:
  postgres:
    image: postgres:16
    env:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: resume_db
```

### 2. Environment Variables (GitHub Actions)

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/resume_db
GEMINI_API_KEY=your_api_key
```

### Required GitHub Secrets

- GEMINI_API_KEY → Google Gemini API key

### 3. Pipeline Steps

* Checkout repository
* Setup Python
* Install dependencies
* Run database migrations (Alembic)
* Run tests (pytest)

```bash
alembic upgrade head
pytest -v
```

---

## CI Status

* Dependency installation
* Database migration 
* API tests
* Service layer validation

---

## CI Badge

![CI](https://github.com/baramee-chaisuwan/AI-Document-Intelligence/actions/workflows/test.yml/badge.svg)

---

## Deployment

The application is deployed on Render.

Render is connected to the GitHub repository and automatically deploys the latest version whenever changes are pushed to the main branch.

---

## API Endpoints

### Upload

```http
POST /upload
```

Upload a PDF resume and process it using the AI pipeline.

---

### Candidates

```http
GET /candidates
GET /candidates/{id}
PUT /candidates/{id}
DELETE /candidates/{id}
```

Manage candidate records stored in the database.

---

### Search

```http
GET /candidates/search
```

Search candidates using filters such as:

* name
* candidate level
* minimum score

---

### Ranking

```http
GET /candidates/ranking
```

Returns the highest-ranked candidates based on skill score.

---

### Statistics

```http
GET /candidates/stats
```

Returns candidate statistics and score averages.

---

### Dashboard

```http
GET /dashboard/summary
GET /dashboard/top-candidates
GET /dashboard/score-distribution
GET /dashboard/level-distribution
GET /dashboard/recent-candidates
```

Provides aggregated analytics including candidate summary, ranking, score distribution, and recent activity.

---

### Export

```http
GET /candidates/csv
```

Exports candidate data as a CSV file.

---

## Scoring System

Hybrid candidate scoring approach:

* Rule-based scoring from extracted skills and experience
* AI-based scoring using Gemini
* Combined skill score for ranking

```text id="score_formula"
Skill Score = (0.7 × Rule Score) + (0.3 × AI Score)
```

```json
{
  "rule_score": 70,
  "ai_score": 78,
  "skill_score": 74
}
```

---

## Example Output

```json
{
  "candidate_level": "Junior",
  "skill_score": 72,
  "ai_status": "success"
}
```

---

## Key Learnings

* FastAPI backend development
* Clean architecture (Router → Service → Repository)
* REST API design
* SQLAlchemy ORM with PostgreSQL
* AI integration using Gemini API
* Resume parsing pipeline
* Duplicate detection system
* Hybrid candidate scoring system
* Error handling with custom exceptions
* Docker-based deployment workflow
* CI/CD pipeline (GitHub Actions for CI, auto-deploy to Render for CD)

---

## Future Improvements 

* JWT authentication system
* Role-based access control (RBAC)
* Redis caching
* Background task processing (Celery)
* Job description matching
* Vector database integration (ChromaDB)
* React dashboard
* Multi-environment deployment (Staging / Production)

---

## Project Status

**Status:** Version 1.0 Completed

### Implemented Features

* Resume upload and PDF processing
* AI-powered resume analysis using Gemini
* Candidate management (CRUD)
* Search and ranking system
* Dashboard analytics
* CSV export
* Duplicate detection
* Hybrid candidate scoring (Rule-based + AI)
* Clean Architecture (Router → Service → Repository)
* PostgreSQL with Docker
* Alembic database migrations
* Automated testing with pytest
* CI pipeline using GitHub Actions
* Deployment on Render

---

### Live Demo

* API: https://ai-document-intelligence-bs16.onrender.com
* Swagger UI: https://ai-document-intelligence-bs16.onrender.com/docs

---

## API Screenshots

### Upload Resume API

![Upload API](assets/screenshots/upload-api.png)

### Search Candidates API

![Search API](assets/screenshots/search-candidates-api.png)

### Ranking API

![Ranking API](assets/screenshots/ranking-api.png)

### Dashboard Summary

![Dashboard Summary](assets/screenshots/dashboard-summary.png)

### Top Candidates

![Top Candidates](assets/screenshots/top-candidates.png)

### Export CSV API

![CSV Export](assets/screenshots/csv-export.png)