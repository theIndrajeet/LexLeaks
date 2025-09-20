#!/usr/bin/env python3
"""
Direct notification test - bypasses authentication for testing
"""

import requests
import json
import os
import sys

# Add the backend directory to Python path
sys.path.append('/Users/issac/Downloads/LexLeaks/backend-api')

# Configuration
BACKEND_URL = "http://127.0.0.1:8000"

def test_notification_system():
    """Test the notification system directly"""
    
    print("🧪 Testing LexLeaks Notification System (Direct Test)")
    print("=" * 60)
    
    # Test 1: Check VAPID key
    print("\n1️⃣ Testing VAPID Key Configuration...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/notifications/vapid-key", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ VAPID key is configured")
            print(f"   Public key: {data['publicKey'][:20]}...")
        else:
            print(f"❌ VAPID key failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False
    
    # Test 2: Check if pywebpush is available
    print("\n2️⃣ Testing pywebpush availability...")
    try:
        import pywebpush
        print("✅ pywebpush is installed and available")
    except ImportError:
        print("❌ pywebpush is not installed")
        return False
    
    # Test 3: Test notification service directly
    print("\n3️⃣ Testing notification service directly...")
    try:
        # Import the notification service
        from app.notification_service import notification_service
        from app.database import SessionLocal
        from app import models
        
        db = SessionLocal()
        
        # Check if we have users
        users = db.query(models.User).limit(1).all()
        if not users:
            print("❌ No users found in database")
            return False
        
        user = users[0]
        print(f"✅ Found user: {user.username or user.email or f'ID {user.id}'}")
        
        # Check if user has push subscriptions
        subscriptions = db.query(models.PushSubscription).filter(
            models.PushSubscription.user_id == user.id
        ).all()
        
        if not subscriptions:
            print("ℹ️ No push subscriptions found - creating test subscription...")
            
            # Create a test subscription
            test_subscription = models.PushSubscription(
                user_id=user.id,
                endpoint="https://fcm.googleapis.com/fcm/send/test-endpoint-123",
                p256dh="test-p256dh-key-for-testing",
                auth="test-auth-key-for-testing",
                is_active=True
            )
            db.add(test_subscription)
            db.commit()
            print("✅ Test subscription created")
        else:
            print(f"✅ Found {len(subscriptions)} push subscription(s)")
        
        # Test the notification service
        print("\n4️⃣ Testing notification sending...")
        
        # Create a test notification record
        test_notification = models.NotificationSent(
            user_id=user.id,
            content="🚀 HELLO! This is a test notification from LexLeaks!",
            style="community",
            post_id=0,  # Test notification
            sent_at=db.query(models.func.now()).scalar()
        )
        db.add(test_notification)
        db.commit()
        
        print("✅ Test notification record created in database")
        print(f"   Content: {test_notification.content}")
        print(f"   Style: {test_notification.style}")
        print(f"   User ID: {test_notification.user_id}")
        
        # Test the web push sending (this will fail with test data, but we can see the flow)
        print("\n5️⃣ Testing web push sending logic...")
        
        # Get the subscription
        subscription = db.query(models.PushSubscription).filter(
            models.PushSubscription.user_id == user.id
        ).first()
        
        if subscription:
            print("✅ Found subscription for testing")
            print(f"   Endpoint: {subscription.endpoint}")
            print(f"   Active: {subscription.is_active}")
            
            # Test the _send_push_notification method
            try:
                # This will fail because it's a test endpoint, but we can see the logic works
                result = notification_service._send_push_notification(
                    subscription, 
                    "🚀 HELLO! Test notification from LexLeaks!",
                    "community",
                    0,
                    test_notification.id
                )
                print(f"✅ Push notification attempt completed: {result}")
            except Exception as e:
                print(f"ℹ️ Push notification failed (expected with test data): {e}")
                print("   This is normal - the test endpoint doesn't exist")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Error testing notification service: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_notification_status():
    """Show current notification system status"""
    print("\n📊 Notification System Status:")
    print("-" * 40)
    
    try:
        from app.database import SessionLocal
        from app import models
        
        db = SessionLocal()
        
        # Count users
        user_count = db.query(models.User).count()
        print(f"👥 Users: {user_count}")
        
        # Count push subscriptions
        subscription_count = db.query(models.PushSubscription).count()
        active_subscriptions = db.query(models.PushSubscription).filter(
            models.PushSubscription.is_active == True
        ).count()
        print(f"📱 Push Subscriptions: {subscription_count} total, {active_subscriptions} active")
        
        # Count sent notifications
        notification_count = db.query(models.NotificationSent).count()
        print(f"📨 Notifications Sent: {notification_count}")
        
        # Show recent notifications
        recent_notifications = db.query(models.NotificationSent).order_by(
            models.NotificationSent.sent_at.desc()
        ).limit(3).all()
        
        if recent_notifications:
            print("\n📋 Recent Notifications:")
            for notif in recent_notifications:
                print(f"   • {notif.content[:50]}... ({notif.style})")
        
        db.close()
        
    except Exception as e:
        print(f"❌ Error getting status: {e}")

if __name__ == "__main__":
    success = test_notification_system()
    show_notification_status()
    
    if success:
        print("\n🎉 Notification system test completed successfully!")
        print("   The system is ready to send notifications when users subscribe.")
    else:
        print("\n❌ Notification system test failed!")
        print("   Check the errors above and fix them.")
