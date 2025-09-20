#!/usr/bin/env python3
"""
Quick test script to send a notification
Run this after setting up your VAPID keys and starting your backend
"""

import requests
import json
import os

# Configuration
BACKEND_URL = "http://localhost:8000"  # Change this to your backend URL
ADMIN_TOKEN = "your_admin_token_here"  # You need to get this from your backend

def test_notification():
    """Send a test notification"""
    
    # Test data
    test_data = {
        "title": "🚀 HELLO - Test Notification",
        "body": "This is a test notification from LexLeaks!",
        "style": "community",
        "user_ids": [2]  # Using user ID 2 (heyjeetttt@gmail.com)
    }
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ADMIN_TOKEN}"
    }
    
    try:
        # Send test notification
        response = requests.post(
            f"{BACKEND_URL}/api/notifications/test/2",
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Test notification sent successfully!")
            print(f"Result: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Failed to send notification: {response.status_code}")
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        print("Make sure your backend server is running!")

def check_vapid_key():
    """Check if VAPID key is configured"""
    try:
        response = requests.get(f"{BACKEND_URL}/api/notifications/vapid-key", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ VAPID key is configured")
            print(f"Public key: {data['publicKey'][:20]}...")
            return True
        else:
            print("❌ VAPID key not configured")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing LexLeaks Notification System")
    print("=" * 50)
    
    # Check VAPID key first
    if check_vapid_key():
        print("\n📱 Sending test notification...")
        test_notification()
    else:
        print("\n⚠️ Please configure VAPID keys first!")
        print("Add these to your backend .env file:")
        print("VAPID_PUBLIC_KEY=BBzBPZHNrYd4yMkW5THmC2vPYHfausBF5_eCaql-9eo8c0Y2ibr6O0znOXLZ7zAs9qSYf1GfHJIcaKF1XWo5BMY")
        print("VAPID_PRIVATE_KEY=gc-RA0w3RET4Zyd4HGAnk-L_KFtRO61NtxGO8f849xQ")
