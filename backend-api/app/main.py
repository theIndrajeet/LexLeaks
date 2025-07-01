from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import engine
from . import models
from .routers import posts, auth


# Create database tables
def create_tables():
    models.Base.metadata.create_all(bind=engine)


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    yield
    # Shutdown (if needed)


# Create FastAPI application
app = FastAPI(
    title="LexLeaks API",
    description="Backend API for the LexLeaks whistleblowing platform",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js development server
        "https://lexleaks.com",   # Production domain
        "https://www.lexleaks.com",  # Production domain with www
        # Add your actual production domain here
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(posts.router, prefix="/api")


# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to LexLeaks API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


# API info endpoint
@app.get("/api")
async def api_info():
    return {
        "message": "LexLeaks API v1.0.0",
        "endpoints": {
            "authentication": "/api/auth",
            "posts": "/api/posts",
            "documentation": "/docs"
        }
    } 