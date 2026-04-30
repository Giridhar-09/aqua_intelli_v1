"""
AquaIntelli - Application Configuration
Centralizes all env vars and settings.
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # ── Server ──
    APP_NAME: str = "AquaIntelli"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    PORT: int = 8001
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://127.0.0.1:8001"

    # ── SQL Database (SQLite for dev, PostgreSQL for prod) ──
    SQL_DATABASE_URL: str = "sqlite+aiosqlite:///./aquaintelli.db"

    # ── NoSQL Database (MongoDB) ──
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "aquaintelli"
    MONGO_MOCK: bool = True  # Use mongomock for dev without MongoDB

    # ── Neo4j Graph Database ──
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "aquaintelli"
    NEO4J_MOCK: bool = True  # Use mock for dev without Neo4j

    # ── NASA EarthData ──
    EARTHDATA_TOKEN: str = ""
    EARTHDATA_USERNAME: str = ""

    # ── Google Earth Engine ──
    GEE_PROJECT: str = ""
    GEE_SERVICE_ACCOUNT: str = ""
    GEE_KEY_PATH: str = "configs/gee_credentials.json"

    # ── OpenWeatherMap ──
    OPENWEATHER_API_KEY: str = ""

    # ── LLM / GenAI ──
    OPENAI_API_KEY: str = ""
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_STORE_PATH: str = "data/vectorstore"

    # ── LangSmith ──
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "aquaintelli"

    # ── Data Paths ──
    DATA_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    CGWB_DATA_PATH: str = "data/cgwb/cgwb_district_gw_2022.json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
