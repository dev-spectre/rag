# src/database.py
from sqlalchemy import create_engine, text, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .config import settings
import datetime

# Setup SQLAlchemy
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define the APIKey table model
class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

def is_valid_api_key(api_key: str) -> bool:
    """Checks if the provided API key is valid by querying the database."""
    db = SessionLocal()
    try:
        key_exists = db.query(APIKey).filter(APIKey.key == api_key).first()
        return key_exists is not None
    finally:
        db.close()