from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

# Import routes but handle database initialization carefully
from .api.routes import auth, user, tasks

app = FastAPI(
    title="Todo App API",
    description="API for todo app with user authentication and task management",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")

def create_db_and_tables():
    """Create database tables - called safely."""
    try:
        from .database import engine
        SQLModel.metadata.create_all(engine)
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"⚠️  Could not connect to database: {e}")
        print("⚠️  The app will run but database functionality may be limited")

@app.on_event("startup")
def on_startup():
    """Initialize database tables on startup."""
    create_db_and_tables()

@app.get("/")
def read_root():
    return {"message": "Todo App Service"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)