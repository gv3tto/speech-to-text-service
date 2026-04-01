# Speech-to-Text Microservice

![Tests](https://github.com/gv3tto/speech-to-text-service/actions/workflows/tests.yml/badge.svg)

A full-stack speech-to-text application built with a microservice architecture. Upload audio files and get accurate transcriptions powered by OpenAI's Whisper model.

## Architecture

The project follows a microservice pattern with two backend services and a frontend, orchestrated with Docker Compose.

```
┌─────────────┐       ┌──────────────────────────┐       ┌──────────────────┐
│   Frontend   │──────▶│  Orchestration Service    │──────▶│  Model Service    │
│  (Nginx)     │◀──────│  - User registration      │◀──────│  - Whisper model  │
│  Port 3000   │       │  - JWT authentication     │       │  - Transcription  │
│              │       │  - Request routing         │       │  Port 8001        │
└─────────────┘       │  Port 8000                 │       └──────────────────┘
                      └──────────────────────────┘
```

**Model Service** — Loads the Whisper model and exposes a `/transcribe` endpoint. This service handles only ML inference, keeping it isolated and independently scalable.

**Orchestration Service** — The main API gateway. Handles user authentication (register/login with JWT tokens), validates requests, and forwards audio files to the Model Service.

**Frontend** — A simple HTML/CSS/JS interface for user registration, login, audio upload, and displaying transcription results.

## Tech Stack

- **Backend:** Python, FastAPI, SQLAlchemy, SQLite
- **ML Model:** OpenAI Whisper (configurable model size)
- **Authentication:** JWT (JSON Web Tokens) with bcrypt password hashing
- **Frontend:** HTML, CSS, JavaScript (vanilla)
- **Containerization:** Docker, Docker Compose
- **Web Server:** Nginx (frontend), Uvicorn (backend)
- **Testing:** pytest (API tests), Playwright (E2E browser tests)

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- Git

### Run with Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/gv3tto/speech-to-text-service.git
   cd speech-to-text-service
   ```

2. Start all services:
   ```bash
   docker-compose up --build
   ```

3. Open the app:
   - **Frontend:** http://localhost:3000
   - **API Docs:** http://localhost:8000/docs
   - **Model Service Health:** http://localhost:8001/health

4. Register an account, login, and upload an audio file!

### Run Locally (Without Docker)

**Model Service:**
```bash
cd model-service
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

**Orchestration Service:**
```bash
cd orchestration-service
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac/Linux
pip install -r requirements.txt
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**Frontend:**
Open `frontend/index.html` in your browser.

> **Note:** Running locally requires Python 3.12+, FFmpeg, and sufficient disk space for the Whisper model (~75MB for tiny).

## Testing

The project includes two levels of testing:

### API Tests (pytest)

Unit and integration tests for the orchestration service covering authentication, authorization, input validation, and health checks.

```bash
cd orchestration-service
venv\Scripts\activate
python -m pytest tests/ -v
```

**What's tested:**
- User registration (success, duplicate username, missing fields)
- Login (success, wrong password, nonexistent user, token validity)
- Protected endpoint access (no token, invalid token, malformed header)
- Transcription input validation (missing file, auth enforcement)
- Health check endpoint

### E2E Browser Tests (Playwright)

End-to-end tests that automate a real browser to test the complete user journey through the frontend.

```bash
cd e2e-tests
venv\Scripts\activate
python -m pytest test_user_journey.py -v
```

> **Note:** All three services must be running before executing E2E tests.

**What's tested:**
- Page loads correctly with login form visible
- User registration flow (success and duplicate handling)
- Login flow (success, wrong password, empty fields)
- Username appears in header after login
- Logout returns to auth screen
- File upload enables the transcribe button
- Upload area and transcribe button visibility

## API Endpoints

### Authentication

| Method | Endpoint          | Description             | Auth Required |
|--------|-------------------|-------------------------|---------------|
| POST   | `/auth/register`  | Create a new account    | No            |
| POST   | `/auth/login`     | Login and get JWT token | No            |

### Transcription

| Method | Endpoint       | Description              | Auth Required |
|--------|----------------|--------------------------|---------------|
| POST   | `/transcribe`  | Transcribe an audio file | Yes (JWT)     |

### Health Checks

| Method | Endpoint   | Service              |
|--------|------------|----------------------|
| GET    | `/health`  | Both services        |

## Project Structure

```
speech-to-text-service/
├── model-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app, endpoints
│   │   ├── model.py         # Whisper model loading & inference
│   │   └── config.py        # Model configuration
│   ├── Dockerfile
│   └── requirements.txt
│
├── orchestration-service/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI app, CORS setup
│   │   ├── auth.py          # JWT & password hashing
│   │   ├── database.py      # SQLAlchemy setup
│   │   ├── models.py        # User database model
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── auth.py      # Register & login endpoints
│   │       └── transcribe.py # Protected transcription endpoint
│   ├── tests/
│   │   ├── conftest.py      # Test fixtures & test database setup
│   │   ├── test_auth.py     # Authentication & authorization tests
│   │   └── test_transcribe.py # Transcription endpoint tests
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── index.html           # Single-page application
│   └── Dockerfile
│
├── e2e-tests/
│   ├── conftest.py          # Playwright browser fixtures
│   └── test_user_journey.py # Full user journey E2E tests
│
├── docker-compose.yml        # Orchestrates all services
├── .gitignore
└── README.md
```

## Configuration

The Whisper model size can be changed in `model-service/app/config.py`:

| Model  | Size   | Speed   | Accuracy |
|--------|--------|---------|----------|
| tiny   | ~75MB  | Fastest | Basic    |
| base   | ~140MB | Fast    | Good     |
| small  | ~460MB | Medium  | Better   |
| medium | ~1.5GB | Slow    | Great    |
| large  | ~3GB   | Slowest | Best     |

## Supported Audio Formats

MP3, WAV, OGG, FLAC, WebM, M4A
