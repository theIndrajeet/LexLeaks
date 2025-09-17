from fastapi import APIRouter, Depends, HTTPException, Header
from typing import Optional
from ..supabase_auth import supabase_auth

router = APIRouter(prefix="/api/auth/supabase", tags=["supabase-auth"])

def get_current_user(authorization: Optional[str] = Header(None)):
    """Get current user from Supabase token"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")
    
    # Extract token from "Bearer <token>"
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    
    user = supabase_auth.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return user

@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current user info"""
    return current_user

@router.get("/user/{user_id}")
async def get_user_by_id(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get user by ID (admin only)"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = supabase_auth.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return user
