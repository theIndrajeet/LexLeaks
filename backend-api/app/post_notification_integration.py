"""
Post-Notification Integration Service
Handles automatic and manual notification triggers for posts
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_

from . import models, crud
from .notification_service import notification_service
from .notification_ai_agent import notification_ai_agent

logger = logging.getLogger(__name__)

class PostNotificationIntegration:
    """Handles integration between posts and notifications"""
    
    def __init__(self):
        self.notification_service = notification_service
        self.ai_agent = notification_ai_agent
    
    async def on_post_published(self, db: Session, post_id: int, post_data: Dict[str, Any]):
        """Triggered when a new post is published"""
        try:
            logger.info(f"📰 Post {post_id} published - triggering notifications")
            
            # Get the post details
            post = crud.get_post(db, post_id=post_id)
            if not post:
                logger.error(f"Post {post_id} not found")
                return
            
            # Check if post should trigger notifications
            if not self._should_trigger_notification(post):
                logger.info(f"Post {post_id} doesn't meet notification criteria")
                return
            
            # Determine notification style based on post characteristics
            style = self._determine_notification_style(post)
            
            # Generate AI notification content
            notification_content = self.ai_agent.generate_creative_notification(
                {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'category': post.category,
                    'verification_status': post.verification_status
                },
                style
            )
            
            # Get users who should receive this notification
            target_users = await self._get_target_users(db, post)
            
            if not target_users:
                logger.info(f"No target users found for post {post_id}")
                return
            
            # Send notifications
            result = await self.notification_service.send_notification_to_users(
                db=db,
                users=target_users,
                content=notification_content['content'],
                style=style,
                post_id=post.id,
                template_id=None  # AI-generated, no template
            )
            
            logger.info(f"✅ Notifications sent for post {post_id}: {result.get('sent_count', 0)} users")
            
        except Exception as e:
            logger.error(f"❌ Error processing post {post_id} notification: {e}")
    
    def _should_trigger_notification(self, post) -> bool:
        """Determine if a post should trigger notifications"""
        # Only send notifications for published posts
        if post.status != 'published':
            return False
        
        # Only send for verified posts (or high-impact unverified)
        if post.verification_status not in ['verified', 'high_impact']:
            return False
        
        # Don't send for very old posts (older than 24 hours)
        if post.published_at:
            time_diff = datetime.now() - post.published_at
            if time_diff.total_seconds() > 86400:  # 24 hours
                return False
        
        return True
    
    def _determine_notification_style(self, post) -> str:
        """Determine the best notification style for a post"""
        # Check post category and content for style determination
        category = post.category or ''
        title = post.title or ''
        content = post.content or ''
        
        # Breaking news indicators
        breaking_keywords = ['breaking', 'urgent', 'arrested', 'scandal', 'fraud', 'lawsuit']
        if any(keyword in title.lower() or keyword in content.lower() for keyword in breaking_keywords):
            return 'breaking'
        
        # Urgent indicators
        urgent_keywords = ['deadline', 'court', 'hearing', 'trial', 'verdict', 'settlement']
        if any(keyword in title.lower() or keyword in content.lower() for keyword in urgent_keywords):
            return 'urgent'
        
        # Mystery indicators
        mystery_keywords = ['investigation', 'probe', 'mystery', 'uncovered', 'revealed', 'exposed']
        if any(keyword in title.lower() or keyword in content.lower() for keyword in mystery_keywords):
            return 'mystery'
        
        # Default to community for general updates
        return 'community'
    
    async def _get_target_users(self, db: Session, post) -> List[models.User]:
        """Get users who should receive notifications for this post"""
        try:
            # Get users with notification preferences enabled
            users_with_preferences = db.query(models.User).join(
                models.UserNotificationPreferences
            ).filter(
                and_(
                    models.UserNotificationPreferences.enabled == True,
                    models.UserNotificationPreferences.categories.contains([post.category])
                )
            ).all()
            
            # Also get users with push subscriptions
            users_with_push = db.query(models.User).join(
                models.PushSubscription
            ).filter(
                models.PushSubscription.is_active == True
            ).all()
            
            # Combine and deduplicate
            all_users = list(set(users_with_preferences + users_with_push))
            
            # Filter by impact level if specified
            filtered_users = []
            for user in all_users:
                prefs = user.notification_preferences[0] if user.notification_preferences else None
                if prefs:
                    impact_level = prefs.impact_level or 'all'
                    if impact_level == 'all' or impact_level == 'high':
                        filtered_users.append(user)
                else:
                    # Default to include if no preferences set
                    filtered_users.append(user)
            
            return filtered_users
            
        except Exception as e:
            logger.error(f"Error getting target users: {e}")
            return []
    
    async def send_manual_notification(
        self, 
        db: Session, 
        post_id: int, 
        style: str,
        target_user_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """Send manual notification for a specific post"""
        try:
            # Get the post
            post = crud.get_post(db, post_id=post_id)
            if not post:
                return {"success": False, "error": "Post not found"}
            
            # Generate AI notification content
            notification_content = self.ai_agent.generate_creative_notification(
                {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'category': post.category,
                    'verification_status': post.verification_status
                },
                style
            )
            
            # Get target users
            if target_user_ids:
                # Send to specific users
                target_users = db.query(models.User).filter(
                    models.User.id.in_(target_user_ids)
                ).all()
            else:
                # Send to all users with preferences
                target_users = await self._get_target_users(db, post)
            
            if not target_users:
                return {"success": False, "error": "No target users found"}
            
            # Send notifications
            result = await self.notification_service.send_notification_to_users(
                db=db,
                users=target_users,
                content=notification_content['content'],
                style=style,
                post_id=post.id,
                template_id=None
            )
            
            return {
                "success": True,
                "sent_count": result.get('sent_count', 0),
                "post_title": post.title,
                "style": style,
                "content": notification_content['content']
            }
            
        except Exception as e:
            logger.error(f"Error sending manual notification: {e}")
            return {"success": False, "error": str(e)}
    
    async def get_posts_for_notification(self, db: Session, limit: int = 50) -> List[Dict[str, Any]]:
        """Get posts that can be used for notifications"""
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
            logger.error(f"Error getting posts for notification: {e}")
            return []

# Global instance
post_notification_integration = PostNotificationIntegration()
