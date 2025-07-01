#!/usr/bin/env python3
"""Test script for Impact tracking API endpoints"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Optional

# Configuration
BASE_URL = "http://localhost:8000/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "LexLeaks2024!"

# Color codes for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_test(test_name: str, passed: bool, details: str = ""):
    """Print test result with color"""
    status = f"{GREEN}PASSED{RESET}" if passed else f"{RED}FAILED{RESET}"
    print(f"{test_name}: {status}")
    if details:
        print(f"  {details}")

def get_auth_token() -> Optional[str]:
    """Get authentication token for admin user"""
    print(f"\n{BLUE}Getting authentication token...{RESET}")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": ADMIN_USERNAME,
            "password": ADMIN_PASSWORD
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print_test("Authentication", True, f"Token obtained successfully")
        return token
    else:
        print_test("Authentication", False, f"Status: {response.status_code}, Error: {response.text}")
        return None

def get_headers(token: str) -> Dict[str, str]:
    """Get headers with authentication"""
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

def test_create_impact(token: str, post_id: int) -> Optional[int]:
    """Test creating a new impact"""
    print(f"\n{BLUE}Testing POST /api/impacts/{RESET}")
    
    impact_data = {
        "title": "Test Investigation Launched",
        "description": "Following our test exposé, an investigation was launched into the matter.",
        "date": datetime.now().isoformat(),
        "type": "investigation",
        "status": "in_progress",
        "post_id": post_id
    }
    
    response = requests.post(
        f"{BASE_URL}/impacts/",
        json=impact_data,
        headers=get_headers(token)
    )
    
    if response.status_code == 201:
        impact = response.json()
        print_test("Create Impact", True, f"Created impact with ID: {impact['id']}")
        return impact['id']
    else:
        print_test("Create Impact", False, f"Status: {response.status_code}, Error: {response.text}")
        return None

def test_get_impact(impact_id: int):
    """Test getting a specific impact"""
    print(f"\n{BLUE}Testing GET /api/impacts/{{id}}{RESET}")
    
    response = requests.get(f"{BASE_URL}/impacts/{impact_id}")
    
    if response.status_code == 200:
        impact = response.json()
        print_test("Get Impact by ID", True, f"Retrieved impact: {impact['title']}")
        return True
    else:
        print_test("Get Impact by ID", False, f"Status: {response.status_code}, Error: {response.text}")
        return False

def test_list_impacts(post_id: Optional[int] = None):
    """Test listing impacts with optional filters"""
    print(f"\n{BLUE}Testing GET /api/impacts/{RESET}")
    
    params = {}
    if post_id:
        params['post_id'] = post_id
    
    response = requests.get(f"{BASE_URL}/impacts/", params=params)
    
    if response.status_code == 200:
        impacts = response.json()
        print_test("List Impacts", True, f"Retrieved {len(impacts)} impacts")
        return True
    else:
        print_test("List Impacts", False, f"Status: {response.status_code}, Error: {response.text}")
        return False

def test_update_impact(token: str, impact_id: int):
    """Test updating an impact"""
    print(f"\n{BLUE}Testing PUT /api/impacts/{{id}}{RESET}")
    
    update_data = {
        "status": "completed",
        "description": "The investigation has been completed with significant findings."
    }
    
    response = requests.put(
        f"{BASE_URL}/impacts/{impact_id}",
        json=update_data,
        headers=get_headers(token)
    )
    
    if response.status_code == 200:
        impact = response.json()
        print_test("Update Impact", True, f"Updated status to: {impact['status']}")
        return True
    else:
        print_test("Update Impact", False, f"Status: {response.status_code}, Error: {response.text}")
        return False

def test_filter_impacts():
    """Test filtering impacts by type and status"""
    print(f"\n{BLUE}Testing GET /api/impacts/ with filters{RESET}")
    
    # Test filter by type
    response = requests.get(f"{BASE_URL}/impacts/", params={"type": "investigation"})
    if response.status_code == 200:
        impacts = response.json()
        print_test("Filter by Type", True, f"Found {len(impacts)} investigation impacts")
    else:
        print_test("Filter by Type", False, f"Status: {response.status_code}")
    
    # Test filter by status
    response = requests.get(f"{BASE_URL}/impacts/", params={"status": "completed"})
    if response.status_code == 200:
        impacts = response.json()
        print_test("Filter by Status", True, f"Found {len(impacts)} completed impacts")
    else:
        print_test("Filter by Status", False, f"Status: {response.status_code}")

def test_delete_impact(token: str, impact_id: int):
    """Test deleting an impact"""
    print(f"\n{BLUE}Testing DELETE /api/impacts/{{id}}{RESET}")
    
    response = requests.delete(
        f"{BASE_URL}/impacts/{impact_id}",
        headers=get_headers(token)
    )
    
    if response.status_code == 204:
        print_test("Delete Impact", True, "Impact deleted successfully")
        return True
    else:
        print_test("Delete Impact", False, f"Status: {response.status_code}, Error: {response.text}")
        return False

def test_unauthorized_access():
    """Test that non-admin users cannot create/update/delete impacts"""
    print(f"\n{BLUE}Testing Unauthorized Access{RESET}")
    
    # Try to create without token
    response = requests.post(
        f"{BASE_URL}/impacts/",
        json={"title": "Unauthorized", "description": "Test", "date": datetime.now().isoformat(), 
              "type": "investigation", "status": "pending", "post_id": 1}
    )
    print_test("Unauthorized Create", response.status_code == 401, f"Status: {response.status_code}")
    
    # Try to update without token
    response = requests.put(f"{BASE_URL}/impacts/1", json={"status": "completed"})
    print_test("Unauthorized Update", response.status_code == 401, f"Status: {response.status_code}")
    
    # Try to delete without token
    response = requests.delete(f"{BASE_URL}/impacts/1")
    print_test("Unauthorized Delete", response.status_code == 401, f"Status: {response.status_code}")

def get_first_post_id(token: str) -> Optional[int]:
    """Get the ID of the first published post"""
    response = requests.get(f"{BASE_URL}/posts/", params={"status": "published", "limit": 1})
    if response.status_code == 200 and response.json():
        return response.json()[0]['id']
    return None

def main():
    """Run all impact API tests"""
    print(f"{YELLOW}=== Testing Impact Tracking API ==={RESET}")
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print(f"{RED}Cannot proceed without authentication token{RESET}")
        return
    
    # Get a post ID to associate impacts with
    post_id = get_first_post_id(token)
    if not post_id:
        print(f"{YELLOW}No published posts found. Creating impacts without specific post.{RESET}")
        post_id = 1  # Fallback to ID 1
    
    # Test unauthorized access
    test_unauthorized_access()
    
    # Test creating an impact
    impact_id = test_create_impact(token, post_id)
    if not impact_id:
        print(f"{RED}Cannot proceed without creating an impact{RESET}")
        return
    
    # Test getting the created impact
    test_get_impact(impact_id)
    
    # Test listing impacts
    test_list_impacts()
    test_list_impacts(post_id)
    
    # Test filtering impacts
    test_filter_impacts()
    
    # Test updating the impact
    test_update_impact(token, impact_id)
    
    # Create additional test impacts for filtering
    print(f"\n{BLUE}Creating additional test impacts...{RESET}")
    impact_types = [
        ("legal_action", "Legal Action Filed", "A lawsuit was filed against the firm"),
        ("policy_change", "New Policy Enacted", "New regulations were introduced"),
        ("resignation", "Partner Resigned", "Senior partner stepped down"),
        ("reform", "Internal Reform", "Company implemented new ethics guidelines")
    ]
    
    for impact_type, title, description in impact_types:
        data = {
            "title": title,
            "description": description,
            "date": (datetime.now() - timedelta(days=10)).isoformat(),
            "type": impact_type,
            "status": "completed" if impact_type in ["resignation", "reform"] else "pending",
            "post_id": post_id
        }
        response = requests.post(f"{BASE_URL}/impacts/", json=data, headers=get_headers(token))
        if response.status_code == 201:
            print(f"  Created {impact_type} impact")
    
    # Test comprehensive filtering
    print(f"\n{BLUE}Testing comprehensive filtering...{RESET}")
    test_filter_impacts()
    
    # Test deleting an impact
    test_delete_impact(token, impact_id)
    
    # Verify deletion
    response = requests.get(f"{BASE_URL}/impacts/{impact_id}")
    print_test("Verify Deletion", response.status_code == 404, f"Impact no longer exists")
    
    print(f"\n{YELLOW}=== All Impact API Tests Completed ==={RESET}")

if __name__ == "__main__":
    main() 