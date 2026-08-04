# AI Document Intelligence ATS

AI Document Intelligence is a full-stack applicant tracking system for ingesting
PDF resumes, extracting structured candidate information, scoring candidates,
searching indexed resume evidence, and supporting recruiter workflows with
Gemini-powered analysis, recommendations, and an HR assistant.

The application combines a Next.js user interface, a FastAPI API, PostgreSQL,
local ChromaDB and BM25 indexes, SentenceTransformer embeddings, and Google
Gemini 2.5 Flash. Authentication and role-based access control are enforced by
the backend and reflected in the frontend.

## Implemented features

- Recruiter self-registration, login, logout, and current-user loading
- bcrypt password hashing and expiring HS256 JWT access tokens
- Backend RBAC for `admin` and `recruiter` users
- Interactive CLI for creating administrator accounts
- PDF validation and text extraction with PyMuPDF
- Gemini-based resume parsing, summarization, and AI assessment
- Deterministic skill scoring with AI-assisted final scoring and fallback
- Candidate list, detail, filtering, ranking, statistics, update, and deletion APIs
- Dashboard totals, top candidates, recent candidates, score distribution, and level distribution
- SentenceTransformer embeddings stored in persistent ChromaDB
- JSON-backed BM25 index and reciprocal-rank-fusion hybrid retrieval
- Semantic candidate search, RAG assistant, and structured candidate recommendation
- UTF-8 CSV export with spreadsheet-formula sanitization
- Next.js dashboard, analytics, candidate, upload, search, assistant, recommendation, and export pages
- Automated backend tests for authentication, RBAC, CRUD, upload, scoring, search, RAG, dashboard, export, and the admin CLI

## Architecture

```text
Browser
  Next.js App Router + React + TypeScript
  Auth context, route guard, Axios services, Tailwind CSS, Recharts
                         |
                         | HTTP/JSON + Bearer JWT
                         v
FastAPI
  API routers -> services -> repositories
       |             |             |
       |             |             +-> SQLAlchemy -> PostgreSQL
       |             +-> Gemini 2.5 Flash
       |             +-> PyMuPDF
       |             +-> SentenceTransformer
       |             +-> ChromaDB + BM25 JSON -> hybrid RAG
       +-> Pydantic request/response validation
```

### Frontend

The frontend is a Next.js 16 App Router application using React 19 and
TypeScript. Pages under `frontend/app` are composed from reusable components,
while `frontend/services` contains the typed Axios calls to the backend.
Authentication state is provided at the root layout by `AuthProvider` and
`AuthGate`.

Key routes:

| Route | Purpose |
| --- | --- |
| `/login` | Public login page |
| `/register` | Public recruiter-registration page |
| `/dashboard` | Candidate summary, charts, top candidates, and recent candidates |
| `/analytics` | Analytics view backed by dashboard endpoints |
| `/candidates` | Candidate list and admin-only delete control |
| `/candidates/{id}` | Candidate profile, scores, and score breakdown |
| `/upload` | PDF resume ingestion |
| `/search` | ChromaDB semantic candidate search |
| `/assistant` | RAG assistant over indexed resume evidence |
| `/recommend` | Structured candidate recommendation for a job requirement |
| `/export` | Admin-only CSV export UI |

There is no separate backend `/analytics` route; the frontend analytics page
uses the authenticated `/dashboard/*` endpoints.

### Backend

The backend is a synchronous FastAPI application organized into:

- `backend/app/api`: HTTP routes, dependencies, validation, and response mapping
- `backend/app/services`: authentication, candidate, PDF, Gemini, scoring, indexing, search, and RAG orchestration
- `backend/app/repositories`: SQLAlchemy data access for users and candidates
- `backend/app/database`: engine, sessions, and ORM models
- `backend/app/models`: Pydantic request and response models
- `backend/app/rag`: prompts, text splitting, model chains, retrieval context, and evaluation helpers
- `backend/app/vector`: ChromaDB, BM25 persistence, vector operations, and hybrid search
- `backend/alembic`: PostgreSQL schema migrations
- `backend/scripts`: administrative CLI tools
- `backend/tests`: pytest suite

### Data stores and external services

- **PostgreSQL** stores users and candidate records.
- **ChromaDB** stores resume chunks and normalized embedding vectors at
  `backend/chroma_db`.
