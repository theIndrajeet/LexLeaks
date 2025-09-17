from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from . import crud, schemas
from .database import get_db
from .supabase_auth import supabase_auth

load_dotenv()

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

if not SECRET_KEY:
    SECRET_KEY = "default-secret-key-for-development-only"
    print("Warning: Using default SECRET_KEY. Set SECRET_KEY environment variable for production.")

# Security scheme
security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[str]:
    """Verify and decode JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        return username
    except JWTError:
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
    
    token = credentials.credentials
    
    # First, try Supabase authentication
    try:
        supabase_user = supabase_auth.verify_token(token)
        if supabase_user:
            # Create a user object that matches the expected format
            class SupabaseUser:
                def __init__(self, user_data):
                    self.id = user_data["id"]
                    self.email = user_data["email"]
                    self.name = user_data["name"]
                    self.is_admin = user_data["is_admin"]
                    self.username = user_data["email"]  # Use email as username
            
            return SupabaseUser(supabase_user)
    except Exception as e:
        print(f"Supabase auth failed: {e}")
        # Fall back to legacy auth
    
    # Fallback to legacy JWT authentication
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Try to find user by ID (for OAuth users)
    user = crud.get_user_by_id(db, user_id=int(user_id))
    
    # If not found by ID, try by username (for traditional users, though username might be None for OAuth)
    if user is None:
        username: Optional[str] = payload.get("username") # Fallback for traditional users
        if username:
            user = crud.get_user_by_username(db, username=username)
    
    if user is None:
        raise credentials_exception
    
    return user


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