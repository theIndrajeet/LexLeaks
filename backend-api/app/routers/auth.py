from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from .. import crud, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)


@router.post("/login", response_model=schemas.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT token
    """
    user = crud.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/json", response_model=schemas.Token)
async def login_json(
    login_data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Alternative login endpoint that accepts JSON instead of form data
    """
    user = crud.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user = Depends(auth.get_current_user)):
    """
    Get current user information
    """
    return current_user


@router.post("/register", response_model=schemas.UserResponse)
async def register(
    user: schemas.UserCreate,
    db: Session = Depends(get_db),
    # Uncomment the line below to require admin privileges for user creation
    # current_user = Depends(auth.get_current_admin_user)
):
    """
    Register a new user (currently open, but can be restricted to admins)
    """
    # Check if username already exists
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Username already registered"
        )
    
    # Create user
    return crud.create_user(db=db, user=user) 