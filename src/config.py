# src/config.py
from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class Settings(BaseSettings):
    # API Keys
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    # OpenAI key in .env is an optional fallback
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")

    # Pinecone - We now need two separate indexes
    PINECONE_API_KEY: str = os.getenv("PINECONE_API_KEY")
    PINECONE_INDEX_NAME_OPENAI: str = "policy-rag-openai"
    PINECONE_INDEX_NAME_GOOGLE: str = "policy-rag-google"
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY")

    # Service API Key for authenticating Gemini-only requests
    SERVICE_API_KEY: str = os.getenv("SERVICE_API_KEY")

    class Config:
        case_sensitive = True

settings = Settings()