- **BM25 storage** persists documents and metadata at
  `backend/data/bm25_data.json` using a temporary file and atomic replacement.
- **Google Gemini 2.5 Flash** performs resume extraction, summarization, AI
  assessment, assistant generation, and structured recommendations.
- **SentenceTransformer** uses `paraphrase-MiniLM-L3-v2` by default. The model
  is loaded lazily and may be downloaded from Hugging Face on first use.

## Authentication

### Backend flow

Passwords are hashed with bcrypt using 12 rounds. The backend implements signed
HS256 JWT access tokens containing `sub`, `type`, `iat`, and `exp` claims. It
does not currently issue refresh tokens or authentication cookies.

| Endpoint | Access | Behavior |
| --- | --- | --- |
| `POST /auth/register` | Public | Validates email, full name, and password; creates an active recruiter |
| `POST /auth/login` | Public | Verifies credentials and active status; returns `access_token`, `token_type`, and `expires_in` |
| `GET /auth/me` | Authenticated | Resolves the Bearer token and returns the active user |

Registration normalizes email to lowercase and trims the full name. Passwords
must contain 8-72 characters and must not exceed 72 UTF-8 bytes. Duplicate
email addresses return `409 Conflict`.

Public registration always creates a user with role `recruiter`. The request
does not accept a role, and there is no public administrator-registration
endpoint.

### Frontend flow

The frontend stores the access token in tab-scoped `sessionStorage`. The shared
Axios request interceptor adds `Authorization: Bearer <token>` to API requests.
At startup, the auth context calls `GET /auth/me` to load the user.

The Axios response interceptor handles any `401` by clearing the stored token
and redirecting to `/login`. Logout performs the same local cleanup and uses a
full redirect to `/login`.

`/login` and `/register` are public. Every other frontend route requires an
authenticated user. Authenticated users who open either public auth page are
redirected to `/dashboard`. A successful registration redirects to `/login`
with a one-time success message.

Because `sessionStorage` is readable by browser JavaScript, production security
depends on preventing XSS. Moving token delivery to backend-issued HttpOnly,
Secure, SameSite cookies would require a backend authentication change.

## Authorization and RBAC

The database and Pydantic model define two roles: `admin` and `recruiter`.
Backend authorization is enforced with FastAPI dependencies.

| Access level | Backend routes |
| --- | --- |
| Public | `GET /health/`, `POST /auth/register`, `POST /auth/login` |
| Authenticated admin or recruiter | `GET /auth/me`, `GET /candidates/`, `GET /candidates/{id}`, `GET /candidates/stats`, `GET /candidates/ranking`, all `GET /dashboard/*` routes |
| Staff (`admin` or `recruiter`) | `GET /candidates/search`, `POST /upload/`, `POST /search/`, `POST /assistant/`, `POST /recommend/` |
| Admin only | `PUT /candidates/{id}`, `DELETE /candidates/{id}`, `GET /export/csv` |

Missing, malformed, expired, or otherwise invalid tokens return
`401 Unauthorized` with `WWW-Authenticate: Bearer`. Tokens for missing or inactive
users also return `401`. A valid authenticated user without the required role
receives `403 Forbidden`; admin-only routes return `Admin access required`.

The frontend mirrors these rules: the navbar displays the authenticated user's
full name and role, recruiters do not see the Export navigation item or
candidate Delete buttons, and recruiter navigation to `/export` redirects to
`/dashboard`. The backend remains the authoritative security boundary. The
admin-only candidate-update API currently has no corresponding update control
in the frontend.

## Resume and AI pipeline

1. `POST /upload/` reads the uploaded file in memory and enforces a `.pdf`
   filename, nonempty content, `%PDF-` signature, and configured size limit.
2. PyMuPDF extracts text from every page. Image-only PDFs without extractable
   text are rejected.
3. Gemini extracts normalized name, skills, languages, education, experience,
   and projects as JSON.
4. The API checks for an existing candidate with the same extracted name.
5. Gemini creates a short summary. The rule engine scores technical keywords,
   experience, projects, and engineering signals; Gemini supplies an AI score.
