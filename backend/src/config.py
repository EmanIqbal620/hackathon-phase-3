import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class to store environment variables and app settings."""

    # JWT Configuration
    JWT_SECRET = os.getenv("JWT_SECRET", "")
    if not JWT_SECRET:
        raise ValueError("JWT_SECRET environment variable is required")

    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))

    # Better Auth Configuration
    BETTER_AUTH_SECRET = os.getenv("BETTER_AUTH_SECRET", "")
    if not BETTER_AUTH_SECRET:
        raise ValueError("BETTER_AUTH_SECRET environment variable is required")

    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./todo_app.db")  # Default to SQLite for development

# Create a global config instance
config = Config()