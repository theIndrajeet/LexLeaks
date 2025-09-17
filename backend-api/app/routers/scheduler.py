from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel

from ..database import get_db
from ..scheduler_service import scheduler_service

router = APIRouter()

class SchedulerStatusResponse(BaseModel):
    is_running: bool
    automation_enabled: bool
    generation_time: str
    publish_time: str
    timezone: str
    next_generation: str
    next_publish: str

class ToggleAutomationRequest(BaseModel):
    enabled: bool

class UpdateScheduleRequest(BaseModel):
    generation_time: str
    publish_time: str

class ManualGenerateRequest(BaseModel):
    topic: str
    article_type: str = 'standard'
    template: str = 'legal_explainer'
    publish_option: str = 'draft'  # 'draft' or 'live'

class RunNowRequest(BaseModel):
    mode: str = 'generate'  # 'generate' | 'generate_and_publish'

@router.get("/scheduler/status", response_model=SchedulerStatusResponse)
async def get_scheduler_status():
    """Get current scheduler status"""
    try:
        status = scheduler_service.get_scheduler_status()
        return SchedulerStatusResponse(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting scheduler status: {str(e)}")

@router.post("/scheduler/start")
async def start_scheduler():
    """Start the scheduler service"""
    try:
        await scheduler_service.start_scheduler()
        return {
            "success": True,
            "message": "Scheduler started successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting scheduler: {str(e)}")

@router.post("/scheduler/stop")
async def stop_scheduler():
    """Stop the scheduler service"""
    try:
        await scheduler_service.stop_scheduler()
        return {
            "success": True,
            "message": "Scheduler stopped successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping scheduler: {str(e)}")

@router.post("/scheduler/toggle-automation")
async def toggle_automation(request: ToggleAutomationRequest):
    """Toggle automation on/off"""
    try:
        result = scheduler_service.toggle_automation(request.enabled)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error toggling automation: {str(e)}")

@router.post("/scheduler/update-schedule")
async def update_schedule(request: UpdateScheduleRequest):
    """Update the schedule times"""
    try:
        result = scheduler_service.update_schedule(
            request.generation_time,
            request.publish_time
        )
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating schedule: {str(e)}")

@router.post("/scheduler/manual-generate")
async def manual_generate_article(request: ManualGenerateRequest):
    """Manually generate an article"""
    try:
        result = await scheduler_service.manual_generate_article(
            request.topic,
            request.article_type,
            request.template,
            request.publish_option
        )
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating article: {str(e)}")

@router.post("/scheduler/manual-publish")
async def manual_publish_scheduled():
    """Manually publish all scheduled articles"""
    try:
        result = await scheduler_service.manual_publish_scheduled()
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error publishing articles: {str(e)}")

@router.post("/scheduler/run-now")
async def run_now(request: RunNowRequest):
    """Run automation immediately (generate or generate+publish)."""
    try:
        result = await scheduler_service.run_automation_now(mode=request.mode)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running automation now: {str(e)}")

@router.get("/scheduler/scheduled-posts")
async def get_scheduled_posts(db: Session = Depends(get_db)):
    """Get all scheduled posts"""
    try:
        from ..models import Post
        from datetime import datetime
        import pytz
        
        timezone = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(timezone)
        
        scheduled_posts = db.query(Post).filter(
            Post.status == 'draft',
            Post.published_at.isnot(None),
            Post.published_at > current_time,
            Post.category == 'ai-generated'
        ).order_by(Post.published_at).all()
        
        return {
            "success": True,
            "scheduled_posts": [
                {
                    "id": post.id,
                    "title": post.title,
                    "scheduled_for": post.published_at.isoformat(),
                    "category": post.category,
                    "created_at": post.created_at.isoformat()
                }
                for post in scheduled_posts
            ],
            "total_count": len(scheduled_posts)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting scheduled posts: {str(e)}")

@router.get("/scheduler/stats")
async def get_scheduler_stats(db: Session = Depends(get_db)):
    """Get scheduler statistics"""
    try:
        from ..models import Post
        from datetime import datetime, timedelta
        import pytz
        
        timezone = pytz.timezone('Asia/Kolkata')
        now = datetime.now(timezone)
        today = now.date()
        week_ago = now - timedelta(days=7)
        
        # Get stats
        total_ai_posts = db.query(Post).filter(Post.category == 'ai-generated').count()
        published_ai_posts = db.query(Post).filter(
            Post.category == 'ai-generated',
            Post.status == 'published'
        ).count()
        scheduled_posts = db.query(Post).filter(
            Post.category == 'ai-generated',
            Post.status == 'draft',
            Post.published_at.isnot(None),
            Post.published_at > now
        ).count()
        posts_today = db.query(Post).filter(
            Post.category == 'ai-generated',
            Post.created_at >= today
        ).count()
        posts_this_week = db.query(Post).filter(
            Post.category == 'ai-generated',
            Post.created_at >= week_ago
        ).count()
        
        return {
            "success": True,
            "stats": {
                "total_ai_posts": total_ai_posts,
                "published_ai_posts": published_ai_posts,
                "scheduled_posts": scheduled_posts,
                "posts_today": posts_today,
                "posts_this_week": posts_this_week,
                "success_rate": round((published_ai_posts / total_ai_posts * 100) if total_ai_posts > 0 else 0, 2)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting scheduler stats: {str(e)}")
