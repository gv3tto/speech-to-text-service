from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from app.database import get_db
from app.models import User

# --- Password hashing ---
# bcrypt is a one-way hash: you can hash a password but never "unhash" it
# To verify, you hash the input again and compare the hashes
pwd_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")

def hash_password(password: str) -> str:
    """Turn a plain password into a secure hash."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Check if a plain password matches a hash."""
    return pwd_context.verify(plain_password, hashed_password)

# --- JWT tokens ---
# This tells FastAPI: "look for the token in the Authorization header"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def create_access_token(data: dict) -> str:
    """
    Create a JWT token.

    A JWT token is like a signed ID card:
    - It contains data (who you are)
    - It has an expiration time
    - It's signed with out SECRET_KEY so nobody can fake it
    """

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    """
    This function runs BEFORE any protected endpoint.

    It:
    1. Extracts the JWT token from the request header
    2. Decodes it to get the username
    3. Looks up the user in the database
    4. Returns the user (or raises an error)
    
    FastAPI calls this automatically thanks to 'Depends()'    
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user