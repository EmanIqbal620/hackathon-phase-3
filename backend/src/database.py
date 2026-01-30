from sqlmodel import Session
from .config import config
import os

# Defer engine creation until it's actually needed
def get_engine():
    from sqlmodel import create_engine
    return create_engine(config.DATABASE_URL, echo=True)

def get_session():
    """Dependency to get database session"""
    engine = get_engine()
    with Session(engine) as session:
        yield session