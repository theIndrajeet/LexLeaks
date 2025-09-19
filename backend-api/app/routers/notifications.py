"""
Notification API Router
Handles notification management, preferences, and analytics
"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_
from pydantic import BaseModel
import os

from .. import auth, models, crud
from ..database import get_db
from ..notification_service import notification_service
from ..notification_ai_agent import notification_ai_agent
from ..post_notification_integration import post_notification_integration

router = APIRouter(
    prefix="/notifications",
    tags=["notifications"]
)

# Pydantic models for API
class NotificationTemplateCreate(BaseModel):
    name: str
    style: str
    template_text: str
    emoji_set: Optional[Dict] = None
    tone: Optional[str] = None

class UserPreferencesUpdate(BaseModel):
    categories: Optional[List[str]] = None
    frequency: Optional[str] = "realtime"
    quiet_hours: Optional[Dict] = None
    impact_level: Optional[str] = "all"
    enabled: Optional[bool] = True

class NotificationCreate(BaseModel):
    post_id: int
    style: Optional[str] = None
    test_ab: Optional[bool] = False

class ABTestCreate(BaseModel):
    test_name: str
    post_id: int

# Template Management
@router.get("/templates", response_model=List[Dict])
def get_notification_templates(
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_admin_user)
):
    """Get all notification templates"""
    try:
        templates = db.query(models.NotificationTemplate).all()
        return [
            {
                "id": template.id,
                "name": template.name,
                "style": template.style,
                "template_text": template.template_text,
                "emoji_set": template.emoji_set,
                "tone": template.tone,
                "created_at": template.created_at.isoformat()
            }
            for template in templates
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching templates: {str(e)}")

@router.post("/templates", response_model=Dict)
def create_notification_template(
    template_data: NotificationTemplateCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_admin_user)
):
    """Create a new notification template"""
    try:
        template = notification_service.create_notification_template(
            db, template_data.dict()
        )
        return {
            "id": template.id,
            "name": template.name,
            "style": template.style,
            "message": "Template created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating template: {str(e)}")

# User Preferences
@router.get("/preferences", response_model=Dict)
def get_user_preferences(
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    """Get current user's notification preferences"""
    try:
        preferences = notification_service.get_user_preferences(db, current_user.id)
        if not preferences:
            return {
                "categories": [],
                "frequency": "realtime",
                "quiet_hours": {"start": "22:00", "end": "08:00"},
                "impact_level": "all",
                "enabled": True
            }
        
        return {
            "categories": preferences.categories or [],
            "frequency": preferences.frequency,
            "quiet_hours": preferences.quiet_hours,
            "impact_level": preferences.impact_level,
            "enabled": preferences.enabled
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching preferences: {str(e)}")

@router.put("/preferences", response_model=Dict)
def update_user_preferences(
    preferences: UserPreferencesUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    """Update current user's notification preferences"""
    try:
        updated_preferences = notification_service.update_user_preferences(
            db, current_user.id, preferences.dict(exclude_unset=True)
        )
        return {
            "message": "Preferences updated successfully",
            "preferences": {
                "categories": updated_preferences.categories,
                "frequency": updated_preferences.frequency,
                "quiet_hours": updated_preferences.quiet_hours,
                "impact_level": updated_preferences.impact_level,
                "enabled": updated_preferences.enabled
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating preferences: {str(e)}")

# Notification Creation and Sending
@router.post("/create", response_model=Dict)
def create_notification(
    notification_data: NotificationCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_admin_user)
):
    """Create and send notification for a post"""
    try:
        # Get post data
        post = db.query(models.Post).filter(models.Post.id == notification_data.post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        post_data = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "category": post.category,
            "verification_status": post.verification_status
        }
        
        # Generate notification content
        notification_content = notification_ai_agent.generate_creative_notification(
            post_data, notification_data.style
        )
        
        # Get eligible users
        user_ids = notification_service.get_users_for_notification(db, post_data)
        
        if not user_ids:
            return {
                "message": "No eligible users found for notification",
                "notification_content": notification_content,
                "users_count": 0
            }
        
        # Send notifications
        sent_count = notification_service.send_notification_to_users(
            db, post_data, user_ids, notification_content
        )
        
        return {
            "message": f"Notification sent to {sent_count} users",
            "notification_content": notification_content,
            "users_count": sent_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating notification: {str(e)}")

# A/B Testing
@router.post("/ab-test", response_model=Dict)
def create_ab_test(
    test_data: ABTestCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_admin_user)
):
    """Create A/B test for notification content"""
    try:
        # Get post data
        post = db.query(models.Post).filter(models.Post.id == test_data.post_id).first()
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        post_data = {
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "category": post.category,
            "verification_status": post.verification_status
        }
        
        ab_test = notification_service.create_ab_test(
            db, test_data.test_name, post_data
        )
        
        return {
            "id": ab_test.id,
            "test_name": ab_test.test_name,
            "variant_a": ab_test.variant_a,
            "variant_b": ab_test.variant_b,
            "message": "A/B test created successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating A/B test: {str(e)}")

@router.get("/ab-tests", response_model=List[Dict])
def get_ab_tests(
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_admin_user)
):
    """Get all A/B tests"""
    try:
        tests = db.query(models.NotificationABTest).order_by(
            models.NotificationABTest.created_at.desc()
        ).all()
        
        return [
            {
                "id": test.id,
                "test_name": test.test_name,
                "variant_a": test.variant_a,
                "variant_b": test.variant_b,
                "winner": test.winner,
                "confidence_level": test.confidence_level,
                "total_sends": test.total_sends,
                "variant_a_opens": test.variant_a_opens,
                "variant_b_opens": test.variant_b_opens,
                "variant_a_clicks": test.variant_a_clicks,
                "variant_b_clicks": test.variant_b_clicks,
                "created_at": test.created_at.isoformat(),
                "completed_at": test.completed_at.isoformat() if test.completed_at else None
            }
            for test in tests
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching A/B tests: {str(e)}")

# Analytics
@router.get("/analytics", response_model=Dict)
def get_notification_analytics(
    days: int = Query(7, ge=1, le=90, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_admin_user)
):
    """Get notification analytics"""
    try:
        analytics = notification_service.get_notification_analytics(db, days)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")

# User Notification History
@router.get("/history", response_model=List[Dict])
def get_notification_history(
    limit: int = Query(10, ge=1, le=50, description="Number of notifications to fetch"),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    """Get current user's notification history"""
    try:
        notifications = notification_service.get_recent_notifications(
            db, current_user.id, limit
        )
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching history: {str(e)}")

# Engagement Tracking
@router.post("/track/{notification_id}")
def track_notification_engagement(
    notification_id: int,
    action: str = Query(..., regex="^(open|click)$", description="Engagement action"),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    """Track user engagement with notification"""
    try:
        success = notification_service.track_notification_engagement(
            db, notification_id, action
        )
        
        if success:
            return {"message": f"Engagement tracked: {action}"}
        else:
            raise HTTPException(status_code=404, detail="Notification not found")
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error tracking engagement: {str(e)}")

# Push Subscription Management
@router.post("/subscribe", response_model=Dict)
def subscribe_to_push(
    subscription_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    """Subscribe user to push notifications"""
    try:
        # Check if subscription already exists
        existing = db.query(models.PushSubscription).filter(
            and_(
                models.PushSubscription.user_id == current_user.id,
                models.PushSubscription.endpoint == subscription_data["endpoint"]
            )
        ).first()
        
        if existing:
            # Update existing subscription
            existing.p256dh = subscription_data.get("p256dh")
            existing.auth = subscription_data.get("auth")
            existing.user_agent = subscription_data.get("user_agent")
            existing.is_active = True
            existing.updated_at = datetime.now()
        else:
            # Create new subscription
            subscription = models.PushSubscription(
                user_id=current_user.id,
                endpoint=subscription_data["endpoint"],
                p256dh=subscription_data.get("p256dh"),
                auth=subscription_data.get("auth"),
                user_agent=subscription_data.get("user_agent"),
                is_active=True
            )
            db.add(subscription)
        
        db.commit()
        return {"message": "Successfully subscribed to push notifications"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error subscribing to push: {str(e)}")

@router.post("/unsubscribe", response_model=Dict)
def unsubscribe_from_push(
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    """Unsubscribe user from push notifications"""
    try:
        # Deactivate all subscriptions for user
        db.query(models.PushSubscription).filter(
            models.PushSubscription.user_id == current_user.id
        ).update({"is_active": False, "updated_at": datetime.now()})
        
        db.commit()
        return {"message": "Successfully unsubscribed from push notifications"}
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error unsubscribing from push: {str(e)}")

@router.get("/vapid-key", response_model=Dict)
def get_vapid_key():
    """Get VAPID public key for push notifications"""
    try:
        # In production, this should come from environment variables
        vapid_public_key = os.getenv("VAPID_PUBLIC_KEY", "BEl62iUYgUivxIkv69yViEuiBIa40HI0X8QwV7VUyR8")
        return {"publicKey": vapid_public_key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting VAPID key: {str(e)}")

# AI Agent Info
@router.get("/ai-agent/styles", response_model=List[Dict])
def get_ai_agent_styles(
    current_user = Depends(auth.get_current_admin_user)
):
    """Get available AI agent notification styles"""
    try:
        styles = notification_ai_agent.get_available_styles()
        return styles
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching styles: {str(e)}")

@router.post("/ai-agent/test", response_model=Dict)
def test_ai_agent(
    post_data: Dict[str, Any],
    style: Optional[str] = None,
    current_user = Depends(auth.get_current_admin_user)
):
    """Test AI agent notification generation"""
    try:
        notification = notification_ai_agent.generate_creative_notification(
            post_data, style
        )
        return {
            "notification": notification,
            "message": "AI agent test successful"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error testing AI agent: {str(e)}")

# Post Integration Endpoints
@router.get("/posts", response_model=List[Dict])
async def get_posts_for_notification(
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_admin_user)
):
    """Get posts available for notification sending"""
    try:
        # Get recent published posts
        posts = db.query(models.Post).filter(
            models.Post.status == 'published'
        ).order_by(
            models.Post.published_at.desc()
        ).limit(limit).all()
        
        # Format for frontend
        formatted_posts = []
        for post in posts:
            formatted_posts.append({
                'id': post.id,
                'title': post.title,
                'category': post.category,
                'verification_status': post.verification_status,
                'published_at': post.published_at.isoformat() if post.published_at else None,
                'author': post.author.username if post.author else 'Unknown',
                'excerpt': post.content[:200] + '...' if len(post.content) > 200 else post.content
            })
        
        return formatted_posts
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching posts: {str(e)}")

@router.post("/send-manual", response_model=Dict)
async def send_manual_notification(
    post_id: int,
    style: str,
    target_user_ids: Optional[List[int]] = None,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_admin_user)
):
    """Send manual notification for a specific post"""
    try:
        result = await post_notification_integration.send_manual_notification(
            db=db,
            post_id=post_id,
            style=style,
            target_user_ids=target_user_ids
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Failed to send notification"))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error sending manual notification: {str(e)}")

@router.post("/trigger-post/{post_id}", response_model=Dict)
async def trigger_post_notification(
    post_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_admin_user)
):
    """Manually trigger notification for a specific post"""
    try:
        # Get post data
        post = crud.get_post(db, post_id=post_id)
        if not post:
            raise HTTPException(status_code=404, detail="Post not found")
        
        if post.status != 'published':
            raise HTTPException(status_code=400, detail="Post must be published to send notifications")
        
        # Convert post to dict format
        post_data = {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'category': post.category,
            'verification_status': post.verification_status
        }
        
        # Trigger notification
        await post_notification_integration.on_post_published(db, post_id, post_data)
        
        return {
            "success": True,
            "message": f"Notification triggered for post: {post.title}",
            "post_id": post_id,
            "post_title": post.title,
            "verification_status": post.verification_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error triggering post notification: {str(e)}")
