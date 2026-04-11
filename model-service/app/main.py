import os
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException
from contextlib import asynccontextmanager

from app.model import load_model, transcribe_audio


print("=== STARTING MODEL SERVICE ===")

# --- Lifespan: what happens when the server starts and stops ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    This runs ONCE when server starts.
    It's the perfect place to load out ML Model.

    The 'yield' keyword splits this into two parts:
    - Before yield: runs on startup (load model)
    - After yield: runs on shutdown (cleanup)
    """

    load_model()

    yield  # Server is running and handling requests here

    # SHUTDOWN: Clean up (nothing to do for now)
    print("Shutting down model service...")

app = FastAPI(
    title="Speech-to-text Model Service",
    description="Transcribe audio files using OpenAI Whisper",
    version="1.0.0",
    lifespan=lifespan
)

# --- Health check endpoint ---
@app.get("/health")
def health_check():
    """
    A simple endpoint to check if the service is running.
    """

    return {"status": "healthy", "service": "model-service"}

# --- The main transcription endpoint ---
@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    """
    Recieve an audio file and return its transcribtion.

    How it work:
    1. User send an audio file via POST request
    2. We save it to a temporary file (Whisper needs a file path)
    3. We run Whisper on it
    4. We delete the temp file
    5. We return the transcribtion as JSON
    
    The 'File(...)' tells FastAPI: "This parameter is required"
    """

    # Validate: check that the file looks like audio
    allowed_types = [
        "audio/mpeg",        # .mp3
        "audio/wav",         # .wav
        "audio/x-wav",       # .wav (alternative)
        "audio/ogg",         # .ogg
        "audio/flac",        # .flac
        "audio/webm",        # .webm
        "audio/mp4",         # .m4a
        "audio/x-m4a",       # .m4a (alternative)
        "audio/aac",         # .aac
        "audio/mp4a-latm",   # .m4a (another variant)
    ]
    if audio.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type '{audio.content_type}' is not supported. "
            f"Please upload an audio file (mp3, wav, ogg, flac, webm)."
        )
    
    # Save the uploaded file to a temporary location
    # We use 'tempfile' so the OS picks a safe location
    temp_file = None
    temp_path = None
    try:
        suffix = os.path.splitext(audio.filename)[1] or ".wav"
        
        # Create temp file, write content, and close it completely
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
            dir="."
        )
        temp_path = temp_file.name  # Save the path BEFORE closing
        
        content = await audio.read()
        temp_file.write(content)
        temp_file.close()  # Must close before Whisper can read it

        # Now Whisper can safely open the file
        result = transcribe_audio(temp_path)

        return {
            "success": True,
            "filename": audio.filename,
            "result": result
        }
    
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Transcription failed: {str(error)}"
        )
    
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)