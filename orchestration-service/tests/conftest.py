import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

# --- Test database setup ---
# We use a SEPARATE database for tests so we don't mess up real data

TEST_DATABASE_URL = "sqlite:///./test_user.db"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestSesstionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)

def override_get_db():
    """
    This replaces the real database with our test database.
    Every test gets a clean database session.
    """
    db = TestSesstionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Fixtures ---

@pytest.fixture(scope="function")
def client():
    """
    Creates a fresh test client for each test.
    
    What this does:
    1. Creates all tables in the TEST database
    2. Overrides the app's database with our test database
    3. Gives the test a client to make requests with
    4. After the test, drops all tables (clean slate)
    
    'scope="function"' means this runs for EVERY test function.
    Each test starts with an empty database — no leftover data.
    """
    # Create tables
    Base.metadata.create_all(bind=test_engine)

    # Override the database dependency
    app.dependency_overrides[get_db] = override_get_db

    # Create the test client
    test_client = TestClient(app)

    # Give it to the test
    yield test_client

    # Cleanup after the test
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)

    # Remove the test database file
    if os.path.exists("./test_users.db"):
        os.remove("./test_users.db")


@pytest.fixture
def registered_user(client):
     """
    A fixture that creates a registered user and returns the credentials.
    
    Many tests need a user to already exist (like login tests).
    Instead of repeating the registration in every test,
    we do it once here and reuse it.
    """
     user_data = {
         "username": "testuser",
         "password": "testpass123"
     }
     client.post("/auth/register", json=user_data)
     return user_data

@pytest.fixture
def auth_token(client, registered_user):
    """
    A fixture that returns a valid JWT token.
    
    This builds on registered_user — first creates a user,
    then logs in to get a token. Tests that need authentication
    can use this directly.
    """
    response = client.post(
        "/auth/login",
        data={
            "username": registered_user["username"],
            "password": registered_user["password"]
        }
    )
    return response.json()["access_token"]