6. On successful AI analysis, the final score is:

   ```text
   skill_score = round(0.8 * rule_score + 0.2 * ai_score)
   ```

   If AI assessment fails, `ai_status` is `fallback`, `ai_score` is `0`, and
   `skill_score` uses the rule score.
7. The candidate is committed to PostgreSQL.
8. Resume text is split with a recursive character splitter, embedded, and
   written to ChromaDB and the BM25 JSON store.

The upload API reports a `503` containing the saved candidate ID if PostgreSQL
succeeds but indexing fails. Indexing attempts to clean partial ChromaDB and
BM25 data before returning the failure.

### Retrieval behavior

- `POST /search/` performs ChromaDB vector similarity search, removes duplicate
  candidate IDs, and joins current candidate details from PostgreSQL.
- The assistant and recommendation paths use hybrid retrieval. Vector and BM25
  rankings are fused with equal-weight reciprocal rank fusion (`RRF_K = 60`).
- The assistant builds bounded context from retrieved chunks and returns a
  no-information response when no evidence is available.
- Recommendation uses a structured Pydantic response and rejects a generated
  candidate ID unless it belongs to the retrieved candidate set.

## API summary

The root API route redirects to FastAPI Swagger UI at `/docs`.

| Method | Route | Purpose | Required access |
| --- | --- | --- | --- |
| `GET` | `/health/` | Health response | Public |
| `POST` | `/auth/register` | Create recruiter | Public |
| `POST` | `/auth/login` | Issue access token | Public |
| `GET` | `/auth/me` | Current user | Authenticated |
| `GET` | `/candidates/` | Paginated candidate list | Authenticated |
| `GET` | `/candidates/search` | Filter by name, level, or minimum AI score | Staff |
| `GET` | `/candidates/stats` | Count and average AI score | Authenticated |
| `GET` | `/candidates/ranking` | Candidate ranking ordered by AI score | Authenticated |
| `GET` | `/candidates/{id}` | Candidate detail | Authenticated |
| `PUT` | `/candidates/{id}` | Update `candidate_level` and/or `skill_score` | Admin |
| `DELETE` | `/candidates/{id}` | Delete candidate and associated indexes | Admin |
| `POST` | `/upload/` | Process and index a PDF resume | Staff |
| `POST` | `/search/` | Semantic candidate search | Staff |
| `POST` | `/assistant/` | Ask the RAG assistant | Staff |
| `POST` | `/recommend/` | Recommend a candidate | Staff |
| `GET` | `/dashboard/summary` | Dashboard totals and top candidate | Authenticated |
| `GET` | `/dashboard/top-candidates` | Highest AI scores | Authenticated |
| `GET` | `/dashboard/score-distribution` | AI-score buckets | Authenticated |
| `GET` | `/dashboard/level-distribution` | Counts by candidate level | Authenticated |
| `GET` | `/dashboard/recent-candidates` | Most recently created candidates | Authenticated |
| `GET` | `/export/csv` | Download timestamped UTF-8 CSV | Admin |

## Repository structure

```text
AI-Document-Intelligence/
|-- backend/
|   |-- app/
|   |   |-- api/              # FastAPI routes and auth dependencies
|   |   |-- core/             # Environment config, security, exceptions
|   |   |-- database/         # SQLAlchemy engine and ORM models
|   |   |-- models/           # Pydantic schemas
|   |   |-- repositories/     # Database access
|   |   |-- services/         # Business, AI, scoring, and indexing logic
|   |   |-- rag/              # Prompts, chains, chunking, evaluation
|   |   `-- vector/           # ChromaDB, BM25, hybrid retrieval
|   |-- alembic/              # Database migrations
|   |-- scripts/create_admin.py
|   |-- tests/
|   |-- Dockerfile
|   |-- main.py
|   `-- requirements.txt
|-- frontend/
|   |-- app/                  # Next.js App Router pages
|   |-- components/           # Auth, layout, candidate, dashboard, UI
|   |-- contexts/             # Authentication context
|   |-- lib/                  # Browser token and flash-message storage
|   |-- services/             # Axios client and API services
|   |-- types/                # Shared frontend auth types
|   `-- package.json
|-- assets/screenshots/
|-- docs/evaluation.md
|-- docker-compose.yml
|-- .env.example
`-- README.md
```

## Configuration

Copy the example file and replace placeholders with environment-specific
values. Never commit a populated `.env` file.

