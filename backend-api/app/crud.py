from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, asc, func
from datetime import datetime, date
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
    status: Optional[str] = None,
    verification_status: Optional[str] = None,
    search: Optional[str] = None,
    category: Optional[str] = None,
    author_username: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sort_by: Optional[str] = 'newest',
    impact_level: Optional[str] = None  # high, medium, low based on count
) -> List[models.Post]:
    """
    Get posts with advanced filtering, searching, and sorting.
    """
    query = db.query(models.Post)
    
    # Join with User table for author filtering
    if author_username:
        query = query.join(models.User).filter(models.User.username.ilike(f"%{author_username}%"))
    
    # Filter by status
    if status:
        query = query.filter(models.Post.status == status)
    
    # Filter by verification status
    if verification_status:
        query = query.filter(models.Post.verification_status == verification_status)
    
    # Filter by category
    if category:
        query = query.filter(models.Post.category == category)
        
    # Filter by date range
    if date_from:
        query = query.filter(models.Post.published_at >= date_from)
    if date_to:
        query = query.filter(models.Post.published_at <= date_to)
        
    # Search query
    if search:
        search_filter = or_(
            models.Post.title.ilike(f"%{search}%"),
            models.Post.content.ilike(f"%{search}%"),
            models.Post.excerpt.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Filter by impact level
    if impact_level:
        # Create a subquery to count impacts per post
        impact_count_subquery = (
            db.query(
                models.Impact.post_id,
                func.count(models.Impact.id).label('impact_count')
            )
            .group_by(models.Impact.post_id)
            .subquery()
        )
        
        query = query.outerjoin(
            impact_count_subquery,
            models.Post.id == impact_count_subquery.c.post_id
        )
        
        if impact_level == 'high':
            query = query.filter(impact_count_subquery.c.impact_count >= 5)
        elif impact_level == 'medium':
            query = query.filter(impact_count_subquery.c.impact_count.between(2, 4))
        elif impact_level == 'low':
            query = query.filter(
                or_(
                    impact_count_subquery.c.impact_count == 1,
                    impact_count_subquery.c.impact_count.is_(None)
                )
            )

    # Sorting logic
    if sort_by == 'oldest':
        query = query.order_by(asc(models.Post.published_at))
    else: # Default to newest
        query = query.order_by(desc(models.Post.published_at))

    return query.offset(skip).limit(limit).all()


def get_posts_with_counts(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    status: Optional[str] = None,
    verification_status: Optional[str] = None,
    search: Optional[str] = None,
    category: Optional[str] = None,
    author_username: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    sort_by: Optional[str] = 'newest',
    impact_level: Optional[str] = None
) -> List[dict]:
    """
    Get posts with impact counts and advanced filtering.
    """
    # Create a subquery to count impacts per post
    impact_count_subquery = (
        db.query(
            models.Impact.post_id,
            func.count(models.Impact.id).label('impact_count')
        )
        .group_by(models.Impact.post_id)
        .subquery()
    )
    
    # Main query with impact count
    query = db.query(
        models.Post,
        func.coalesce(impact_count_subquery.c.impact_count, 0).label('impact_count')
    ).outerjoin(
        impact_count_subquery,
        models.Post.id == impact_count_subquery.c.post_id
    )
    
    # Join with User table for author filtering
    if author_username:
        query = query.join(models.User).filter(models.User.username.ilike(f"%{author_username}%"))
    
    # Filter by status
    if status:
        query = query.filter(models.Post.status == status)
    
    # Filter by verification status
    if verification_status:
        query = query.filter(models.Post.verification_status == verification_status)
    
    # Filter by category
    if category:
        query = query.filter(models.Post.category == category)
        
    # Filter by date range
    if date_from:
        query = query.filter(models.Post.published_at >= date_from)
    if date_to:
        query = query.filter(models.Post.published_at <= date_to)
        
    # Search query
    if search:
        search_filter = or_(
            models.Post.title.ilike(f"%{search}%"),
            models.Post.content.ilike(f"%{search}%"),
            models.Post.excerpt.ilike(f"%{search}%")
        )
        query = query.filter(search_filter)
    
    # Filter by impact level
    if impact_level:
        if impact_level == 'high':
            query = query.having(func.coalesce(impact_count_subquery.c.impact_count, 0) >= 5)
        elif impact_level == 'medium':
            query = query.having(func.coalesce(impact_count_subquery.c.impact_count, 0).between(2, 4))
        elif impact_level == 'low':
            query = query.having(func.coalesce(impact_count_subquery.c.impact_count, 0) <= 1)

    # Sorting logic
    if sort_by == 'oldest':
        query = query.order_by(asc(models.Post.published_at))
    elif sort_by == 'impact':
        query = query.order_by(desc('impact_count'))
    else: # Default to newest
        query = query.order_by(desc(models.Post.published_at))

    results = query.offset(skip).limit(limit).all()
    
    # Convert to list of dicts with impact_count
    posts_with_counts = []
    for post, impact_count in results:
        post_dict = {
            "id": post.id,
            "title": post.title,
            "slug": post.slug,
            "excerpt": post.excerpt,
            "status": post.status,
            "verification_status": post.verification_status,
            "category": post.category,
            "document_url": post.document_url,
            "published_at": post.published_at,
            "created_at": post.created_at,
            "author": post.author,
            "impact_count": impact_count
        }
        posts_with_counts.append(post_dict)
    
    return posts_with_counts


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
        category=post.category,
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


# Impact CRUD operations
def get_impact(db: Session, impact_id: int) -> Optional[models.Impact]:
    """Get impact by ID"""
    return db.query(models.Impact).filter(models.Impact.id == impact_id).first()


def get_impacts(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    post_id: Optional[int] = None,
    type: Optional[str] = None,
    status: Optional[str] = None
) -> List[models.Impact]:
    """Get impacts with optional filtering"""
    query = db.query(models.Impact)
    
    if post_id:
        query = query.filter(models.Impact.post_id == post_id)
    if type:
        query = query.filter(models.Impact.type == type)
    if status:
        query = query.filter(models.Impact.status == status)
    
    return query.order_by(desc(models.Impact.date)).offset(skip).limit(limit).all()


def create_impact(db: Session, impact: schemas.ImpactCreate) -> models.Impact:
    """Create a new impact"""
    # Verify post exists
    post = get_post(db, impact.post_id)
    if not post:
        raise ValueError("Post not found")
    
    db_impact = models.Impact(
        title=impact.title,
        description=impact.description,
        date=impact.date,
        type=impact.type,
        status=impact.status,
        post_id=impact.post_id
    )
    
    db.add(db_impact)
    db.commit()
    db.refresh(db_impact)
    return db_impact


def update_impact(
    db: Session,
    impact_id: int,
    impact_update: schemas.ImpactUpdate
) -> Optional[models.Impact]:
    """Update an existing impact"""
    db_impact = get_impact(db, impact_id)
    if not db_impact:
        return None
    
    update_data = impact_update.model_dump(exclude_unset=True)
    
    # Apply updates
    for field, value in update_data.items():
        setattr(db_impact, field, value)
    
    db.commit()
    db.refresh(db_impact)
    return db_impact


def delete_impact(db: Session, impact_id: int) -> bool:
    """Delete an impact"""
    db_impact = get_impact(db, impact_id)
    if not db_impact:
        return False
    
    db.delete(db_impact)
    db.commit()
    return True 