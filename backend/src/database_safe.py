from sqlmodel import Session
from .config import config
import os

# Create database engine function (only when called)
def get_engine():
    from sqlmodel import create_engine
    return create_engine(config.DATABASE_URL, echo=True)

def get_session():
    """Dependency to get database session"""
    from sqlmodel import create_engine
    engine = create_engine(config.DATABASE_URL, echo=True)
    with Session(engine) as session:
        yield session