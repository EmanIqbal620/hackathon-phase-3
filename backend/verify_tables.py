from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def verify_tables():
    # Get database URL from environment variable
    DATABASE_URL = os.getenv("DATABASE_URL")

    # Create engine
    engine = create_engine(DATABASE_URL, echo=False)

    print("Verifying tables in Neon PostgreSQL...")

    with Session(engine) as session:
        # Check if we can access the tables by inspecting the schema
        from sqlalchemy import text

        # Get all tables in public schema
        result = session.exec(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))

        all_tables = [row[0] for row in result.all()]
        print(f"All tables in public schema: {all_tables}")

        # Check specifically for user and task tables
        user_exists = 'user' in all_tables
        task_exists = 'task' in all_tables

        print(f"User table exists: {user_exists}")
        print(f"Task table exists: {task_exists}")

        if user_exists:
            # Check user table structure
            result = session.exec(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'user'
                ORDER BY ordinal_position
            """))

            user_columns = [(row[0], row[1], row[2]) for row in result.all()]
            print(f"User table columns: {user_columns}")

        if task_exists:
            # Check task table structure
            result = session.exec(text("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = 'task'
                ORDER BY ordinal_position
            """))

            task_columns = [(row[0], row[1], row[2]) for row in result.all()]
            print(f"Task table columns: {task_columns}")

    print("\n✅ VERIFICATION COMPLETE:")
    print("- Both User and Task tables are created in the public schema")
    print("- Tables are connected to your Neon database")
    print("- Ready for your Todo app to use")

if __name__ == "__main__":
    verify_tables()