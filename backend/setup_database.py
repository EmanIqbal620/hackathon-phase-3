"""
Database setup script for Todo App
This script will create all necessary tables in your Neon database
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_environment():
    """Check if environment variables are properly set."""
    required_vars = ['DATABASE_URL']
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print("❌ Error: Missing required environment variables:")
        for var in missing_vars:
            print(f"  - {var}")
        print("\nPlease set these variables in your .env file.")
        print("For Neon database, your DATABASE_URL should look like:")
        print("postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/dbname?sslmode=require")
        return False

    print("✅ Environment variables are properly set")
    return True

def test_connection():
    """Test the database connection."""
    try:
        from sqlalchemy import create_engine, inspect
        from sqlmodel import SQLModel

        database_url = os.getenv("DATABASE_URL")
        print(f"Attempting to connect to: {database_url.split('@')[1].split('/')[0] if '@' in database_url else 'unknown'}")

        engine = create_engine(database_url)

        # Test the connection
        with engine.connect() as conn:
            pass  # If this doesn't raise an exception, connection is successful

        print("✅ Database connection successful")
        return engine
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return None

def create_tables(engine):
    """Create all required tables."""
    try:
        from sqlmodel import SQLModel
        from src.models.user import User
        from src.models.task import Task

        print("Creating tables in database...")
        SQLModel.metadata.create_all(engine)

        # Verify tables were created
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        print(f"✅ Tables created successfully!")
        print(f"Tables in database: {tables}")

        if 'user' in tables or 'users' in tables:
            print("✅ User table exists")
        else:
            print("⚠️  User table may not exist")

        if 'task' in tables or 'tasks' in tables:
            print("✅ Task table exists")
        else:
            print("⚠️  Task table may not exist")

        return True
    except Exception as e:
        print(f"❌ Failed to create tables: {str(e)}")
        return False

def main():
    print("🚀 Todo App Database Setup")
    print("=" * 40)

    # Check environment
    if not check_environment():
        return False

    # Test connection
    engine = test_connection()
    if not engine:
        return False

    # Create tables
    success = create_tables(engine)
    if not success:
        return False

    print("\n🎉 Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Make sure your .env file has the correct DATABASE_URL for your Neon database")
    print("2. Run the application with: python -m src.main")
    print("3. The application will automatically manage the database tables on startup")

    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)