"""Initialize the database tables."""
from sqlmodel import SQLModel
from .src.database import engine
from .src.models.user import User
from .src.models.task import Task

def init_db():
    """Create database tables."""
    print("Creating database tables...")
    SQLModel.metadata.create_all(engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()