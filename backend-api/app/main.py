from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from .database import engine
from . import models
from .routers import posts, auth, impacts, ai, google_auth, kanoon, opportunities, legal_ai
from .smart_automation import start_automation

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
def create_tables():
    try:
        models.Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.warning("⚠️  Server will continue without database features")
        logger.warning("⚠️  Some features may not work properly")


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    # Start smart automation
    await start_automation()
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
        "http://localhost:3001",  # Next.js development server (alternative port)
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
app.include_router(ai.router, prefix="/api")
app.include_router(google_auth.router, prefix="/api/auth")
app.include_router(kanoon.router, prefix="/api/kanoon")
app.include_router(opportunities.router, prefix="/api")
app.include_router(legal_ai.router, prefix="/api/legal-ai")
# app.include_router(notifications.router, prefix="/api/notifications")  # TODO: Add notifications module


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


# API info endpoint
@app.get("/api")
async def api_info():
    return {
        "message": "LexLeaks API v1.0.0",
        "endpoints": {
            "authentication": "/api/auth",
            "posts": "/api/posts",
            "impacts": "/api/impacts",
            "opportunities": "/api/opportunities",
            "kanoon": "/api/kanoon",
            "ai": "/api/ai",
            "jurisbrain-ai": "/api/legal-ai",
            "notifications": "/api/notifications",
            "documentation": "/docs"
        }
    } 