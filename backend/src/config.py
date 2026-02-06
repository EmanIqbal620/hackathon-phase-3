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

    # AI Provider Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openrouter/auto")  # Auto-select best model

    # AI Provider Selection
    AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")  # Can be 'openai' or 'openrouter'

# Create a global config instance
config = Config()