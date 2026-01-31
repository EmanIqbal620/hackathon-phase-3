from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.pool import QueuePool, NullPool
from .models import Task, User
from .models.performance import PerformanceMetrics
from .models.accessibility import AccessibilitySettings
from .models.ux_enhancement import UXEnhancement
from .models.micro_feature import MicroFeature, UserMicroFeaturePreference
from .config import config
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration for connection pooling
POOL_SIZE = 20  # Number of connections to maintain in the pool
MAX_OVERFLOW = 30  # Additional connections beyond pool_size
POOL_TIMEOUT = 30  # Seconds to wait before giving up on getting a connection
POOL_RECYCLE = 3600  # Seconds after which to recreate connections
POOL_PRE_PING = True  # Verify connections before using them

# Create sync engine with connection pooling for use throughout the application
sync_engine = create_engine(
    config.DATABASE_URL,
    echo=False,  # Set to True for debugging SQL queries
    poolclass=QueuePool,  # Use QueuePool for thread-safe connection pooling
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=POOL_PRE_PING,  # Validates connections before use
    connect_args={
        "connect_timeout": 20,  # Timeout for establishing connections
    }
)

def create_db_and_tables():
    """Create all database tables based on SQLModel definitions"""
    SQLModel.metadata.create_all(sync_engine)
    logger.info(f"Database tables created successfully with connection pooling configured: "
                f"pool_size={POOL_SIZE}, max_overflow={MAX_OVERFLOW}, "
                f"pool_timeout={POOL_TIMEOUT}, pool_recycle={POOL_RECYCLE}")

def get_session():
    """Dependency to get database session"""
    with Session(sync_engine) as session:
        yield session

def get_connection_pool_stats():
    """
    Get statistics about the current connection pool.

    Returns:
        Dictionary with pool statistics
    """
    pool = sync_engine.pool
    return {
        "pool_size": pool.size(),
        "checked_out": pool.checkedout(),
        "overflow": pool.overflow(),
        "pool_timeout": pool.timeout,
        "recycle_cutoff_time": getattr(pool, '_recycle_cutoff', 'N/A'),
    }

def dispose_engine():
    """
    Dispose of the database engine and close all connections.
    This should be called when shutting down the application.
    """
    logger.info("Disposing database engine and closing all connections...")
    sync_engine.dispose()
    logger.info("Database engine disposed successfully")

# Initialize the database and tables when this module is imported
try:
    create_db_and_tables()
    logger.info("Database initialized successfully with connection pooling")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    raise