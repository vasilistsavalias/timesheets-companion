from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from src.config.settings import settings
from loguru import logger
import time

Base = declarative_base()

class DatabaseManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._init_db()
        return cls._instance

    def _init_db(self):
        try:
            self.engine = create_engine(
                settings.DATABASE_URL,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10
            )
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            logger.info("Database connection established.")
        except Exception as e:
            logger.critical(f"Failed to connect to database: {e}")
            raise

    def get_db(self) -> Session:
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)

# Dependency for Streamlit/FastAPI
def get_db_session():
    manager = DatabaseManager()
    return next(manager.get_db())
