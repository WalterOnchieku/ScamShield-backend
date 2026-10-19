# ScamShield KE — Backend API

**AI-assisted suspicious message screening for Kenya**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-4169E1?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![scikit--learn](https://img.shields.io/badge/scikit--learn-ML-F7931E?logo=scikitlearn&logoColor=white)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-TBD-lightgrey)](#license)

ScamShield KE is an AI-assisted message-screening project designed to help users identify potentially suspicious SMS messages, job offers, payment requests, and notifications. The backend exposes a REST API that combines a trained machine-learning classifier with a rule-based risk assessment engine, explains detected warning signs, and stores completed analyses for later review.

The project focuses on practical AI engineering: integrating a trained model into an API, validating requests, combining model output with interpretable rules, persisting results in PostgreSQL, testing application behaviour, and preparing the service for deployment.

> **Important:** ScamShield KE provides screening signals, not definitive fraud detection. Its current classifier was trained on the UCI SMS Spam Collection, which is not a Kenya-specific scam dataset. A low-risk result does not guarantee that a message is legitimate, and a high-risk result does not prove fraud.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Project Repositories](#project-repositories)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Technology Stack](#technology-stack)
- [Machine Learning Model](#machine-learning-model)
- [Rule-Based Risk Assessment](#rule-based-risk-assessment)
- [Backend API](#backend-api)
- [Analysis Workflow](#analysis-workflow)
- [Database Design](#database-design)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Environment Configuration](#environment-configuration)
- [Running the Backend](#running-the-backend)
- [Testing and Code Quality](#testing-and-code-quality)
- [API Examples](#api-examples)
- [Deployment Architecture](#deployment-architecture)
- [Deployment Guide](#deployment-guide)
- [Security and Privacy Considerations](#security-and-privacy-considerations)
- [Current Limitations](#current-limitations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Project Overview

Fraudulent messages can use urgency, prize claims, requests for sensitive credentials, advance fees, suspicious links, and threats against accounts to pressure recipients into taking action.

ScamShield KE evaluates submitted messages using two complementary approaches:

1. **Machine learning:** A TF-IDF text representation and Logistic Regression classifier estimate whether a message resembles spam in the training dataset.
2. **Rule-based analysis:** Explicit rules identify selected suspicious message patterns and return findings with severity levels and explanations.

The backend combines these signals into an analysis response containing the predicted label, model scores, overall risk level, risk reasons, detected findings, recommendations, and a disclaimer.

Completed analyses are stored in PostgreSQL, allowing the application to retrieve historical records, inspect individual analyses, and delete records.

### Project objectives

- Build a working machine-learning inference API.
- Integrate model predictions with explainable rule-based screening.
- Expose a clean REST interface for a separate frontend.
- Persist analysis results in a relational database.
- Implement database migrations and repository-layer operations.
- Test API behaviour, prediction logic, risk rules, and database operations.
- Containerize the local PostgreSQL development environment.
- Prepare the backend for deployment on Render with a Supabase-hosted PostgreSQL database.

---

## Project Repositories

ScamShield KE is organized into separate repositories to keep the frontend, backend, and machine-learning workflow independently maintainable.

| Component | Repository | Responsibility |
|---|---|---|
| Backend API | **This repository** | REST endpoints, inference, risk assessment, database operations, validation, and tests |
| Frontend | [ScamShield-frontend](https://github.com/WalterOnchieku/ScamShield-frontend) | User interface for submitting messages and viewing analysis results |
| Machine learning | [ScamShield-ml](https://github.com/WalterOnchieku/ScamShield-ml) | Dataset preparation, model training, evaluation, and model artefacts |

**Live application:** [ScamShield KE — deployed frontend](#deployment-architecture)

The frontend deployment URL will be added here once deployment is complete.

---

## Key Features

### 1. Machine-learning inference

- Loads a trained TF-IDF and Logistic Regression pipeline.
- Predicts `ham` or `spam`.
- Returns ham and spam model scores.
- Uses the same saved model artefact for API inference.
- Keeps model inference separate from persistence and API routing.

### 2. Explainable risk screening

- Checks for selected suspicious patterns using explicit rules.
- Assigns severity levels to detected indicators.
- Returns risk reasons, matched evidence, and recommended precautions.
- Combines model output and rule findings into an overall risk assessment.

### 3. Persistent analysis history

- Saves completed analyses in PostgreSQL.
- Retrieves paginated history.
- Filters history by risk level.
- Retrieves an individual analysis by ID.
- Deletes a saved analysis by ID.

### 4. API validation and documentation

- Uses Pydantic schemas to validate requests and responses.
- Provides interactive API documentation through FastAPI.
- Returns appropriate errors for invalid requests and missing records.

### 5. Development and quality assurance

- Automated tests with pytest.
- Static analysis and linting with Ruff.
- PostgreSQL development environment through Docker Compose.
- Alembic database migrations.

---

## System Architecture

```mermaid
flowchart TD
    A[Next.js Frontend] -->|POST /analyze| B[FastAPI Backend]
    B --> C[Request Validation]
    C --> D[Prediction Service]
    D --> E[TF-IDF + Logistic Regression]
    C --> F[Rule Engine]
    E --> G[Risk Assessment]
    F --> G
    G --> H[Analysis Response]
    G --> I[Analysis Repository]
    I --> J[(PostgreSQL on Supabase)]
    J --> K[Analysis History]
    K -->|GET /history| B
    K -->|GET /history/id| B
    K -->|DELETE /history/id| B
    H --> A
```

### Architecture responsibilities

| Layer | Responsibility |
|---|---|
| API layer | Receives HTTP requests, validates input, and returns responses |
| Schemas | Defines and validates API request and response structures |
| Prediction service | Runs the saved machine-learning pipeline |
| Rule engine | Identifies configured warning patterns |
| Analysis service | Coordinates model predictions, rules, risk assessment, and recommendations |
| Repository | Encapsulates database operations |
| Database models | Represent persisted analysis records |
| Alembic | Manages database schema migrations |

The frontend and backend are independently deployable. The backend does not depend on the Next.js development server to perform inference or store analysis records.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Backend language |
| FastAPI | REST API framework |
| Pydantic | Request and response validation |
| scikit-learn | Text classification pipeline |
| Joblib | Loading the serialized model artefact |
| SQLAlchemy 2.x | Database ORM and session management |
| PostgreSQL | Persistent relational storage |
| Psycopg 3 | PostgreSQL database driver |
| Alembic | Database schema migrations |
| pytest | Automated testing |
| HTTPX | HTTP testing support |
| Ruff | Python linting and code-quality checks |
| Docker Compose | Local PostgreSQL development environment |
| Render | Planned backend hosting |
| Supabase | Planned managed PostgreSQL hosting |

---

## Machine Learning Model

The backend currently uses a baseline classifier trained in the separate machine-learning repository.

### Training dataset

The model was developed using the [UCI SMS Spam Collection](https://archive.ics.uci.edu/dataset/228/sms+spam+collection).

The original dataset contains 5,572 messages. The preparation pipeline removed 403 duplicate rows, leaving 5,169 unique messages.

| Dataset property | Value |
|---|---:|
| Original messages | 5,572 |
| Duplicate rows removed | 403 |
| Unique messages retained | 5,169 |
| Training examples | 4,135 |
| Test examples | 1,034 |
| Split strategy | Stratified 80/20 |
| Random seed | 42 |

The preparation process checks for exact-message overlap between the training and test partitions.

### Model pipeline

The current baseline uses:

- **TF-IDF vectorization** to convert text into numerical features.
- Unigrams and bigrams (`ngram_range=(1, 2)`).
- `min_df=2` to ignore terms appearing in fewer than two documents.
- Sublinear term frequency scaling.
- **Logistic Regression** for classification.
- `class_weight="balanced"` to account for the unequal class distribution.
- `max_iter=1000`.
- `random_state=42`.

The vectorizer and classifier are saved together as a serialized scikit-learn pipeline.

**Model artefact:** `models/scamshield_baseline.joblib`

The backend loads the artefact during application startup. The expected deployment layout places the model at `backend/models/scamshield_baseline.joblib`, relative to the repository's backend directory structure.

### Baseline evaluation

The held-out test-set evaluation produced the following results:

| Metric | Score |
|---|---:|
| Accuracy | 97.68% |
| Spam precision | 90.23% |
| Spam recall | 91.60% |
| Spam F1-score | 90.91% |
| Ham precision | 98.78% |
| Ham recall | 98.56% |
| Ham F1-score | 98.67% |

Confusion matrix:

| Actual class | Predicted ham | Predicted spam |
|---|---:|---:|
| Ham | 890 | 13 |
| Spam | 11 | 120 |

These figures describe performance on the held-out, deduplicated UCI dataset. They must not be interpreted as equivalent performance on Kenyan job scams, M-Pesa fraud, phishing campaigns, or other real-world fraud categories.

### Model score interpretation

The API returns `ham_probability` and `spam_probability` from the classifier's `predict_proba` output.

These are model scores, not calibrated estimates of the real-world probability that a message is fraudulent. The classifier learns patterns associated with the dataset's spam and ham labels; it does not independently verify the sender, the destination of a URL, or the truth of an offer.

---

## Rule-Based Risk Assessment

The rule engine supplements the classifier with explicit, interpretable indicators.

The currently implemented rules cover the following patterns:

| Rule ID | Purpose | Severity |
|---|---|---|
| `urgency_pressure` | Detects urgency or pressure intended to rush a recipient | Medium |
| `unsolicited_prize` | Detects suspicious prize or reward claims | Medium |
| `credential_request` | Detects requests for sensitive credentials, such as PINs | High |
| `advance_fee_request` | Detects requests to pay a fee before receiving a promised benefit | High |
| `suspicious_url_pattern` | Flags selected URL patterns that warrant careful inspection | Medium |
| `account_threat` | Detects threats or warnings involving an account | Medium |

A single message can trigger multiple rules. Each finding can include its rule identifier, category, severity, matched text, and an explanation.

The analysis service uses the classifier output and rule findings to determine the overall risk assessment and recommendations.

### Why combine machine learning and rules?

Machine learning can recognize combinations of text features that resemble examples it has seen during training. Rules provide explicit checks for selected patterns that are important to the application.

This hybrid approach improves explainability, but it also has limitations. Rules can miss unfamiliar wording, and legitimate messages can contain language that resembles a suspicious pattern. Rule findings should therefore be treated as indicators requiring judgement rather than conclusive evidence.

---

## Backend API

The default local API address is:

`http://127.0.0.1:8000`

Interactive documentation is available at `/docs` when the server is running.

### Endpoint reference

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Root endpoint and basic service information |
| `GET` | `/health` | Basic health check |
| `POST` | `/predict` | Performs a model prediction without persisting an analysis |
| `POST` | `/analyze` | Performs a complete risk assessment and stores the result |
| `GET` | `/history` | Retrieves paginated analysis history, optionally filtered by risk |
| `GET` | `/history/{analysis_id}` | Retrieves one saved analysis |
| `DELETE` | `/history/{analysis_id}` | Deletes one saved analysis |

### `GET /health`

Provides a basic endpoint for checking whether the service is responding.

This endpoint should not be treated as a complete dependency-readiness check unless database and model readiness checks are explicitly included in its implementation.

### `POST /predict`

Runs the model prediction without saving an analysis record.

Example request:

```json
{
  "message": "Congratulations, you have won a prize. Pay a processing fee to claim it."
}
```

The prediction response includes the predicted label, ham and spam scores, a screening result, and a disclaimer.

### `POST /analyze`

Runs the complete analysis workflow and persists the result.

The response includes:

- `predicted_label`
- `ham_probability`
- `spam_probability`
- `risk_level`
- `risk_reasons`
- `findings`
- `recommendations`
- `disclaimer`

The complete response structure is defined by the backend's Pydantic schemas and can be inspected in the interactive API documentation.

### `GET /history`

Retrieves saved analyses with pagination and an optional risk-level filter.

Supported query parameters:

| Parameter | Purpose |
|---|---|
| `limit` | Maximum number of records returned |
| `offset` | Number of records skipped |
| `risk_level` | Optional risk-level filter |

For example:

```http
GET /history?limit=10&offset=0&risk_level=high
```

The response contains an `items` array together with the requested `limit` and `offset`.

### `GET /history/{analysis_id}`

Returns a single stored analysis identified by its database ID. A missing record returns `404 Not Found`.

### `DELETE /history/{analysis_id}`

Deletes a saved analysis by ID. A missing record returns `404 Not Found`.

**Privacy note:** The current history API does not provide user authentication or user-scoped records. Until that is implemented, records must not be treated as private per-user data.

---

## Analysis Workflow

A typical request to `/analyze` follows this sequence:

1. The client submits a message to the API.
2. FastAPI validates the incoming request.
3. The prediction service runs the saved classifier.
4. The rule engine checks for configured suspicious patterns.
5. The analysis service combines the available signals into a risk assessment.
6. Recommendations and a disclaimer are included in the result.
7. The repository persists the completed analysis in PostgreSQL.
8. The API returns the result to the client.
9. The record becomes available through the history endpoints.

The `/predict` endpoint provides a lighter-weight inference path that does not persist the completed result.

---

## Database Design

The backend uses PostgreSQL with SQLAlchemy and Alembic.

### Analysis records

The `analysis_records` table stores the information required to reproduce and display a completed screening result.

The current history schema includes:

| Field | Description |
|---|---|
| `id` | Unique analysis identifier |
| `message` | Submitted message text |
| `predicted_label` | Model classification: `ham` or `spam` |
| `ham_probability` | Model score for the ham class |
| `spam_probability` | Model score for the spam class |
| `risk_level` | Overall risk classification |
| `risk_reasons` | List of assessment reasons |
| `findings` | Structured rule-engine findings |
| `recommendations` | List of recommended precautions |
| `created_at` | Analysis creation timestamp |

The SQLAlchemy model defines the database representation, while Pydantic schemas define the response representation. The repository layer handles database queries and persistence.

### Database migrations

Alembic manages changes to the database schema. The initial analysis-records migration has been created and applied successfully in the local development environment.

When deploying to a new database, apply the committed migrations rather than relying on manually creating tables.

### Local PostgreSQL

The local development database runs through Docker Compose using PostgreSQL 16 Alpine.

The development configuration maps host port `5433` to PostgreSQL's container port `5432` and uses a persistent Docker volume named `scamshield_postgres_data`.

Local database credentials are for development only. Do not reuse them as production credentials.

---

## Project Structure

The backend repository contains the API application, model artefact, database migration configuration, and tests.

```text
backend/
├── migrations/
│   └── versions/
│       └── 2ef5d431002f_create_analysis_records_table.py
├── models/
│   └── scamshield_baseline.joblib
├── src/
│   └── scamshield/
│       ├── main.py
│       ├── schemas/
│       │   ├── prediction.py
│       │   ├── analysis.py
│       │   └── history.py
│       ├── services/
│       │   ├── prediction.py
│       │   ├── analysis.py
│       │   └── rule_engine.py
│       ├── db/
│       │   ├── database.py
│       │   └── models.py
│       └── repositories/
│           └── analysis.py
├── tests/
│   ├── test_main.py
│   ├── test_prediction.py
│   ├── test_analysis.py
│   ├── test_analysis_api.py
│   ├── test_rule_engine.py
│   ├── test_analysis_repository.py
│   └── test_analysis_history_api.py
├── docker-compose.yml
├── alembic.ini
└── requirements.txt
```

The exact repository may also include environment templates, development configuration, and other supporting files.

The trained model is kept in the backend's model directory so that the deployed API can load it without needing to retrain the classifier at application startup.

---

## Getting Started

### Prerequisites

Install or prepare the following:

- Python 3.12
- Git
- Docker Engine with Docker Compose, for the local PostgreSQL setup
- A copy of the backend repository
- The trained model artefact in the expected model directory

### 1. Clone the repository

```bash
git clone https://github.com/WalterOnchieku/ScamShield-backend.git
cd ScamShield-backend
```

### 2. Create a virtual environment

Linux, macOS, or WSL:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the project has a separate development requirements file or optional development dependencies, install those according to the repository's current configuration.

### 4. Prepare the model artefact

Ensure this file exists:

```text
models/scamshield_baseline.joblib
```

If the model is maintained in the ML repository, use the trained artefact from that project. The backend expects a compatible scikit-learn pipeline at the configured path.

Do not attempt to load an untrusted Joblib file. Serialized Python objects can execute code during deserialization; only use model artefacts from a trusted source.

### 5. Start PostgreSQL

Start the local database from the backend directory:

```bash
docker compose up -d
```

Check that the database container is running:

```bash
docker compose ps
```

The local database configuration expects PostgreSQL to be available on port `5433`.

### 6. Configure the database connection

Configure the `DATABASE_URL` environment variable if your local settings differ from the development defaults.

Example local connection:

```text
postgresql+psycopg://scamshield:<YOUR_LOCAL_PASSWORD>@localhost:5433/scamshield
```

Replace the placeholder with your actual local password. Do not commit credentials to Git.

### 7. Apply migrations

With the virtual environment active and the database connection configured:

```bash
alembic upgrade head
```

This applies the database schema migrations, including the migration that creates the analysis-records table.

### 8. Start the API

Run:

```bash
uvicorn scamshield.main:app --app-dir src --reload
```

The API should now be available at:

- Base URL: `http://127.0.0.1:8000`
- Interactive documentation: `http://127.0.0.1:8000/docs`
- Alternative documentation: `http://127.0.0.1:8000/redoc`
- Health check: `http://127.0.0.1:8000/health`

The application needs access to both the trained model and the configured database for the full analysis workflow.

---

## Environment Configuration

The backend uses environment-based configuration for deployment flexibility.

| Variable | Purpose | Example or guidance |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | Use a local URL during development and a Supabase connection string in production |
| `PORT` | Hosting platform's HTTP port, if required by the start command | Render commonly provides a `PORT` environment variable |
| `FRONTEND_ORIGIN` | Optional configuration if CORS is made environment-driven | Set to the deployed frontend origin |

`DATABASE_URL` is the database setting used by the database configuration. Verify the other variables against the current application code before relying on them; they are configuration recommendations rather than a claim that all are currently implemented.

Do not commit `.env` files, production database URLs, API credentials, or passwords. Use your hosting provider's environment-variable settings.

For local development, a `.env` file may be used if supported by the application's configuration. Ensure that it is excluded from version control.

---

## Testing and Code Quality

The backend has automated coverage for core API and service behaviour.

The existing test suite covers:

- Root and health endpoints.
- Model prediction behaviour.
- Analysis-service behaviour.
- Analysis API responses.
- Rule-engine matching and non-matching cases.
- Analysis repository operations.
- Analysis-history API behaviour.

The recorded development checkpoint reached **55 passing tests**, with one warning, and Ruff checks passed at that point. This is a historical checkpoint, not a guarantee that the current checkout still passes without changes.

### Run tests

From the backend directory with the virtual environment active:

```bash
pytest
```

### Run Ruff

```bash
python -m ruff check src tests
```

### Test the API manually

Start the API and open:

```text
http://127.0.0.1:8000/docs
```

Use the interactive documentation to submit requests to `/predict`, `/analyze`, and the history endpoints.

### Integration testing

A useful manual integration test is to:

1. Submit a suspicious sample to `/analyze`.
2. Confirm that the response contains a predicted label, risk level, findings, and recommendations.
3. Retrieve `/history` and verify that the record was persisted.
4. Retrieve the individual record by ID.
5. Delete that record and verify that it is no longer available.

---

## API Examples

### Analyze a suspicious message

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "URGENT! You have won a prize. Pay a processing fee to claim it."
  }'
```

The response should contain the fields defined by the current `AnalysisResponse` schema. Exact scores and findings depend on the model artefact and rule-engine implementation.

### Run a model-only prediction

```bash
curl -X POST "http://127.0.0.1:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hi, I will arrive at the office at 10 tomorrow."
  }'
```

### Retrieve analysis history

```bash
curl "http://127.0.0.1:8000/history?limit=10&offset=0"
```

### Filter history by risk

```bash
curl "http://127.0.0.1:8000/history?limit=10&offset=0&risk_level=high"
```

### Retrieve an individual record

Replace `23` with a valid analysis ID:

```bash
curl "http://127.0.0.1:8000/history/23"
```

### Delete a record

```bash
curl -X DELETE "http://127.0.0.1:8000/history/23"
```

---

## Deployment Architecture

The intended public deployment separates the frontend, API, and database.

| Component | Hosting platform | Status |
|---|---|---|
| Next.js frontend | Frontend hosting provider | Deployment URL to be added |
| FastAPI backend | [Render](https://render.com/) | Planned |
| PostgreSQL database | [Supabase](https://supabase.com/) | Planned |

This separation allows each component to be deployed and configured independently.

### Production request flow

1. A visitor opens the deployed frontend.
2. The frontend sends API requests to the public Render backend URL.
3. The backend validates the request and performs inference and rule-based analysis.
4. The backend persists completed analyses to the Supabase PostgreSQL database.
5. The API returns the analysis response to the frontend.

The public frontend URL and backend URL should be configured independently; the frontend must not use a localhost API URL in production.

---

## Deployment Guide

The following steps describe the intended deployment process. They should be checked off only after each deployment stage has been completed and verified.

### 1. Provision the Supabase database

Create a Supabase project and obtain its PostgreSQL connection details.

Configure the backend's `DATABASE_URL` using the connection method recommended by Supabase for your hosting environment. Check whether your selected connection uses direct PostgreSQL access or a pooler, and use the appropriate connection parameters.

The backend uses Psycopg 3 and expects a SQLAlchemy-compatible PostgreSQL URL, such as:

```text
postgresql+psycopg://USER:PASSWORD@HOST:PORT/DATABASE
```

This is a format example, not a real connection string. Use the actual host, port, database name, username, and password supplied by Supabase.

**Important deployment checks:**

- Use a strong, unique database password.
- Keep credentials out of Git and frontend environment variables.
- Confirm that the selected connection method supports the SQLAlchemy and migration workflow.
- Restrict database access where practical.
- Back up important data and understand the provider's recovery options.

### 2. Deploy the backend on Render

Create a new Render web service connected to the backend repository.

Configure the service with the correct repository root and Python environment. Since this repository is structured as a backend project, confirm the service's root directory matches the location of `requirements.txt`, `src/`, `models/`, and `alembic.ini`.

A typical start command is:

```bash
uvicorn scamshield.main:app --app-dir src --host 0.0.0.0 --port $PORT
```

If the service configuration does not expand `$PORT` in a shell, use a start command compatible with Render's runtime environment.

Set the production `DATABASE_URL` in Render's environment settings.

Ensure the model artefact is included in the deployed backend repository or otherwise made available at the exact path expected by the application.

#### Database migrations during deployment

Run the Alembic migration against the production database:

```bash
alembic upgrade head
```

Configure this as an appropriate release or deployment step where supported, rather than relying on manually creating database tables.

Before applying migrations to a production database, verify the target connection and migration history. Avoid running concurrent migrations from multiple application instances.

#### Health checks

Configure Render to check the backend's health endpoint if it is compatible with the platform's health-check expectations.

The current `/health` endpoint provides a basic service check. If deployment requires verification that the model and database are both ready, implement and test those dependency checks explicitly.

### 3. Configure the frontend

The frontend should point to the deployed backend rather than localhost.

For a Next.js deployment, configure:

```text
NEXT_PUBLIC_API_BASE_URL=https://YOUR-BACKEND-SERVICE.onrender.com
```

Replace the example URL with the actual public Render service URL.

The `NEXT_PUBLIC_` prefix means the value is exposed to the browser bundle, so it must never contain secrets. A public API base URL is appropriate; database credentials are not.

After configuring the variable, rebuild and redeploy the frontend if required by its hosting platform.

### 4. Configure CORS

If the frontend and backend use different origins, configure FastAPI's CORS middleware to allow the actual deployed frontend origin.

For example, the production allowlist should contain the real frontend origin:

```text
https://YOUR-DEPLOYED-FRONTEND.example
```

Use the actual deployed hostname rather than the placeholder. Keep local development origins separate from production configuration.

Do not enable unrestricted credentialed cross-origin access. CORS is a browser security mechanism, not a substitute for authentication or API authorization.

### 5. Verify the deployment

Once the services are deployed:

- Open the Render health endpoint.
- Open the public `/docs` page if public API documentation is intended.
- Submit a test message to `/predict`.
- Submit a test message to `/analyze`.
- Verify that a completed analysis is saved in Supabase.
- Retrieve the record through `/history`.
- Verify the individual-record and deletion endpoints.
- Open the frontend and confirm that its API requests target the deployed backend.
- Inspect service logs for model-loading, database, CORS, and migration errors.

Do not publish real user messages or sensitive credentials as deployment test data.

---

## Security and Privacy Considerations

ScamShield KE is a screening tool, and its backend handles submitted message content. A production deployment therefore needs clear data-handling controls.

### Current considerations

**Message retention:** The analysis history currently stores submitted message text alongside predictions and findings. Messages can contain phone numbers, financial details, names, or other sensitive information. Users should be advised to remove sensitive information before submitting messages.

**Shared history:** The current history API does not implement authentication or per-user authorization. Until this is addressed, the history endpoints should not be treated as a private user workspace.

**Deletion:** A record-deletion endpoint exists, but deletion alone does not constitute a complete retention policy, particularly where backups or logs may retain data.

**Database credentials:** Production credentials must be stored in hosting environment settings, not in the repository or frontend code.

**Model artefacts:** Joblib files should only be loaded from trusted sources.

**API abuse:** Public deployment should consider rate limiting, request-size limits, abuse monitoring, and reasonable resource limits.

**Error handling:** Production responses should not expose stack traces, secrets, internal database details, or sensitive message contents unnecessarily.

### Recommended before public launch

- Define and publish a clear retention policy.
- Add authentication and user-scoped authorization before offering private history.
- Review logging to avoid recording complete message contents unnecessarily.
- Configure production CORS explicitly.
- Add rate limiting and abuse protection.
- Verify that database backups and deletion behaviour meet the intended retention policy.
- Document the limitations of the model and rule engine.

---

## Current Limitations

The current implementation is a working project baseline, not a claim of fully production-hardened fraud detection.

1. **Dataset coverage:** The classifier was trained on a general SMS spam dataset rather than a dataset representative of all Kenyan scam types.
2. **Model confidence:** Classifier scores are not calibrated real-world fraud probabilities.
3. **Rule coverage:** The rule engine covers selected patterns and cannot recognize every scam strategy.
4. **False positives and false negatives:** Legitimate messages can be flagged, and malicious messages can pass screening.
5. **Identity and link verification:** The system does not independently verify a sender's identity, validate an offer, or prove that a URL is malicious.
6. **History access control:** Authentication and user-scoped access have not yet been implemented.
7. **Production deployment:** Render and Supabase deployment remains planned until live endpoints and persistence are verified.
8. **Operational resilience:** Production rate limiting, monitoring, and comprehensive dependency-readiness checks remain deployment hardening tasks.

---

## Roadmap

### Completed development milestones

- [x] Audit the UCI SMS Spam Collection.
- [x] Remove exact duplicate messages and prepare stratified training and test datasets.
- [x] Train and evaluate the TF-IDF and Logistic Regression baseline.
- [x] Integrate the serialized model into FastAPI.
- [x] Implement the prediction endpoint.
- [x] Implement a rule-based screening engine.
- [x] Implement the complete analysis endpoint.
- [x] Persist analysis records in PostgreSQL.
- [x] Add history retrieval, filtering, individual-record retrieval, and deletion.
- [x] Add SQLAlchemy models, repository operations, and an Alembic migration.
- [x] Add automated backend tests and Ruff checks.
- [x] Configure a local PostgreSQL development environment with Docker Compose.

### Next priorities

- [ ] Deploy PostgreSQL on Supabase.
- [ ] Deploy the FastAPI backend on Render.
- [ ] Configure production CORS and the frontend API URL.
- [ ] Verify the complete deployed frontend-to-backend-to-database workflow.
- [ ] Add authentication and user-scoped history.
- [ ] Define message retention and privacy controls.
- [ ] Add rate limiting and more comprehensive health checks.
- [ ] Improve evaluation on representative Kenyan scam and legitimate-message examples.
- [ ] Evaluate score calibration and threshold selection.
- [ ] Expand monitoring, deployment automation, and CI/CD checks.

---

## Contributing

Contributions and constructive feedback are welcome.

A useful contribution workflow is:

1. Fork the repository.
2. Create a feature branch.
3. Implement the change with appropriate validation and tests.
4. Run the test suite and Ruff.
5. Open a pull request describing the change and its expected behaviour.

For changes to prediction logic or the rule engine, include tests covering both suspicious and legitimate examples. Avoid treating the presence of a keyword alone as conclusive proof of fraud.

---

## License

A project license has not yet been specified. Until a license is added to the repository, do not assume that the code is available for unrestricted reuse.

