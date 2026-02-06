from sqlmodel import create_engine, SQLModel
from sqlalchemy.pool import QueuePool
import os
# Import all models to ensure they're registered with SQLModel's metadata
from src import models

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/todoapp")

# Create sync engine for table creation
sync_engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300,
)

def create_tables():
    """Create all database tables"""
    SQLModel.metadata.create_all(sync_engine)