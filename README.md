# AI-powered Resume Screening System (ATS) with RAG, Gemini AI, ChromaDB, FastAPI, PostgreSQL, Docker, and GitHub Actions

AI-powered Resume Screening System built with FastAPI, Gemini AI, PostgreSQL, SQLAlchemy, Docker, LangChain, and ChromaDB.

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
* Generate resume embeddings
* Store vectors in ChromaDB
* Perform semantic search using vector similarity
* Provide RAG-based candidate recommendation

---

## AI Analysis

* Resume summarization using Gemini LLM
* Skill inference from unstructured text
* Candidate profiling (Junior / Mid / Senior)
* AI-based semantic evaluation

---

## Architecture

```text
           Client Layer
                 ↓
      FastAPI Application Layer
                 ↓
           Service Layer
                 ↓
 ┌───────────────┬────────────────┐
 ↓               ↓                ↓
Data Layer    AI Processing     RAG Pipeline
              Layer             Layer
 ↓               ↓                ↓
PostgreSQL    Gemini AI       Embedding Model
Database      + PyMuPDF            ↓
                              ChromaDB
                                   ↓
                         Semantic Search
                    (Vector Similarity Retrieval)
                                   ↓
                          Retrieved Context
                                   ↓
                              Gemini LLM
```

The system follows a layered backend architecture with an integrated AI pipeline.
The FastAPI service layer orchestrates business logic, database operations, and AI workflows.
The RAG pipeline handles document embedding, vector retrieval, and LLM-based candidate recommendation.

## Architecture Diagram

![System Architecture](assets/screenshots/architecture_v2.png)

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
Store Candidate Data
        ↓
Index Resume
        ↓
Generate Resume Embedding
        ↓
Store Vector in ChromaDB
        ↓
Semantic Search
(Vector Similarity Matching)
        ↓
Retrieved Resume Context
        ↓
Gemini RAG Recommendation
        ↓
Expose REST API
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

### RAG & AI Recommendation

* Resume embedding generation using SentenceTransformer
* Vector storage with ChromaDB
* Semantic search using vector similarity
* Context-aware candidate recommendation using Gemini
* AI-generated candidate matching explanation

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
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-336791)
![Gemini](https://img.shields.io/badge/Gemini-AI-8E75B2)
![ChromaDB](https://img.shields.io/badge/ChromaDB-vector--db-1D9E75)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI-2088FF)

### Backend
* Python 3.13
* FastAPI (REST API Framework)
* SQLAlchemy (ORM)
* PostgreSQL (Relational Database)
* Pydantic (Data Validation)

### AI & Document Processing
* Google Gemini API (LLM-based Resume Analysis)
* PyMuPDF (PDF Text Extraction)
* LangChain (RAG pipeline orchestration)
* Sentence Transformers (Embedding model)
* ChromaDB (Vector database)

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
│   ├── services/         # business logic + AI layer
│   ├── rag/              # RAG pipeline and prompts
│   └── vector/           # Embedding and ChromaDB operations
│
├── alembic/             # database migrations
├── alembic.ini          # migration config
│
├── main.py              # FastAPI entry point
├── tests/               # pytest test cases
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
* RAG assistant testing
* Candidate recommendation testing
* Vector search testing
* Semantic search validation
* Hybrid search validation
* AI scoring validation

---

## CI/CD Pipeline

GitHub Actions is used for Continuous Integration (CI), while Render provides Continuous Deployment (CD).

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
POST /upload/
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

### Semantic Search

```http
POST /search/
```

Performs semantic search using vector similarity retrieval with ChromaDB.

---

### AI Recommendation

```http
POST /recommend/
```

Provides AI-powered candidate recommendation using RAG retrieval.

---

### RAG Assistant

```http
POST /assistant/
```

Answers resume-related questions using retrieved candidate context.

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

```text
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
* Retrieval Augmented Generation (RAG)
* Vector database integration with ChromaDB
* Semantic search implementation
* AI recommendation pipeline
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
* Background processing with Celery
* Job description matching with resume retrieval
* Advanced reranking model
* React dashboard
* Production monitoring
* Multi-environment deployment (Staging / Production)

---

## Project Status

**Status:** Version 2.0 - RAG Pipeline Completed

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

### Version 2.0 Implemented Features

* Resume embedding pipeline
* ChromaDB vector storage
* Semantic search using ChromaDB vector similarity
* Hybrid search implementation
* RAG assistant
* AI candidate recommendation
* Automated RAG integration tests

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

### Semantic Search

![Semantic Search API](assets/screenshots/semantic-search-api.png)

![Semantic Search API](assets/screenshots/semantic-search-api2.png)

### AI Recommendation API

![Recommendation API](assets/screenshots/recommend-api.png)

![Recommendation API](assets/screenshots/recommend-api2.png)

### RAG Assistant API

![Assistant API](assets/screenshots/assistant-api.png)

![Assistant API](assets/screenshots/assistant-api2.png)

### Dashboard Summary

![Dashboard Summary](assets/screenshots/dashboard-summary.png)

### Top Candidates

![Top Candidates](assets/screenshots/top-candidates.png)

### Export CSV API

![CSV Export](assets/screenshots/csv-export.png)
