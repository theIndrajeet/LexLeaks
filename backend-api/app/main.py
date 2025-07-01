from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import Depends
from sqlalchemy.sql import text
from sqlalchemy.orm import Session

from .database import engine, get_db
from . import models
from .routers import posts, auth, impacts


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

# Configure CORS - using allow_origin_regex to support Netlify preview URLs
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js development server
        "https://lexleaks.com",   # Production domain
        "https://www.lexleaks.com",  # Production domain with www
        "https://lexleaks.netlify.app",  # Your main Netlify domain
        "https://glittery-dragon-d3e69b.netlify.app",  # Current Netlify deployment
    ],
    allow_origin_regex=r"https://.*\.netlify\.app",  # All Netlify preview deployments
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(posts.router, prefix="/api")
app.include_router(impacts.router, prefix="/api")


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
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/api/check-verification-field")
def check_verification_field(db: Session = Depends(get_db)):
    """Check if verification_status field exists in posts table"""
    try:
        # Try to query the verification_status column
        result = db.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = 'posts' AND column_name = 'verification_status'"))
        row = result.fetchone()
        
        if row:
            # Also get a sample of verification statuses
            posts_result = db.execute(text("SELECT id, title, verification_status FROM posts LIMIT 3"))
            sample_posts = [{"id": row[0], "title": row[1], "verification_status": row[2]} for row in posts_result]
            
            return {
                "field_exists": True,
                "message": "verification_status column exists",
                "sample_posts": sample_posts
            }
        else:
            return {
                "field_exists": False,
                "message": "verification_status column does not exist"
            }
    except Exception as e:
        return {
            "field_exists": False,
            "error": str(e)
        }


# API info endpoint
@app.get("/api")
async def api_info():
    return {
        "message": "LexLeaks API v1.0.0",
        "endpoints": {
            "authentication": "/api/auth",
            "posts": "/api/posts",
            "impacts": "/api/impacts",
            "documentation": "/docs"
        }
    } 