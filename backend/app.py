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
allowed_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []

# Add specific origins for both development and production
allowed_origins.extend([
    "http://localhost:3000",  # Local frontend development
    "https://emaniqbal-todo-phase2.hf.space",  # Deployed frontend on Hugging Face
    "http://localhost:7860",  # Local backend (correct port)
    "http://127.0.0.1:3000",
    "http://127.0.0.1:7860",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://localhost",
    "http://127.0.0.1"
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