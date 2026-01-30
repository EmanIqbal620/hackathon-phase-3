from sqlmodel import SQLModel, Field, create_engine, Session
from typing import Optional
import os

# Define the User model
class User(SQLModel, table=True):
    __tablename__ = "user"
    __table_args__ = {"schema": "public"}

    id: str = Field(primary_key=True)
    email: str = Field(unique=True, nullable=False)
    password_hash: str = Field(nullable=False)
    name: Optional[str] = Field(default=None)
    is_active: bool = Field(default=True)


# Define the Task model
class Task(SQLModel, table=True):
    __tablename__ = "task"
    __table_args__ = {"schema": "public"}

    id: str = Field(primary_key=True)
    user_id: str = Field(foreign_key="public.user.id", nullable=False)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    is_completed: bool = Field(default=False)


def main():
    # Database URL from your environment - this matches your .env file
    DATABASE_URL = ""

    # Create engine
    engine = create_engine(DATABASE_URL, echo=True)

    # Create all tables
    print("Creating tables in Neon PostgreSQL...")
    SQLModel.metadata.create_all(bind=engine)
    print("Tables created successfully!")

    # Verify tables were created
    with Session(engine) as session:
        print("Verifying table creation...")

        # Check if we can access the tables by inspecting the schema
        from sqlalchemy import text
        result = session.exec(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('user', 'task')
        """))

        created_tables = [row[0] for row in result.all()]
        print(f"Tables found in public schema: {created_tables}")

    print("Database setup completed successfully!")
    print("- User table created with columns: id, email, password_hash, name, is_active")
    print("- Task table created with columns: id, user_id, title, description, is_completed")
    print("- Both tables are in the public schema")


if __name__ == "__main__":
    main()