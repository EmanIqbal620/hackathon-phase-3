from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlmodel import SQLModel
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import your routers
from src.api.routes import tasks, auth, user, ai_agent
from src.api.routes import chat_simple as chat
from src.api.routes import chat_fast
from src.api.routers import analytics
from database import sync_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables at startup with error handling
    try:
        print("=" * 60)
        print("Initializing database...")
        SQLModel.metadata.create_all(bind=sync_engine)
        print("[OK] Database tables created successfully")
        print("=" * 60)
    except Exception as e:
        print("=" * 60)
        print(f"[ERROR] Database initialization error: {e}")
        print("App will continue but database operations may fail")
        print("=" * 60)
        # Don't raise - allow app to start even if DB fails
    yield
    # Cleanup on shutdown (if needed)


app = FastAPI(
    title="Todo App API for Hugging Face",
    lifespan=lifespan,
    docs_url="/docs",  # Enable docs for Hugging Face
    redoc_url="/redoc",  # Enable redoc for Hugging Face
)

# Add CORS middleware - allow specific origins including localhost for development
allowed_origins = (
    os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
)

# Add specific origins for both development and production
allowed_origins.extend(
    [
        "http://localhost:3000",  # Local frontend development
        "https://emaniqbal-todo-phase2.hf.space",  # Deployed frontend on Hugging Face
        "https://emaniqbal-phase-3-chatbot.hf.space",  # Current deployed frontend
        "http://localhost:7860",  # Local backend (correct port)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:7860",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://localhost",
        "https://tobo-app-chatbot.vercel.app",  # Vercel frontend
        "http://127.0.0.1",
    ]
)

# Add Vercel deployment URL for production frontend
vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    allowed_origins.append(f"https://{vercel_url}")
    allowed_origins.append(f"http://{vercel_url}")

# Add custom production domain if set
production_frontend_url = os.getenv("PRODUCTION_FRONTEND_URL")
if production_frontend_url:
    if not production_frontend_url.startswith(("http://", "https://")):
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

# Add GZip compression for faster responses (60-80% smaller)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Include routers
app.include_router(tasks.router, prefix="/api", tags=["Tasks"])
app.include_router(auth.router, prefix="/api", tags=["Authentication"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(chat_fast.router, prefix="/api", tags=["Chat-Fast"])
app.include_router(user.router, prefix="/api", tags=["User"])
app.include_router(ai_agent.router, prefix="/api", tags=["AI Agent"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])

@app.get("/")
def read_root():
    return {
        "message": "Todo App API running on Hugging Face Spaces",
        "service": "backend",
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "platform": "huggingface-spaces"}

@app.get("/debug")
def debug_info():
    """Debug endpoint to check configuration and diagnose issues"""
    import os

    # Check database connection
    try:
        from database import sync_engine
        db_status = "connected"
        db_url = os.getenv("DATABASE_URL", "NOT_SET")
        # Mask password in URL for security
        if "@" in db_url and "://" in db_url:
            parts = db_url.split("@")
            user_pass = parts[0].split("://")[1]
            if ":" in user_pass:
                user = user_pass.split(":")[0]
                db_url_masked = db_url.replace(user_pass, f"{user}:****")
            else:
                db_url_masked = db_url
        else:
            db_url_masked = "NOT_SET" if db_url == "NOT_SET" else "INVALID_FORMAT"
    except Exception as e:
        db_status = f"error: {str(e)}"
        db_url_masked = "ERROR"

    return {
        "status": "debug_info",
        "database": {
            "status": db_status,
            "url_format": db_url_masked,
        },
        "environment_variables": {
            "JWT_SECRET": "SET" if os.getenv("JWT_SECRET") else "NOT_SET",
            "BETTER_AUTH_SECRET": "SET" if os.getenv("BETTER_AUTH_SECRET") else "NOT_SET",
            "DATABASE_URL": "SET" if os.getenv("DATABASE_URL") else "NOT_SET",
            "OPENROUTER_API_KEY": "SET" if os.getenv("OPENROUTER_API_KEY") else "NOT_SET",
            "AI_PROVIDER": os.getenv("AI_PROVIDER", "NOT_SET"),
        },
        "cors": {
            "allowed_origins_count": len(allowed_origins),
            "origins": allowed_origins,
        },
        "routes": {
            "auth": "registered",
            "tasks": "registered",
            "chat": "registered",
            "user": "registered",
            "ai_agent": "registered",
            "analytics": "registered",
        }
    }

# For Hugging Face Spaces, make sure the app is available at the global level
# The app will be run with uvicorn by Hugging Face
if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
