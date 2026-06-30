# AI Document Intelligence

AI-powered Resume Screening System built with FastAPI, Gemini AI, SQLAlchemy, PostgreSQL, and Docker.

This project is a mini Applicant Tracking System (ATS) that processes PDF resumes, extracts structured candidate information, analyzes skills using rule-based + AI scoring, and provides APIs for ranking, search, and analytics.

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

## Architecture

```text
Client (Swagger / Postman)
        ↓
FastAPI Router Layer
        ↓
Service Layer (Business Logic)
        ↓
Repository Layer (Database Access)
        ↓
SQLAlchemy ORM
        ↓
PostgreSQL (Docker)
```

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
Combined Final Score
        ↓
Store in Database
        ↓
Expose via REST API
```

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

### Backend

* Python
* FastAPI
* SQLAlchemy
* PostgreSQL
* Pydantic

### AI & Processing

* Google Gemini API
* PyMuPDF

### Infrastructure

* Docker
* Uvicorn
* Git / GitHub

---

## Project Structure

```text
AI-Document-Intelligence/
│
├── app/
│   ├── api/              # REST endpoints
│   ├── core/             # config & exceptions
│   ├── database/         # DB connection & models
│   ├── models/          # Pydantic schemas
│   ├── repositories/    # data access layer
│   └── services/        # business logic + AI
│
├── alembic/             # database migrations
├── uploads/             # uploaded PDF files
├── main.py              # FastAPI entry point
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

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

Hybrid scoring approach:

* Rule-based scoring from extracted skills and experience
* AI-based scoring using Gemini
* Combined final score for ranking

```json
{
  "rule_score": 70,
  "ai_score": 78,
  "final_score": 74
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

## Docker Setup (Required)

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

---

## Run Project

### Install dependencies

```bash
pip install -r requirements.txt
```

### Start server

```bash
pip uvicorn main:app --reload
```

### API documentation

```text
http://127.0.0.1:8000/docs
```

## Key Learnings

* FastAPI backend development
* Clean architecture (Router → Service → Repository)
* REST API design
* SQLAlchemy ORM with PostgreSQL
* AI integration using Gemini API
* Resume parsing pipeline
* Duplicate detection system
* Hybrid scoring system
* Error handling with custom exceptions
* Docker-based development environment

```

## Future Improvements (v2.0)

* JWT authentication system
* Role-based access control
* Redis caching layer
* Background task processing (Celery)
* Job description matching system
* Vector database integration (ChromaDB)
* Frontend dashboard (React)
* CI/CD pipeline

```

## Project Status

Version 1.0 Completed

Includes:

* Resume upload and processing pipeline
* AI-powered resume analysis (Gemini)
* Candidate management system (CRUD)
* Search and ranking system
* Dashboard analytics module
* CSV export functionality
* Duplicate detection system
* Hybrid scoring system
* Clean architecture (Router → Service → Repository)
* PostgreSQL via Docker
* Custom exception handling layer