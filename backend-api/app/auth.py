import os
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import requests

from . import crud, schemas
from .database import get_db

load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "43200"))  # 30 days

if not SECRET_KEY:
    SECRET_KEY = "default-secret-key-for-development-only"
    print("Warning: Using default SECRET_KEY. Set SECRET_KEY environment variable for production.")

# Security scheme
security = HTTPBearer()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def verify_supabase_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify Supabase JWT token"""
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        print("Warning: Supabase configuration missing")
        return None
    
    try:
        # Use Supabase's user verification endpoint
        response = requests.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": SUPABASE_SERVICE_ROLE_KEY
            }
        )
        
        if response.status_code == 200:
            user_data = response.json()
            return {
                "id": user_data.get("id"),
                "email": user_data.get("email"),
                "name": user_data.get("user_metadata", {}).get("full_name", user_data.get("email")),
                "is_admin": user_data.get("user_metadata", {}).get("is_admin", False)
            }
        return None
    except Exception as e:
        print(f"Supabase token verification failed: {e}")
        return None

# Legacy JWT functions removed - using Supabase Auth exclusively

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Dependency to get the current authenticated user - Supabase Auth only"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    
    # Use Supabase authentication exclusively
    supabase_user = verify_supabase_token(token)
    if not supabase_user:
        raise credentials_exception
    
    # Create a user object that matches the expected format
    class SupabaseUser:
        def __init__(self, user_data):
            self.id = user_data["id"]
            self.email = user_data["email"]
            self.name = user_data["name"]
            self.is_admin = user_data["is_admin"]
            self.username = user_data["email"]  # Use email as username
    
    return SupabaseUser(supabase_user)

# Optional: Admin-only dependency
async def get_current_admin_user(
    current_user = Depends(get_current_user)
):
    """Dependency to ensure the current user is an admin"""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return current_user
