import os
from dotenv import load_dotenv

# Load settings from .env file
load_dotenv()

# Database
DATABASE_URL = "sqlite:///./users.db"

# JWT Settings
# SECRET_KEY is used to sign tokens — keep it secret!
# In production, this comes from .env file
SECRET_KEY = os.getenv("SECRET_KEY", "Super-Secret-Key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Model Service URL — where our Whisper service is running
MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL", "http://127.0.0.1:8001")
