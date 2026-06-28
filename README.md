# AI Document Intelligence

AI-powered Resume Screening System built with FastAPI, Gemini AI, SQLAlchemy, and SQLite.

This project simulates a mini Applicant Tracking System (ATS) used by HR teams to process resumes, extract candidate information, analyze skills, rank applicants, and manage candidate data through REST APIs.

---

## Overview

The system allows users to upload PDF resumes, automatically extracts text from the document, uses Gemini AI to summarize and structure candidate information, performs candidate analysis and scoring, and stores the results in a database for further search and management.

### Processing Flow

```text
Upload Resume (PDF)
        ↓
Extract Text from PDF
        ↓
Generate AI Summary
        ↓
Extract Structured Resume Data
        ↓
Analyze Candidate
        ↓
Calculate Skill Score
        ↓
Save to Database
        ↓
Search / Ranking / Dashboard
```

---

## Features

### Resume Processing

* Upload PDF resumes
* Extract text using PyMuPDF
* Generate AI-powered resume summaries
* Extract structured candidate information

### Candidate Analysis

* Candidate level classification
* Rule-based scoring engine
* AI-assisted scoring
* Explainable score breakdown
* Skill evaluation

### Candidate Management

* View all candidates
* Get candidate by ID
* Update candidate information
* Delete candidate records
* Duplicate candidate detection

### Search & Ranking

* Search candidates by name
* Filter candidates by level
* Filter candidates by minimum score
* Candidate ranking endpoint

### Analytics

* Candidate statistics
* Average skill score
* Candidate distribution by level
* Dashboard summary
* Top candidates endpoint

### Export

* Export candidate data as CSV

---

## Tech Stack

### Backend

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic

### AI & Document Processing

* Google Gemini API
* PyMuPDF

### Development Tools

* Git
* GitHub
* Uvicorn

---

## Project Structure

```text
AI-Document-Intelligence
│
├── app
│   ├── api
│   ├── core
│   ├── database
│   ├── models
│   └── services
│
├── uploads
├── main.py
├── requirements.txt
├── README.md
└── resume.db
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
```

Provides dashboard analytics and top candidate information.

---

### Export

```http
GET /candidates/csv
```

Exports candidate data as a CSV file.

---

## Explainable Scoring System

The scoring system combines rule-based scoring with AI analysis.

Example score breakdown:

```json
{
  "python": 15,
  "sql": 15,
  "machine_learning": 15,
  "etl": 15,
  "experience": 10
}
```

The final score is calculated from the rule-based score and AI score to provide a more transparent evaluation process.

---

## Example Candidate Analysis Output

```json
{
  "candidate_level": "Junior",
  "skill_score": 72,
  "rule_score": 70,
  "ai_score": 78,
  "ai_status": "success"
}
```

---

## How to Run

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Start Server

```bash
uvicorn main:app --reload
```

### Open API Documentation

```text
http://127.0.0.1:8000/docs
```

---

## Learning Outcomes

Through this project, I gained hands-on experience with:

* FastAPI API development
* REST API design
* SQLAlchemy ORM
* SQLite database management
* PDF processing
* Gemini AI integration
* Prompt engineering
* Candidate scoring systems
* Search and analytics APIs
* Error handling
* Git and GitHub workflows

---

## Future Improvements

* Docker deployment
* PostgreSQL support
* Frontend dashboard
* Authentication and authorization
* Resume matching against job descriptions
* Advanced AI candidate recommendations
* ChromaDB and vector search integration

---

## Project Status

Current Version: Portfolio Edition

Completed Features:

* Resume Upload
* Resume Extraction
* AI Summary
* Candidate Analysis
* Candidate Management
* Search & Filtering
* Ranking System
* Dashboard Analytics
* CSV Export
* Duplicate Detection
* Explainable Scoring
* REST API Documentation

```
```
