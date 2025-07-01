from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Add connection pool and timeout settings for better reliability
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using them
    pool_size=5,         # Number of connections to maintain in pool
    max_overflow=10,     # Maximum overflow connections allowed
    connect_args={
        "connect_timeout": 30,  # Connection timeout in seconds
        "options": "-c statement_timeout=30000"  # Query timeout in milliseconds
    }
)

# Create SessionLocal class for database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for our models
Base = declarative_base()

# Dependency to get database session
def get_db():
    """
    Dependency that provides a database session.
    This will be used by FastAPI's dependency injection system.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 