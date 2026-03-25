from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone

from app.database import Base


class User(Base):
    """
    This class becomes a database table called "users".

    Each attributre becomes a column:
    - id: unique numver for each user (auto-incremented)
    - username: their chosen username (must be unique)
    - hashed_password: their password after hashing
    - created_at: when they register
    """

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))