from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import User
from app.auth import hash_password, verify_password, create_access_token
from app.logger import get_logger
from app.metrics import metrics

logger = get_logger("auth")

# APIRouter lets us group related endpoints together
router = APIRouter(prefix="/auth", tags=["Authentication"])

# --- Request/Response schemas ---
# These define what data the endpoints expect and return
class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    message: str

class Token(BaseModel):
    access_token: str
    token_type: str


# --- Endpoints ---
@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user account.
    
    Steps:
    1. Check if username already exists
    2. Hash the password
    3. Save to database
    4. Return success message
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user with hashed password
    new_user = User(
        username=user_data.username,
        hashed_password=hash_password(user_data.password)
    )

    logger.info(f"New user registered: {user_data.username}")
    
    db.add(new_user)
    db.commit()
    
    # Fetch the user back from DB to get the auto-generated id
    saved_user = db.query(User).filter(User.username == user_data.username).first()
    
    return UserResponse(
        id=saved_user.id,
        username=saved_user.username,
        message="User created successfully!"
    )

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Log in and receive a JWT token.
    
    Steps:
    1. Find the user by username
    2. Verify their password
    3. Create and return a JWT token
    """

    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for: {form_data.username}")
        metrics.record_failed_login(form_data.username)
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    # Create token with the username inside it
    access_token = create_access_token(data={"sub": user.username})

    logger.info(f"User logged in: {form_data.username}")

    return Token(access_token=access_token, token_type="bearer")