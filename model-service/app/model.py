import whisper
from app.config import  MODEL_NAME

# This variable will hold our loaded model
whisper_model = None

def load_model():
    """
    Load the Whisper model into memory:

    We do this once when the server starts, not on every request.
    Why? Because loading a model taks a several seconds.
    If we loaded it on every request, each user would wait extra time.
    
    """

    global whisper_model
    
    print(f"Loading Whisper model: {MODEL_NAME}...")
    whisper_model = whisper.load_model(MODEL_NAME)
    print(f"Model '{MODEL_NAME}' loaded successfully!")

def transcribe_audio(file_path: str) -> dict:
    """
    Transcribe an audio file to text.

    Parameters:
        file_path: path to the audio file on disk

    Returns:
        A dictionary with the transcribtion result

    Example return value:
        {
            "text": "Hello, how are you?",
            "language": "en"
        }
    """

    # Safety check: we make sure the model is loaded
    if whisper_model is None:
        raise RuntimeError("Model is not loaded! Call load_model() fist")
    
    # Run the model on the audio file
    result = whisper_model.transcribe(file_path)

    # Return a clean dictionary with just what we need
    return{
        "text": result["text"].strip(),
        "language": result["language"]
    }

