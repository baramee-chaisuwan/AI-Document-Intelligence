# AI-powered Resume Screening System (ATS) with Next.js, FastAPI, RAG, Gemini AI, ChromaDB, PostgreSQL, Docker, and GitHub Actions

AI-powered Resume Screening System built with Next.js, FastAPI, Gemini AI, PostgreSQL, SQLAlchemy, Docker, LangChain, and ChromaDB.

This project is a lightweight Applicant Tracking System (ATS) that automates resume processing, extracts structured candidate data, and performs AI-assisted evaluation and ranking.

The system provides a full-stack web application for HR users, including candidate management, AI assistant, AI recommendation, analytics dashboard, and resume export functionality.

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
* Provide HR web interface using Next.js
* Visualize candidate analytics through interactive dashboard
* Provide AI Assistant conversational interface
* Provide AI-powered candidate recommendation system
* Export candidate information as CSV

---

## AI Analysis

* Resume summarization using Gemini LLM
* Skill inference from unstructured text
* Candidate profiling (Junior / Mid / Senior)
* AI-based semantic evaluation

---

## Architecture

```text
                              HR User
                                 |
                                 v

                      +--------------------+
                      |  Next.js Frontend  |
                      |                    |
                      | Dashboard          |
                      | Candidate UI       |
                      | AI Assistant       |
                      | Recommendation     |
                      | Analytics          |
                      +--------------------+

                                 |
                                 |
                            REST API

                                 |
                                 v

                      +--------------------+
                      |  FastAPI Backend   |
                      |                    |
                      | API Layer          |
                      | Service Layer      |
                      | Repository Layer  |
                      +--------------------+

              ----------------|----------------
              |               |               |
              v               v               v

       +-------------+  +-------------+  +-------------+
       | PostgreSQL  |  |  RAG        |  | Gemini AI   |
       | Database    |  | Pipeline    |  | LLM API     |
       |             |  |             |  |             |
       | Candidate   |  | Embedding   |  | Analysis    |
       | Resume Data |  | Retrieval   |  | Generation  |
       | Scores      |  | ChromaDB    |  | Reasoning   |
       +-------------+  +-------------+  +-------------+
```

The system follows a full-stack AI architecture consisting of:

* Next.js Frontend for HR users to manage candidates, search resumes, view analytics, interact with AI Assistant, and receive AI recommendations.

* FastAPI Backend as the main application layer handling REST APIs, business logic, authentication-ready services, and AI workflows.

* PostgreSQL Database for storing candidate profiles, resume information, scores, and analysis results.
* RAG Pipeline using SentenceTransformer embeddings and ChromaDB for semantic resume retrieval and context-aware AI responses.

* Gemini AI for resume analysis, candidate evaluation, recommendation generation, and AI assistant responses.

## Architecture Diagram

![System Architecture](assets/screenshots/architecture_v2.1.png)

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
Gemini RAG Processing
        ↓
Expose REST API
        ↓
Next.js Web Application
        ↓
HR Dashboard / AI Assistant /
Recommendation / Analytics
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

* Resume embedding generation using SentenceTransformer (all-MiniLM-L6-v2)
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

### Web Application

* HR dashboard interface
* Candidate management UI
* Resume upload interface
* AI semantic search interface
* AI Assistant chat interface
* AI candidate recommendation interface
* Analytics visualization dashboard
* CSV export interface

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
![LangChain](https://img.shields.io/badge/LangChain-RAG-orange)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-CI-2088FF)
![Next.js](https://img.shields.io/badge/Next.js-black)
![TypeScript](https://img.shields.io/badge/TypeScript-blue)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-38B2AC)

### Backend
* Python 3.13
* FastAPI (REST API Framework)
* SQLAlchemy (ORM)
* PostgreSQL (Relational Database)
* Pydantic (Data Validation)

### Frontend

* Next.js
* TypeScript
* Tailwind CSS
* Recharts
* Lucide React

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
├── backend/
│   │
│   ├── app/
│   │   ├── api/                # REST API endpoints
│   │   ├── core/               # Configuration & exceptions
│   │   ├── database/           # Database connection & models
│   │   ├── models/             # Pydantic schemas
│   │   ├── repositories/       # Data access layer
│   │   ├── services/           # Business logic & AI services
│   │   ├── rag/                # RAG pipeline & prompts
│   │   └── vector/             # Embedding & ChromaDB operations
│   │
│   ├── alembic/                # Database migrations
│   ├── alembic.ini             # Alembic configuration
│   ├── tests/                  # Pytest test cases
│   ├── pytest.ini              # Pytest configuration
│   ├── Dockerfile              # Backend container
│   ├── requirements.txt        # Python dependencies
│   └── main.py                 # FastAPI entry point
│
├── frontend/
│   │
│   ├── app/
│   │   ├── dashboard/          # HR dashboard page
│   │   ├── candidates/         # Candidate management pages
│   │   ├── upload/             # Resume upload page
│   │   ├── search/             # AI semantic search page
│   │   ├── assistant/          # AI Assistant chat page
│   │   ├── recommend/          # AI recommendation page
│   │   ├── analytics/          # Candidate analytics page
│   │   └── export/             # Candidate export page
│   │
│   ├── components/             # Reusable UI components
│   │   ├── assistant/          # AI chat components
│   │   ├── candidates/         # Candidate UI components
│   │   ├── dashboard/          # Dashboard charts/components
│   │   ├── layout/             # Navbar, Sidebar, Layout
│   │   ├── search/             # Search components
│   │   └── upload/             # Upload components
│   │
│   ├── public/                 # Static assets
│   ├── services/               # Frontend API client services
│   ├── package.json            # Node dependencies
│   ├── package-lock.json
│   └── next.config.ts          # Next.js configuration
│
├── docker-compose.yml          # Multi-container orchestration
│
├── .github/
│   └── workflows/              # GitHub Actions CI/CD
│
├── .env.example                # Environment variables template
├── .gitignore
└── README.md
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
docker compose up -d postgres
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
cd backend

pip install -r requirements.txt

uvicorn main:app --reload
```

### 5.Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

### 6.Access the application

```text
Frontend:
http://localhost:3000

Backend:
http://localhost:8000/docs
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
GET /export/csv
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
* Full-stack application development with Next.js
* Frontend-backend API integration

---

## Future Improvements 

* JWT Authentication
* Role-based access control
* Redis caching
* Background processing with Celery
* Job description matching
* Cross encoder reranking
* Production monitoring
* AWS deployment

---

## Project Status

**Status:** Version 2.0 - Fullstack AI ATS Completed

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

### Version 2.0 Fullstack Features

* Next.js HR dashboard
* Candidate management interface
* AI Assistant
* AI Recommendation
* Analytics dashboard
* CSV Export

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

---

## Frontend Screenshots

### Dashboard

![Dashboard](assets/screenshots/frontend-dashboard.png)

### Candidate Management

![Candidates](assets/screenshots/frontend-candidates.png)

### AI Search

![Candidates](assets/screenshots/frontend-ai-search.png)

### AI Assistant

![Assistant](assets/screenshots/frontend-assistant.png)

### Recommendation

![Recommendation](assets/screenshots/frontend-recommend.png)

### Analytics

![Analytics](assets/screenshots/frontend-analytics.png)

### Export CSV

![Export CSV](assets/screenshots/frontend-export.png)