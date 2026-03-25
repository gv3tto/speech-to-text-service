from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import DATABASE_URL

# Create the database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Base is the parent class for all out database models
class Base(DeclarativeBase):
    pass

def get_db():
    """
    Creates a database session for each request.

    The 'yield' makes this a generator - FastAPI uses it to:
    1. Create a session before handling the request
    2. Give it to the endpoint function
    3. Close it after the response is sent

    This patter is called "dependency injection"
    """
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()