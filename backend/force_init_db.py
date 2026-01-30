from sqlmodel import SQLModel, create_engine
from models import User, Task  # your SQLModel classes
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get the exact same database URL used by the application
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://username:password@localhost:5432/todoapp")

print(f"Connecting to database: {DATABASE_URL}")

# Create engine with the same settings as the main application
engine = create_engine(DATABASE_URL, echo=True)

print("Forcing table creation...")
# This explicitly creates all tables defined in SQLModel metadata
SQLModel.metadata.create_all(engine)
print("Tables created or verified successfully")

# Let's also check what tables exist
from sqlalchemy import text
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """))

    tables = [row[0] for row in result.fetchall()]
    print(f"All tables in database: {tables}")

    # Specifically check for our tables
    user_exists = 'user' in [t.lower() for t in tables]
    task_exists = 'task' in [t.lower() for t in tables]

    print(f"User table exists: {user_exists}")
    print(f"Task table exists: {task_exists}")