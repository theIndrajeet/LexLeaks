from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from typing import List, Optional
from . import models, schemas
from .schemas import generate_slug
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# User CRUD operations
def get_user(db: Session, user_id: int) -> Optional[models.User]:
    """Get user by ID"""
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    """Get user by username"""
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    """Create a new user"""
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    """Authenticate a user"""
    user = get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# Post CRUD operations
def get_post(db: Session, post_id: int) -> Optional[models.Post]:
    """Get post by ID"""
    return db.query(models.Post).filter(models.Post.id == post_id).first()


def get_post_by_slug(db: Session, slug: str) -> Optional[models.Post]:
    """Get post by slug"""
    return db.query(models.Post).filter(models.Post.slug == slug).first()


def get_posts(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None
) -> List[models.Post]:
    """Get posts with optional status filter"""
    query = db.query(models.Post)
    
    if status:
        query = query.filter(models.Post.status == status)
    
    return query.offset(skip).limit(limit).all()


def get_published_posts(db: Session, skip: int = 0, limit: int = 100) -> List[models.Post]:
    """Get only published posts, ordered by publish date"""
    return (
        db.query(models.Post)
        .filter(models.Post.status == "published")
        .filter(models.Post.published_at.isnot(None))
        .order_by(models.Post.published_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def create_post(db: Session, post: schemas.PostCreate, author_id: int) -> models.Post:
    """Create a new post"""
    # Generate unique slug
    base_slug = generate_slug(post.title)
    slug = base_slug
    counter = 1
    
    while get_post_by_slug(db, slug):
        slug = f"{base_slug}-{counter}"
        counter += 1
    
    # Set published_at if status is published
    published_at = datetime.utcnow() if post.status == "published" else None
    
    db_post = models.Post(
        title=post.title,
        slug=slug,
        content=post.content,
        excerpt=post.excerpt,
        status=post.status,
        author_id=author_id,
        published_at=published_at
    )
    
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def update_post(
    db: Session, 
    post_id: int, 
    post_update: schemas.PostUpdate
) -> Optional[models.Post]:
    """Update an existing post"""
    db_post = get_post(db, post_id)
    if not db_post:
        return None
    
    update_data = post_update.model_dump(exclude_unset=True)
    
    # Handle slug regeneration if title changed
    if "title" in update_data:
        new_slug = generate_slug(update_data["title"])
        if new_slug != db_post.slug:
            # Ensure slug uniqueness
            base_slug = new_slug
            counter = 1
            while get_post_by_slug(db, new_slug) and new_slug != db_post.slug:
                new_slug = f"{base_slug}-{counter}"
                counter += 1
            update_data["slug"] = new_slug
    
    # Handle published_at timestamp
    if "status" in update_data:
        if update_data["status"] == "published" and not db_post.published_at:
            update_data["published_at"] = datetime.utcnow()
        elif update_data["status"] != "published":
            update_data["published_at"] = None
    
    # Apply updates
    for field, value in update_data.items():
        setattr(db_post, field, value)
    
    db.commit()
    db.refresh(db_post)
    return db_post


def delete_post(db: Session, post_id: int) -> bool:
    """Delete a post"""
    db_post = get_post(db, post_id)
    if not db_post:
        return False
    
    db.delete(db_post)
    db.commit()
    return True


def search_posts(
    db: Session, 
    query: str, 
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[models.Post]:
    """Search posts by title or content"""
    search_filter = or_(
        models.Post.title.ilike(f"%{query}%"),
        models.Post.content.ilike(f"%{query}%")
    )
    
    db_query = db.query(models.Post).filter(search_filter)
    
    if status:
        db_query = db_query.filter(models.Post.status == status)
    
    return db_query.offset(skip).limit(limit).all() 