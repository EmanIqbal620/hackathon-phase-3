from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

from api.routers import tasks, auth
from database import sync_engine

# Load environment variables
load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables at startup
    SQLModel.metadata.create_all(bind=sync_engine)
    yield
    # Cleanup on shutdown (if needed)

app = FastAPI(title="Todo App API", lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
app.include_router(auth.router, prefix="/api", tags=["Authentication"])

@app.get("/")
def read_root():
    return {"message": "Todo App API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}