```bash
cp .env.example .env
```

### Required backend variables

| Variable | Requirement |
| --- | --- |
| `DATABASE_URL` | SQLAlchemy PostgreSQL connection URL; no default |
| `GEMINI_API_KEY` | Google Gemini API key; application import fails if missing |
| `JWT_SECRET_KEY` | Signing secret; token operations require at least 32 UTF-8 bytes |

`JWT_ALGORITHM` is configurable but the implementation supports only `HS256`.

### Optional backend variables and verified defaults

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_NAME` | `AI Resume Intelligence` | FastAPI title and logs |
| `APP_VERSION` | `1.0.0` | FastAPI version |
| `ENVIRONMENT` | `development` | Enables startup `create_all` only in development when not testing |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:3001` | Comma-separated allowed browser origins |
| `JWT_ALGORITHM` | `HS256` | Access-token signature algorithm |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access-token lifetime |
| `MAX_UPLOAD_SIZE_MB` | `10` | Maximum PDF size |
| `EMBEDDING_MODEL_NAME` | `paraphrase-MiniLM-L3-v2` | SentenceTransformer model |
| `EMBEDDING_BATCH_SIZE` | `16` | Batch embedding size |
| `RAG_CHUNK_SIZE` | `1000` | Recursive splitter character size |
| `RAG_CHUNK_OVERLAP` | `150` | Recursive splitter overlap |
| `DATABASE_MAX_RETRIES` | `10` | Initial database connection attempts |
| `DATABASE_RETRY_DELAY_SECONDS` | `3` | Delay between connection attempts |
| `DATABASE_POOL_SIZE` | `5` | SQLAlchemy pool size |
| `DATABASE_MAX_OVERFLOW` | `10` | SQLAlchemy pool overflow |
| `TESTING` | `false` | Skips startup database connection checks when `true` |
| `PORT` | `8000` | Uvicorn port used by the Docker command |

The current `.env.example` also contains `FRONTEND_URL`, but application code
does not read it; configure browser access with `CORS_ORIGINS` instead.

### Frontend variable

Create `frontend/.env.local`:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

`NEXT_PUBLIC_API_URL` is required when the shared Axios client is imported. It
is public frontend configuration and must not contain a secret.

## Local development

### Prerequisites

- Python 3.13 (the version used by the backend Docker image and CI)
- PostgreSQL 16, or Docker for the provided database service
- Node.js and npm compatible with Next.js 16
- A Gemini API key

### 1. Create the environment file

From the repository root:

```bash
cp .env.example .env
```

When using the provided PostgreSQL container with a locally running backend,
use this database URL because Compose publishes PostgreSQL on host port `5433`:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/resume_db
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
JWT_SECRET_KEY=REPLACE_WITH_A_RANDOM_SECRET_OF_AT_LEAST_32_BYTES
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:3000
```

The values above are placeholders, not production secrets.

### 2. Start PostgreSQL

```bash
docker compose up -d db
```

### 3. Install and run the backend

Create a virtual environment from the repository root:

```bash
python -m venv .venv
```

Activate it on macOS/Linux:

```bash
source .venv/bin/activate
```

Or activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies, apply migrations, and run the API:

```bash
cd backend
python -m pip install -r requirements.txt
alembic upgrade head
python -m uvicorn main:app --reload
```

The API is available at `http://localhost:8000`; Swagger UI is at
`http://localhost:8000/docs`.

### 4. Install and run the frontend

Create `frontend/.env.local` with `NEXT_PUBLIC_API_URL`, then:

```bash
cd frontend
npm install
npm run dev
```

The frontend is available at `http://localhost:3000`.

Production validation and build:

```bash
npm run lint
npx tsc --noEmit --incremental false
npm run build
```

Run the built frontend with:

```bash
npm run start
```

## Docker

`docker-compose.yml` defines two services:

| Service | Container | Published port | Storage |
| --- | --- | --- | --- |
| `api` | `resume_api` | `8000:8000` | `./backend:/app` and `./backend/chroma_db:/app/chroma_db` |
| `db` | `resume_db` | `5433:5432` | Named volume `pgdata` |

