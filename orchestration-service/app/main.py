from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import Base
from app.routes import auth, transcribe
from app.middleware import LoggingMiddleware
from app.logger import get_logger
from app.metrics import metrics

logger = get_logger("main")

# Create all database tables on startup
# This looks at our User model and creates the "users" table
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Speech-to-Text Orchestration Service",
    description="Authentication and transcription routing",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

# Register our route groups
app.include_router(auth.router)
app.include_router(transcribe.router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "orchestration-service"}


@app.get("/metrics")
def get_metrics():
    """
    Returns current application metrics.
    
    This endpoint lets us to check:
    - Average response times
    - Whether the model service is healthy
    - Active alerts
    - Recent error count
    """
    return metrics.get_status()


logger.info("Orchestration service started")