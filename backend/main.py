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
allowed_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []

# Add specific origins for both development and production
allowed_origins.extend([
    "http://localhost:3000",  # Local frontend development
    "https://emaniqbal-todo-phase2.hf.space",  # Deployed frontend on Hugging Face
    "http://localhost:8000",  # Local backend (for testing)
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
])

# Add Vercel deployment URL for production frontend
vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    allowed_origins.append(f"https://{vercel_url}")
    allowed_origins.append(f"http://{vercel_url}")

# Add custom production domain if set
production_frontend_url = os.getenv("PRODUCTION_FRONTEND_URL")
if production_frontend_url:
    if not production_frontend_url.startswith(('http://', 'https://')):
        production_frontend_url = f"https://{production_frontend_url}"
    allowed_origins.append(production_frontend_url)

# Remove duplicates while preserving order
seen = set()
unique_origins = []
for origin in allowed_origins:
    origin = origin.strip()
    if origin and origin not in seen:
        seen.add(origin)
        unique_origins.append(origin)

# Ensure no empty strings made it in
allowed_origins = [origin for origin in unique_origins if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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