The API image uses Python 3.13, installs `backend/requirements.txt`, and runs
Uvicorn on `0.0.0.0:${PORT:-8000}`. Compose loads the root `.env` for the API
and overrides `DATABASE_URL` with the internal
`postgresql://postgres:postgres@db:5432/resume_db` address.

Start and migrate the backend stack:

```bash
docker compose up -d --build db api
docker compose exec api alembic upgrade head
```

Follow API logs:

```bash
docker compose logs -f api
```

The Compose file does not define a frontend service. Run the frontend locally
against `http://localhost:8000` or deploy it separately. Because the backend
directory is bind-mounted, ChromaDB and `backend/data/bm25_data.json` persist on
the host; PostgreSQL persists in `pgdata`.

## Create the first administrator

Public registration intentionally creates recruiters only. Create the first
administrator directly through the interactive bootstrap CLI after applying
database migrations. It prompts for email, full name, password, and password
confirmation; passwords are read with `getpass` and are never printed.

Local command from the backend directory:

```bash
cd backend
alembic upgrade head
python scripts/create_admin.py
```

Inside the running API container:

```bash
docker compose exec api alembic upgrade head
docker compose exec api python scripts/create_admin.py
```

The command creates an active `admin`, rejects duplicate email addresses,
rolls back failures, and exits nonzero on failure.

## Testing

### Backend

From the backend directory:

```bash
cd backend
pytest -v
```

Or inside the API container:

```bash
docker compose exec api pytest -v
```

The suite covers health, authentication, real JWT/RBAC paths, candidates,
dashboard data, upload orchestration, scoring, semantic and hybrid retrieval,
assistant/recommendation behavior, CSV export, and the administrator CLI. The
hybrid-search test loads the SentenceTransformer model, so its first run may
need network access to download the configured model.

### Frontend

No frontend unit-test runner is configured in `package.json`. The available
quality checks are:

```bash
cd frontend
npm run lint
npx tsc --noEmit --incremental false
npm run build
```

The GitHub Actions workflow currently installs backend dependencies, starts
PostgreSQL 16, applies Alembic migrations, and runs pytest. It does not run the
frontend checks.

## Operational notes

- Resume upload, Gemini calls, database writes, and indexing execute in the
  request path; there is no background worker or queue.
- PostgreSQL is committed before resume indexing. An indexing failure therefore
  leaves the candidate row saved and returns its ID in the error response.
- ChromaDB and BM25 are local persistent stores. Multi-replica deployments need
  a shared-storage and concurrency design beyond the included single-container
  Compose setup.
- Access tokens are not refreshable and are stored in browser
  `sessionStorage`.
- Development startup calls `Base.metadata.create_all`, but Alembic migrations
  remain the required schema-management workflow.

## Screenshots

All images below already exist in `assets/screenshots`.

### Frontend

#### Dashboard

![Frontend dashboard](assets/screenshots/frontend-dashboard.png)

#### Candidate management

![Frontend candidates](assets/screenshots/frontend-candidates.png)

#### AI search

![Frontend AI search](assets/screenshots/frontend-ai-search.png)

#### AI assistant

![Frontend assistant](assets/screenshots/frontend-assistant.png)

#### Candidate recommendation

![Frontend recommendation](assets/screenshots/frontend-recommend.png)

#### Analytics

![Frontend analytics](assets/screenshots/frontend-analytics.png)

#### CSV export

![Frontend export](assets/screenshots/frontend-export.png)

### API

#### Resume upload

![Upload API](assets/screenshots/upload-api.png)

#### Candidate filtering and ranking

![Candidate search API](assets/screenshots/search-candidates-api.png)

![Candidate ranking API](assets/screenshots/ranking-api.png)

#### Semantic search

![Semantic search API](assets/screenshots/semantic-search-api.png)

![Semantic search API result](assets/screenshots/semantic-search-api2.png)

#### RAG assistant

![Assistant API](assets/screenshots/assistant-api.png)

![Assistant API result](assets/screenshots/assistant-api2.png)

#### Recommendation

![Recommendation API](assets/screenshots/recommend-api.png)

![Recommendation API result](assets/screenshots/recommend-api2.png)

#### Dashboard and export

![Dashboard summary API](assets/screenshots/dashboard-summary.png)

![Top candidates API](assets/screenshots/top-candidates.png)

![CSV export API](assets/screenshots/csv-export.png)
