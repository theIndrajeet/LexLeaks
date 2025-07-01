#!/usr/bin/env python3
import requests

API_BASE = "https://lexleaks-api-563011146464.asia-south1.run.app"

# Test 1: Check API is alive
print("1. Testing API health...")
r = requests.get(f"{API_BASE}/health")
print(f"   Status: {r.status_code}")
print(f"   Response: {r.text}")

# Test 2: Login
print("\n2. Testing login...")
login_data = {
    "username": "admin",
    "password": "LexLeaks2024!"
}
r = requests.post(f"{API_BASE}/api/auth/login", data=login_data)
print(f"   Status: {r.status_code}")
print(f"   Response: {r.text[:200]}...")

if r.status_code == 200:
    token = r.json()["access_token"]
    print(f"   Token: {token[:50]}...")
    
    # Test 3: Create a post
    print("\n3. Testing post creation...")
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    post_data = {
        "title": "Test Post",
        "content": "This is a test post content.",
        "excerpt": "Test excerpt",
        "status": "published"
    }
    r = requests.post(f"{API_BASE}/api/posts", headers=headers, json=post_data)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text}")
    
    # Test 4: Get posts
    print("\n4. Testing get posts...")
    r = requests.get(f"{API_BASE}/api/posts/published")
    print(f"   Status: {r.status_code}")
    print(f"   Posts count: {len(r.json())}") 