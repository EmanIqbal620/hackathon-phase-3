"""
Script to create database tables in Neon PostgreSQL
"""
import os
from dotenv import load_dotenv
from sqlmodel import SQLModel
from sqlalchemy import create_engine

# Load environment variables
load_dotenv()

# Get database URL from environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("DATABASE_URL environment variable is required")

print(f"Connecting to database: {database_url.replace('@', '***@')}")  # Mask password for security

# Create engine
engine = create_engine(database_url)

def create_tables():
    """Create all tables in the database."""
    print("Importing models...")
    from src.models.user import User
    from src.models.task import Task
    from src.models.conversation import Conversation, Message

    print("Creating tables...")
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully!")

    # Verify tables were created
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables in database: {tables}")

if __name__ == "__main__":
    create_tables()