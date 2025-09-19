from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
import secrets
import os
from urllib.parse import urlencode

from ..database import get_db
from ..models import User
from ..google_oauth import google_oauth
from ..auth import get_current_user
from ..schemas import UserResponse, TokenResponse

router = APIRouter()

@router.get("/google/login")
async def google_login(request: Request, state: Optional[str] = None):
    """Initiate Google OAuth login"""
    # Generate state parameter for security
    if not state:
        state = secrets.token_urlsafe(32)
    
    # Store state in session or return it to frontend
    authorization_url = google_oauth.get_authorization_url(state=state)
    
    return {
        "authorization_url": authorization_url,
        "state": state
    }

@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        # Exchange code for tokens
        tokens = google_oauth.exchange_code_for_token(code)
        
        # Verify ID token and get user info
        user_info = google_oauth.verify_id_token(tokens["id_token"])
        
        # Check if user exists
        user = db.query(User).filter(
            (User.google_id == user_info["sub"]) | 
            (User.email == user_info["email"])
        ).first()
        
        if not user:
            # Create new user
            user = User(
                email=user_info["email"],
                full_name=user_info["name"],
                google_id=user_info["sub"],
                profile_picture=user_info.get("picture"),
                oauth_provider="google",
                is_admin=False  # Default to non-admin, can be changed manually
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        else:
            # Update existing user with Google info if needed
            if not user.google_id:
                user.google_id = user_info["sub"]
                user.oauth_provider = "google"
                if not user.profile_picture:
                    user.profile_picture = user_info.get("picture")
                if not user.email:
                    user.email = user_info["email"]
                if not user.full_name:
                    user.full_name = user_info["name"]
                db.commit()
        
        # Redirect to frontend with user info (Supabase handles auth)
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        redirect_url = f"{frontend_url}/auth/callback?user_id={user.id}&email={user.email}"
        
        return RedirectResponse(url=redirect_url)
        
    except Exception as e:
        # Redirect to frontend with error
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        error_url = f"{frontend_url}/auth/error?error={str(e)}"
        return RedirectResponse(url=error_url)

@router.get("/google/user-info")
async def get_google_user_info(current_user: User = Depends(get_current_user)):
    """Get current user's Google profile info"""
    if current_user.oauth_provider != "google":
        raise HTTPException(status_code=400, detail="User is not authenticated via Google")
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.full_name,
        "picture": current_user.profile_picture,
        "is_admin": current_user.is_admin,
        "username": current_user.username
    }

@router.post("/google/assign-admin")
async def assign_admin_role(
    user_id: int,
    is_admin: bool,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Assign admin role to user (admin only)"""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_admin = is_admin
    db.commit()
    
    return {"message": f"Admin status updated to {is_admin} for user {user.email or user.username}"}
