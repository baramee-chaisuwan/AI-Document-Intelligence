# AI Document Intelligence

AI-powered Resume Screening System built with FastAPI, Gemini AI, SQLAlchemy, PostgreSQL, and Docker.

This project is a mini Applicant Tracking System (ATS) that processes PDF resumes, extracts structured candidate information, analyzes skills using rule-based + AI scoring, and provides APIs for ranking, search, and analytics.

---

## Overview

The system automates resume processing and candidate evaluation through an AI pipeline:

- Upload PDF resumes
- Extract text from documents
- Generate AI summaries using Gemini
- Parse structured candidate data
- Analyze skills and experience
- Compute candidate scores (rule-based + AI hybrid)
- Store results in PostgreSQL
- Provide search, ranking, and analytics APIs

---

## Architecture

Client (Swagger / Postman)
→ FastAPI Router Layer
→ Service Layer (Business Logic)
→ Repository Layer (Database Access)
→ SQLAlchemy ORM
→ PostgreSQL (Docker)

---

## Processing Flow

Upload Resume (PDF)
→ Extract Text (PyMuPDF)
→ Gemini AI Analysis
→ Structured Data Extraction
→ Duplicate Detection
→ Rule-based Scoring
→ AI Scoring
→ Combined Final Score
→ Store in Database
→ Expose via REST API

---

## Features

### Resume Processing
- Upload PDF resumes
- Extract text using PyMuPDF
- Gemini AI-based resume analysis
- Structured candidate extraction
- Duplicate detection during ingestion

### Candidate Management
- Get all candidates
- Get candidate by ID
- Update candidate information
- Delete candidate records
- Search candidates with filters

### Search & Ranking
- Search candidates by name
- Filter by candidate level
- Filter by minimum skill score
- Ranking system based on skill score

### Dashboard Analytics
- Dashboard summary
- Top candidates
- Score distribution
- Level distribution
- Recent candidates

### Export
- Export candidate data as CSV

---

## Tech Stack

### Backend
- Python
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic

### AI & Processing
- Google Gemini API
- PyMuPDF

### Infrastructure
- Docker
- Uvicorn
- Git / GitHub

---

## Project Structure

AI-Document-Intelligence/
│
├── app/
│   ├── api/              # REST endpoints
│   ├── core/             # config & exceptions
│   ├── database/         # DB connection & models
│   ├── models/           # Pydantic schemas
│   ├── repositories/     # data access layer
│   └── services/         # business logic + AI
│
├── alembic/              # database migrations
├── uploads/              # uploaded PDF files
├── main.py               # FastAPI entry point
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md

---

## API Endpoints

### Upload
POST /upload
Upload and process PDF resume

---

### Candidates
GET /candidates
GET /candidates/{id}
PUT /candidates/{id}
DELETE /candidates/{id}

---

### Search
GET /candidates/search

Filters:
- name
- level
- minimum score

---

### Ranking
GET /candidates/ranking

---

### Statistics
GET /candidates/stats

---

### Dashboard
GET /dashboard/summary
GET /dashboard/top-candidates
GET /dashboard/score-distribution
GET /dashboard/level-distribution
GET /dashboard/recent-candidates

---

### Export
GET /candidates/csv

---

## Scoring System

- Rule-based scoring from extracted skills
- AI scoring using Gemini
- Combined final score

Example:

{
  "rule_score": 70,
  "ai_score": 78,
  "final_score": 74
}

---

## Example Output

{
  "candidate_level": "Junior",
  "skill_score": 72,
  "ai_status": "success"
}

---

## Docker Setup (Required)

Start PostgreSQL:

docker compose up -d

or

docker run -d \
  --name resume-postgres \
  -p 5432:5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=resume_db \
  postgres

---

## Run Project

Install dependencies:
pip install -r requirements.txt

Start server:
uvicorn main:app --reload

Docs:
http://127.0.0.1:8000/docs

---

## Key Learnings

- FastAPI backend development
- Clean architecture (Router → Service → Repository)
- REST API design
- SQLAlchemy ORM with PostgreSQL
- AI integration using Gemini API
- Resume parsing pipeline
- Duplicate detection system
- Hybrid scoring system
- Docker-based development environment

---

## Future Improvements (v2.0)

- JWT authentication
- Role-based access control
- Redis caching
- Celery background tasks
- Job matching system
- Vector DB (ChromaDB)
- React dashboard
- CI/CD pipeline

---

## Project Status

Version 1.0 Completed

Includes:
- Resume upload pipeline
- AI analysis (Gemini)
- Candidate management (CRUD)
- Search & ranking
- Dashboard analytics
- CSV export
- Duplicate detection
- Hybrid scoring
- Clean architecture
- PostgreSQL via Docker
- Exception handling