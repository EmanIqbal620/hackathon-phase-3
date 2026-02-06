from sqlmodel import create_engine, SQLModel
from sqlalchemy.pool import QueuePool
import os
from backend.src.models import User, Task, Conversation, Message  # Import models

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