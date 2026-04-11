import os
import time
from faster_whisper import WhisperModel
from app.config import  MODEL_NAME, COMPUTE_TYPE, MODEL_DIR

# This variable will hold our loaded model
whisper_model = None

def load_model():
    """
    Load the Whisper model into memory:
    """

    global whisper_model

    # create model directory if it doens't exist
    os.makedirs(MODEL_DIR, exist_ok=True)

    print(f"Loading faster-whisper model: {MODEL_NAME} (computer_type={COMPUTE_TYPE})...")
    start_time = time.time()

    whisper_model = WhisperModel(
        MODEL_NAME,
        device="cpu",
        compute_type=COMPUTE_TYPE,
        download_root=MODEL_DIR
    )

    duration = time.time() - start_time
    print(f"Model '{MODEL_NAME}' loaded in {duration:.1f}s")


def transcribe_audio(file_path: str) -> dict:
    """
    Transcribe an audio file to text using faster-whisper.
    
    The API of faster-whisper:
    - Returns segments (chunks of text with timestamps)
    - We join them together to get the full text
    - Also returns language detection info
    """

    # Safety check: we make sure the model is loaded
    if whisper_model is None:
        raise RuntimeError("Model is not loaded! Call load_model() first")
    
    start_time = time.time()

    # faster-whisper returns segments and info separately
    segments, info = whisper_model.transcribe(file_path)

    full_text = " ".join(segment.text.strip() for segment in segments)

    duration = time.time() - start_time
    print(f"Transcription completed in {duration:.1f}s (language: {info.language})")

    return {
        "text": full_text,
        "language": info.language
    }

