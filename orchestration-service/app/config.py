import os
from dotenv import load_dotenv

# Load settings from .env file
load_dotenv()

# Database
DATABASE_URL = "sqlite:///./users.db"

# JWT Settings
SECRET_KEY = os.getenv("SECRET_KEY", "Super-Secret-Key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Model Service URL — where our Whisper service is running
MODEL_SERVICE_URL = os.getenv("MODEL_SERVICE_URL", "http://127.0.0.1:8001")

# Email Alert Settings
ALERT_EMAIL_FROM = os.getenv("ALERT_EMAIL_FROM")
ALERT_EMAIL_PASSWORD = os.getenv("ALERT_EMAIL_PASSWORD")
ALERT_EMAIL_TO = os.getenv("ALERT_EMAIL_TO")