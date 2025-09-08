from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional, Literal
from datetime import datetime
from pydantic import BaseModel
import re

from .. import models, schemas
from ..database import get_db
from ..auth import get_current_admin_user
from ..ai_service import ai_generator

router = APIRouter()

class AIGenerateRequest(BaseModel):
    topic: str
    article_type: Literal["quick", "standard", "deep"] = "standard"
    ai_provider: Literal["gemini", "perplexity", "both"] = "gemini"
    publish_option: Literal["now", "draft", "schedule"] = "draft"
    scheduled_for: Optional[datetime] = None
    category: Optional[str] = "ai-generated"

@router.post("/ai/generate")
async def generate_article(
    request: AIGenerateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Generate an article using AI"""
    
    try:
        # Generate the article
        result = await ai_generator.generate_article(
            topic=request.topic,
            article_type=request.article_type,
            ai_provider=request.ai_provider
        )
        
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Determine status based on publish option
        if request.publish_option == "now":
            status = "published"
            published_at = datetime.utcnow()
        elif request.publish_option == "schedule" and request.scheduled_for:
            status = "draft"  # Will be published later by scheduler
            published_at = None
        else:  # draft
            status = "draft"
            published_at = None
        
        # Create post in database
        new_post = models.Post(
            title=result["title"],
            slug=result["slug"],
            content=result["content"],
            excerpt=result["excerpt"],
            status=status,
            verification_status="unverified",
            category=request.category,
            author_id=current_user.id,
            published_at=published_at,
            ai_generated=True,
            ai_prompt=request.topic,
            scheduled_for=request.scheduled_for if request.publish_option == "schedule" else None
        )
        
        db.add(new_post)
        db.commit()
        db.refresh(new_post)
        
        return {
            "success": True,
            "post_id": new_post.id,
            "title": result["title"],
            "status": status,
            "word_count": result.get("word_count", 0),
            "provider": result["provider"],
            "scheduled_for": request.scheduled_for if request.publish_option == "schedule" else None,
            "preview_url": f"/{new_post.slug}" if status == "published" else None
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@router.get("/ai/scheduled")
async def get_scheduled_posts(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Get all scheduled AI posts"""
    
    scheduled_posts = db.query(models.Post).filter(
        models.Post.scheduled_for != None,
        models.Post.status == "draft"
    ).order_by(models.Post.scheduled_for.asc()).all()
    
    return [
        {
            "id": post.id,
            "title": post.title,
            "scheduled_for": post.scheduled_for,
            "topic": post.ai_prompt,
            "created_at": post.created_at
        }
        for post in scheduled_posts
    ]

@router.post("/ai/publish-scheduled")
async def publish_scheduled_posts(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    """Manually trigger publishing of scheduled posts (for testing)"""
    
    # Find posts that should be published
    now = datetime.utcnow()
    posts_to_publish = db.query(models.Post).filter(
        models.Post.scheduled_for <= now,
        models.Post.status == "draft"
    ).all()
    
    published_count = 0
    for post in posts_to_publish:
        post.status = "published"
        post.published_at = now
        published_count += 1
    
    db.commit()
    
    return {
        "success": True,
        "published_count": published_count,
        "message": f"Published {published_count} scheduled posts"
    }
