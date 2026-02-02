import os
from dotenv import load_dotenv
from loguru import logger

load_dotenv()

class Settings:
    # App
    APP_NAME = "timesheets-companion"
    APP_VERSION = "2.0.0"
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
    
    # AI
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    AI_MODEL = "meta-llama/llama-3.3-70b-instruct:free"

settings = Settings()
