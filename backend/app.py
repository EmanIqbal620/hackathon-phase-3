from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your routers
from api.routers import tasks, auth
from database import sync_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables at startup
    SQLModel.metadata.create_all(bind=sync_engine)
    yield
    # Cleanup on shutdown (if needed)

app = FastAPI(
    title="Todo App API for Hugging Face",
    lifespan=lifespan,
    docs_url="/docs",  # Enable docs for Hugging Face
    redoc_url="/redoc"  # Enable redoc for Hugging Face
)

# Add CORS middleware - allow specific origins including localhost for development
allowed_origins = os.getenv("ALLOWED_ORIGINS", "*").split(",") if os.getenv("ALLOWED_ORIGINS") else ["*"]

# Add localhost for development if in development mode
if os.getenv("ENVIRONMENT") == "development" or "*" in allowed_origins:
    # For development, allow localhost with common ports
    allowed_origins.extend([
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://localhost",
        "http://127.0.0.1"
    ])

# Remove duplicates while preserving order
seen = set()
unique_origins = []
for origin in allowed_origins:
    origin = origin.strip()
    if origin and origin not in seen:
        seen.add(origin)
        unique_origins.append(origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=unique_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
app.include_router(auth.router, prefix="/api", tags=["Authentication"])

@app.get("/")
def read_root():
    return {"message": "Todo App API running on Hugging Face Spaces", "service": "backend"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "platform": "huggingface-spaces"}

# For Hugging Face Spaces, make sure the app is available at the global level
# The app will be run with uvicorn by Hugging Face
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)