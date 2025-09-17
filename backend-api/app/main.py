from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import asyncio
import os

from .database import engine
from . import models
from .routers import posts, auth, impacts, ai, google_auth, kanoon, opportunities, legal_ai, deep_research, chat, multi_agent_research, event_driven_research, trends, scheduler, pipeline
from .smart_automation import start_automation
from .event_driven_agent_system import event_driven_system
from .scheduler_service import scheduler_service

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
def create_tables():
    try:
        models.Base.metadata.create_all(bind=engine)
        logger.info(" Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        logger.warning("⚠️  Server will continue without database features")
        logger.warning("⚠️  Some features may not work properly")

async def start_background_services():
    """Start heavy services in background for production"""
    try:
        await asyncio.sleep(5)  # Let the server start first
        await start_automation()
        asyncio.create_task(event_driven_system.start())
        logger.info("🔧 Event-driven agent system started")
        await scheduler_service.start_scheduler()
        logger.info("📅 Article scheduler service started")
    except Exception as e:
        logger.error(f"❌ Background services failed: {e}")


# Lifespan event handler
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()
    
    # Check if we're in production (Cloud Run)
    is_production = os.getenv("K_SERVICE") or os.getenv("GOOGLE_CLOUD_PROJECT")
    
    if is_production:
        # Production: Start services in background to avoid timeout
        logger.info("🚀 Production mode: Starting services in background")
        asyncio.create_task(start_background_services())
    else:
        # Development: Start services normally
        await start_automation()
        asyncio.create_task(event_driven_system.start())
        logger.info("🔧 Event-driven agent system started")
        await scheduler_service.start_scheduler()
        logger.info("📅 Article scheduler service started")
    
    yield
    # Shutdown (if needed)

async def start_background_services():
    """Start heavy services in background for production"""
    try:
        await asyncio.sleep(5)  # Let the server start first
        await start_automation()
        asyncio.create_task(event_driven_system.start())
        logger.info("🔧 Event-driven agent system started")
        await scheduler_service.start_scheduler()
        logger.info("📅 Article scheduler service started")
    except Exception as e:
        logger.error(f"❌ Background services failed: {e}")


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
        "http://localhost:3100",  # Stagewise development server
        "https://lexleaks.com",   # Production domain - OAuth fix
        "https://www.lexleaks.com",  # Production domain with www
        "https://lexleaks.netlify.app",  # Your main Netlify domain
        "https://glittery-dragon-d3e69b.netlify.app",  # Current Netlify deployment
    ],
    allow_origin_regex=r"https://.*\.netlify\.app|http://localhost:\d+",  # All Netlify preview deployments and localhost ports
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
app.include_router(deep_research.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(multi_agent_research.router)
app.include_router(event_driven_research.router)
app.include_router(trends.router, prefix="/api", tags=["trends"])
app.include_router(scheduler.router, prefix="/api", tags=["scheduler"])
app.include_router(pipeline.router, prefix="/api", tags=["pipeline"])
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
            "deep-research": "/api/deep-research",
            "notifications": "/api/notifications",
            "documentation": "/docs"
        }
    } 