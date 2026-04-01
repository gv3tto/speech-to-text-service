# Speech-to-Text Microservice

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
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── index.html           # Single-page application
│   └── Dockerfile
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

## What I Learned

This project was my first full-stack application. Key concepts I practiced:

- **Microservice Architecture** — Separating ML inference from business logic for independent scaling
- **REST API Design** — Building clean endpoints with FastAPI
- **Authentication** — Implementing JWT-based auth with secure password hashing (bcrypt)
- **Docker** — Containerizing services and orchestrating them with Docker Compose
- **Inter-service Communication** — Services talking to each other over HTTP
- **ML in Production** — Loading and serving an ML model behind an API

## License

This project is open source and available under the [MIT License](LICENSE).
