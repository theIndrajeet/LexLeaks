import os
from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import requests

from . import crud, schemas, models
from .database import get_db

load_dotenv()

# Supabase-only auth: remove legacy JWT paths

# Security scheme (allow missing Authorization for optional routes)
security = HTTPBearer(auto_error=False)

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

def create_access_token(*args, **kwargs):
    raise NotImplementedError("Legacy JWT token creation is disabled. Use Supabase Auth.")

def verify_token(*args, **kwargs):
    return None

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Dependency to get the current authenticated user - supports both Supabase and legacy auth"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if credentials is None or not getattr(credentials, "credentials", None):
        # No Authorization header provided
        raise credentials_exception

    token = credentials.credentials
    
    # Supabase authentication only
    supabase_user = verify_supabase_token(token)
    if supabase_user:
        # Ensure local user record exists for roles/preferences
        try:
            existing = (
                db.query(models.User)
                .filter(models.User.email == supabase_user.get("email"))
                .first()
            )
            if not existing:
                new_user = models.User(
                    email=supabase_user.get("email"),
                    full_name=supabase_user.get("name"),
                    oauth_provider="supabase",
                    is_admin=bool(supabase_user.get("is_admin", False)),
                )
                db.add(new_user)
                db.commit()
            else:
                # Keep admin flag in sync if changed
                desired_admin = bool(supabase_user.get("is_admin", False))
                if existing.is_admin != desired_admin:
                    existing.is_admin = desired_admin
                    db.add(existing)
                    db.commit()
        except Exception:
            pass

        # Create a user object that matches the expected format for dependency usage
        class SupabaseUser:
            def __init__(self, user_data):
                self.id = user_data["id"]
                self.email = user_data["email"]
                self.name = user_data["name"]
                self.is_admin = user_data["is_admin"]
                self.username = user_data["email"]  # Use email as username
        
        return SupabaseUser(supabase_user)
    
    raise credentials_exception

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


# Optional current-user dependency that does not raise on failure
async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
):
    try:
        if credentials is None:
            return None
        return await get_current_user(credentials=credentials, db=db)
    except Exception:
        return None
