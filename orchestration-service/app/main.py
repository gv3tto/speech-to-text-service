from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from app.database import engine
from app.models import Base
from app.routes import auth, transcribe

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


# Register our route groups
app.include_router(auth.router)
app.include_router(transcribe.router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "orchestration-service"}