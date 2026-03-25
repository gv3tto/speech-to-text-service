import httpx
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException

from app.config import MODEL_SERVICE_URL
from app.auth import get_current_user
from app.models import User

router = APIRouter(tags=["Transcription"])

@router.post("/transcribe")
async def transcribe(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user) #this requires login
):
    """
    Transcribe audio — only for authenticated users.
    
    The 'Depends(get_current_user)' is the magic:
    - FastAPI automatically checks for a JWT token
    - If no token or invalid token → 401 error
    - If valid token → we get the user object
    
    Then we forward the audio file to our Model Service.
    """
    
    try:
        # Read the uploaded file
        content = await audio.read()
        
        # Forward to model service using httpx
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{MODEL_SERVICE_URL}/transcribe",
                files={"audio": (audio.filename, content, audio.content_type)}
            )
        
        # Check if model service returned an error
        if response.status_code != 200:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Model service error: {response.text}"
            )
        
        # Return the result with user info
        result = response.json()
        return {
            "user": current_user.username,
            "transcription": result
        }
    
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not connect to model service: {str(e)}"
        )