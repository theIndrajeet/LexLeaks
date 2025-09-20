"""
Notification Service for LexLeaks
Handles push notifications, user preferences, and analytics
"""

import os
import logging
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func

from . import models, crud
from .notification_ai_agent import notification_ai_agent
from .database import get_db

# Web Push imports
try:
    from pywebpush import webpush, WebPushException
    WEBPUSH_AVAILABLE = True
except ImportError:
    WEBPUSH_AVAILABLE = False
    logger.warning("pywebpush not available. Push notifications will not work.")

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for managing notifications"""
    
    def __init__(self):
        self.ai_agent = notification_ai_agent
        self.vapid_private_key = os.getenv("VAPID_PRIVATE_KEY")
        self.vapid_public_key = os.getenv("VAPID_PUBLIC_KEY")
        self.vapid_claims = {"sub": "mailto:heyjeetttt@gmail.com"}
        
        if not self.vapid_private_key:
            logger.warning("⚠️ VAPID_PRIVATE_KEY not found in environment variables")
        if not self.vapid_public_key:
            logger.warning("⚠️ VAPID_PUBLIC_KEY not found in environment variables")
            
        logger.info("✅ Notification Service initialized")
    
    def create_notification_template(self, db: Session, template_data: Dict) -> models.NotificationTemplate:
        """Create a new notification template"""
        try:
            template = models.NotificationTemplate(
                name=template_data["name"],
                style=template_data["style"],
                template_text=template_data["template_text"],
                emoji_set=template_data.get("emoji_set"),
                tone=template_data.get("tone")
            )
            db.add(template)
            db.commit()
            db.refresh(template)
            logger.info(f"✅ Created notification template: {template.name}")
            return template
        except Exception as e:
            logger.error(f"❌ Error creating template: {e}")
            db.rollback()
            raise
    
    def get_user_preferences(self, db: Session, user_id: int) -> Optional[models.UserNotificationPreferences]:
        """Get user notification preferences"""
        return db.query(models.UserNotificationPreferences).filter(
            models.UserNotificationPreferences.user_id == user_id
        ).first()
    
    def update_user_preferences(self, db: Session, user_id: int, preferences: Dict) -> models.UserNotificationPreferences:
        """Update user notification preferences"""
        try:
            existing = self.get_user_preferences(db, user_id)
            
            if existing:
                # Update existing preferences
                for key, value in preferences.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                existing.updated_at = datetime.now()
            else:
                # Create new preferences
                existing = models.UserNotificationPreferences(
                    user_id=user_id,
                    **preferences
                )
                db.add(existing)
            
            db.commit()
            db.refresh(existing)
            logger.info(f"✅ Updated notification preferences for user {user_id}")
            return existing
        except Exception as e:
            logger.error(f"❌ Error updating preferences: {e}")
            db.rollback()
            raise
    
    def get_users_for_notification(self, db: Session, post_data: Dict) -> List[int]:
        """Get list of users who should receive this notification"""
        try:
            # Get users with notification preferences
            query = db.query(models.UserNotificationPreferences).filter(
                models.UserNotificationPreferences.enabled == True
            )
            
            # Filter by category if specified
            category = post_data.get("category")
            if category:
                # For now, skip category filtering to avoid JSON operator issues
                # TODO: Implement proper JSON category filtering
                pass
            
            # Filter by impact level
            impact_level = self._determine_impact_level(post_data)
            if impact_level == "high":
                query = query.filter(
                    or_(
                        models.UserNotificationPreferences.impact_level == "all",
                        models.UserNotificationPreferences.impact_level == "high"
                    )
                )
            
            preferences = query.all()
            user_ids = [pref.user_id for pref in preferences if pref.user_id]
            
            logger.info(f"📊 Found {len(user_ids)} users eligible for notification")
            return user_ids
            
        except Exception as e:
            logger.error(f"❌ Error getting users for notification: {e}")
            return []
    
    async def send_notification_to_users(self, db: Session, users: List[models.User], 
                                       content: str, style: str, post_id: int, 
                                       template_id: Optional[int] = None) -> Dict[str, Any]:
        """Send notification to multiple users"""
        try:
            sent_count = 0
            failed_count = 0
            
            for user in users:
                try:
                    # Get user's push subscriptions
                    subscriptions = db.query(models.PushSubscription).filter(
                        and_(
                            models.PushSubscription.user_id == user.id,
                            models.PushSubscription.is_active == True
                        )
                    ).all()
                    
                    if not subscriptions:
                        logger.info(f"ℹ️ No active push subscriptions for user {user.id}")
                        continue
                    
                    # Create notification record first
                    notification = models.NotificationSent(
                        user_id=user.id,
                        content=content,
                        style=style,
                        post_id=post_id,
                        sent_at=datetime.now()
                    )
                    db.add(notification)
                    db.flush()  # Get the notification ID
                    
                    # Send push notification to each subscription
                    push_sent = False
                    for subscription in subscriptions:
                        try:
                            success = await self._send_push_notification(
                                subscription, content, style, post_id, notification.id
                            )
                            if success:
                                push_sent = True
                        except Exception as e:
                            logger.error(f"❌ Failed to send push to subscription {subscription.id}: {e}")
                            # Mark subscription as inactive if it's expired
                            if "410" in str(e) or "expired" in str(e).lower():
                                subscription.is_active = False
                    
                    if push_sent:
                        sent_count += 1
                    else:
                        failed_count += 1
                        
                except Exception as e:
                    logger.error(f"❌ Error processing user {user.id}: {e}")
                    failed_count += 1
                    continue
            
            db.commit()
            logger.info(f"✅ Sent notification to {sent_count} users, {failed_count} failed")
            return {
                "sent_count": sent_count, 
                "failed_count": failed_count,
                "success": sent_count > 0
            }
            
        except Exception as e:
            logger.error(f"❌ Error sending notifications: {e}")
            db.rollback()
            return {"sent_count": 0, "failed_count": len(users), "success": False, "error": str(e)}
    
    async def _send_push_notification(self, subscription: models.PushSubscription, 
                                    content: str, style: str, post_id: int, 
                                    notification_id: int) -> bool:
        """Send push notification to a specific subscription"""
        try:
            if not WEBPUSH_AVAILABLE:
                logger.error("❌ pywebpush not available")
                return False
                
            if not self.vapid_private_key:
                logger.error("❌ VAPID private key not configured")
                return False
            
            # Prepare notification payload
            payload = {
                "title": self._get_notification_title(style),
                "content": content,
                "style": style,
                "postId": post_id,
                "notificationId": notification_id,
                "url": f"/posts/{post_id}",
                "icon": "/icon-192x192.png",
                "badge": "/icon-144x144.png",
                "timestamp": datetime.now().isoformat()
            }
            
            # Prepare subscription info
            subscription_info = {
                "endpoint": subscription.endpoint,
                "keys": {
                    "p256dh": subscription.p256dh,
                    "auth": subscription.auth
                }
            }
            
            # Send the push notification
            webpush(
                subscription_info=subscription_info,
                data=json.dumps(payload),
                vapid_private_key=self.vapid_private_key,
                vapid_claims=self.vapid_claims
            )
            
            logger.info(f"✅ Push notification sent to subscription {subscription.id}")
            return True
            
        except WebPushException as e:
            logger.error(f"❌ WebPush error for subscription {subscription.id}: {e}")
            # Handle specific error cases
            if e.response and e.response.status_code == 410:
                logger.info(f"🔄 Subscription {subscription.id} expired, marking as inactive")
                return False
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error sending push to subscription {subscription.id}: {e}")
            return False
    
    def _get_notification_title(self, style: str) -> str:
        """Get notification title based on style"""
        titles = {
            "breaking": "🚨 BREAKING NEWS - LexLeaks",
            "mystery": "🤔 New Mystery - LexLeaks", 
            "urgent": "⚡ URGENT - LexLeaks",
            "community": "👥 Community Update - LexLeaks"
        }
        return titles.get(style, "📰 LexLeaks Update")
    
    async def send_test_notification(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Send a test notification to a specific user"""
        try:
            user = db.query(models.User).filter(models.User.id == user_id).first()
            if not user:
                return {"success": False, "error": "User not found"}
            
            test_content = "🚀 Test notification from LexLeaks! Your push notifications are working perfectly."
            test_style = "community"
            
            result = await self.send_notification_to_users(
                db=db,
                users=[user],
                content=test_content,
                style=test_style,
                post_id=0  # Test notification
            )
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error sending test notification: {e}")
            return {"success": False, "error": str(e)}
    
    def cleanup_expired_subscriptions(self, db: Session) -> int:
        """Clean up expired or invalid push subscriptions"""
        try:
            # Mark subscriptions as inactive that haven't been updated in 30 days
            cutoff_date = datetime.now() - timedelta(days=30)
            
            expired_count = db.query(models.PushSubscription).filter(
                and_(
                    models.PushSubscription.is_active == True,
                    models.PushSubscription.updated_at < cutoff_date
                )
            ).update({"is_active": False})
            
            db.commit()
            logger.info(f"🧹 Cleaned up {expired_count} expired subscriptions")
            return expired_count
            
        except Exception as e:
            logger.error(f"❌ Error cleaning up subscriptions: {e}")
            db.rollback()
            return 0
    
    def create_ab_test(self, db: Session, test_name: str, post_data: Dict) -> models.NotificationABTest:
        """Create A/B test for notification content"""
        try:
            # Generate two variants
            variant_a, variant_b = self.ai_agent.generate_ab_test_variants(post_data)
            
            ab_test = models.NotificationABTest(
                test_name=test_name,
                variant_a=variant_a["content"],
                variant_b=variant_b["content"],
                test_duration=24  # 24 hours default
            )
            
            db.add(ab_test)
            db.commit()
            db.refresh(ab_test)
            
            logger.info(f"✅ Created A/B test: {test_name}")
            return ab_test
            
        except Exception as e:
            logger.error(f"❌ Error creating A/B test: {e}")
            db.rollback()
            raise
    
    def get_notification_analytics(self, db: Session, days: int = 7) -> Dict:
        """Get notification analytics for the last N days"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Total notifications sent
            total_sent = db.query(models.NotificationSent).filter(
                models.NotificationSent.sent_at >= start_date
            ).count()
            
            # Notifications opened
            total_opened = db.query(models.NotificationSent).filter(
                and_(
                    models.NotificationSent.sent_at >= start_date,
                    models.NotificationSent.opened_at.isnot(None)
                )
            ).count()
            
            # Notifications clicked
            total_clicked = db.query(models.NotificationSent).filter(
                and_(
                    models.NotificationSent.sent_at >= start_date,
                    models.NotificationSent.clicked_at.isnot(None)
                )
            ).count()
            
            # Calculate rates
            open_rate = (total_opened / total_sent * 100) if total_sent > 0 else 0
            click_rate = (total_clicked / total_sent * 100) if total_sent > 0 else 0
            
            # Style performance
            style_performance = db.query(
                models.NotificationSent.style,
                func.count(models.NotificationSent.id).label('total'),
                func.count(models.NotificationSent.opened_at).label('opened'),
                func.count(models.NotificationSent.clicked_at).label('clicked')
            ).filter(
                models.NotificationSent.sent_at >= start_date
            ).group_by(models.NotificationSent.style).all()
            
            return {
                "total_sent": total_sent,
                "total_opened": total_opened,
                "total_clicked": total_clicked,
                "open_rate": round(open_rate, 2),
                "click_rate": round(click_rate, 2),
                "style_performance": [
                    {
                        "style": row.style,
                        "total": row.total,
                        "opened": row.opened,
                        "clicked": row.clicked,
                        "open_rate": round((row.opened / row.total * 100) if row.total > 0 else 0, 2),
                        "click_rate": round((row.clicked / row.total * 100) if row.total > 0 else 0, 2)
                    }
                    for row in style_performance
                ],
                "period_days": days
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting analytics: {e}")
            return {"error": str(e)}
    
    def track_notification_engagement(self, db: Session, notification_id: int, 
                                    action: str) -> bool:
        """Track user engagement with notification"""
        try:
            notification = db.query(models.NotificationSent).filter(
                models.NotificationSent.id == notification_id
            ).first()
            
            if not notification:
                return False
            
            if action == "open" and not notification.opened_at:
                notification.opened_at = datetime.now()
            elif action == "click" and not notification.clicked_at:
                notification.clicked_at = datetime.now()
            
            # Calculate engagement score
            score = 0
            if notification.opened_at:
                score += 1
            if notification.clicked_at:
                score += 2
            
            notification.engagement_score = score
            db.commit()
            
            logger.info(f"✅ Tracked {action} for notification {notification_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error tracking engagement: {e}")
            return False
    
    def _determine_impact_level(self, post_data: Dict) -> str:
        """Determine impact level of post"""
        title = post_data.get("title", "").lower()
        content = post_data.get("content", "").lower()
        
        high_impact_keywords = [
            "scandal", "corruption", "fraud", "bribery", "lawsuit", 
            "settlement", "resignation", "crisis", "emergency"
        ]
        
        if any(keyword in title or keyword in content for keyword in high_impact_keywords):
            return "high"
        return "medium"
    
    def get_recent_notifications(self, db: Session, user_id: int, limit: int = 10) -> List[Dict]:
        """Get recent notifications for a user"""
        try:
            notifications = db.query(models.NotificationSent).filter(
                models.NotificationSent.user_id == user_id
            ).order_by(desc(models.NotificationSent.sent_at)).limit(limit).all()
            
            return [
                {
                    "id": notif.id,
                    "content": notif.content,
                    "style": notif.style,
                    "sent_at": notif.sent_at.isoformat(),
                    "opened_at": notif.opened_at.isoformat() if notif.opened_at else None,
                    "clicked_at": notif.clicked_at.isoformat() if notif.clicked_at else None,
                    "engagement_score": notif.engagement_score
                }
                for notif in notifications
            ]
            
        except Exception as e:
            logger.error(f"❌ Error getting recent notifications: {e}")
            return []

# Global instance
notification_service = NotificationService()
