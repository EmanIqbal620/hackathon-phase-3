import asyncio
from sqlmodel import SQLModel, create_engine, text
from models import User, Task
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/todoapp")

print(f"Connecting to database: {DATABASE_URL}")

try:
    # Create sync engine
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=300,
    )

    # Test the connection
    with engine.connect() as conn:
        print("+ Database connection successful!")

        # Check if tables exist
        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """))

        tables = [row[0] for row in result.fetchall()]
        print(f"Tables: {tables}")

        # Check if our tables exist
        user_exists = 'user' in [t.lower() for t in tables]
        task_exists = 'task' in [t.lower() for t in tables]

        print(f"User table exists: {user_exists}")
        print(f"Task table exists: {task_exists}")

        if not user_exists or not task_exists:
            print("Creating tables...")
            SQLModel.metadata.create_all(bind=engine)

            # Check again
            result = conn.execute(text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """))

            tables = [row[0] for row in result.fetchall()]
            print(f"Tables after creation: {tables}")

            user_exists = 'user' in [t.lower() for t in tables]
            task_exists = 'task' in [t.lower() for t in tables]
            print(f"User table exists after creation: {user_exists}")
            print(f"Task table exists after creation: {task_exists}")

        # Check table structure if they exist
        if user_exists:
            result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'user'"))
            user_columns = [(row[0], row[1]) for row in result.fetchall()]
            print(f"User table columns: {user_columns}")

        if task_exists:
            result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'task'"))
            task_columns = [(row[0], row[1]) for row in result.fetchall()]
            print(f"Task table columns: {task_columns}")

except Exception as e:
    print(f"Database connection failed: {e}")
    print("Make sure your Neon database URL is correct and you have the proper credentials.")