from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

# Import routers
from .api.routes import auth, user, tasks
from .api.routers import chat, analytics

app = FastAPI(
    title="Todo App API",
    description="API for todo app with user authentication and task management",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local frontend development
        "https://emaniqbal-todo-phase2.hf.space",  # Deployed frontend
        "http://localhost:8000",  # Local backend (for testing)
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(user.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")

# Public routes that should never require payment
PUBLIC_ROUTES = {
    "/api/login",
    "/api/register",
    "/health",
    "/",
    "/docs",
    "/redoc",
    "/openapi.json",
}

def create_db_and_tables():
    """Create database tables safely."""
    try:
        from .database import get_engine
        engine = get_engine()
        SQLModel.metadata.create_all(engine)
        print("+ Database tables created successfully")
    except Exception as e:
        print(f"! Could not connect to database: {e}")
        print("! The app will run but database functionality may be limited")

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

# Optional: middleware to skip payment verification on public routes
@app.middleware("http")
async def skip_payment_for_public_routes(request, call_next):
    if request.url.path in PUBLIC_ROUTES:
        # Skip subscription/payment check
        response = await call_next(request)
        return response
    # For protected routes, you can add payment/subscription check in router level
    response = await call_next(request)
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
