from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import crud, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


@router.get("/", response_model=List[schemas.PostWithCounts])
def read_posts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, regex="^(draft|published|archived)$"),
    verification_status: Optional[str] = Query(None, regex="^(unverified|verified|disputed)$"),
    search: Optional[str] = Query(None, min_length=1, description="Search query for title, content, and excerpt"),
    category: Optional[str] = Query(None, description="Filter by category"),
    author: Optional[str] = Query(None, description="Filter by author username"),
    date_from: Optional[date] = Query(None, description="Filter posts published on or after this date"),
    date_to: Optional[date] = Query(None, description="Filter posts published on or before this date"),
    sort_by: Optional[str] = Query('newest', regex="^(newest|oldest|impact)$", description="Sort order"),
    impact_level: Optional[str] = Query(None, regex="^(high|medium|low)$", description="Filter by impact level"),
    db: Session = Depends(get_db)
):
    """
    Retrieve posts with advanced filtering, searching, and sorting.
    - **status**: Filter by post status (draft, published, archived).
    - **verification_status**: Filter by verification status (unverified, verified, disputed).
    - **search**: Search query to filter by title, content, or excerpt.
    - **category**: Filter by a specific category.
    - **author**: Filter by author username (partial match).
    - **date_from / date_to**: Filter by a date range (YYYY-MM-DD).
    - **sort_by**: Sort by 'newest', 'oldest', or 'impact' (most impactful).
    - **impact_level**: Filter by impact level - 'high' (5+ impacts), 'medium' (2-4), 'low' (0-1).
    """
    posts = crud.get_posts_with_counts(
        db, 
        skip=skip, 
        limit=limit, 
        status=status,
        verification_status=verification_status,
        search=search,
        category=category,
        author_username=author,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        impact_level=impact_level
    )
    return posts


@router.get("/published", response_model=List[schemas.PostSummary], deprecated=True)
def read_published_posts(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve only published posts for public consumption
    """
    posts = crud.get_published_posts(db, skip=skip, limit=limit)
    return posts


@router.get("/search", response_model=List[schemas.PostSummary])
def search_posts(
    q: str = Query(..., min_length=1, description="Search query"),
    status: Optional[str] = Query(None, regex="^(draft|published|archived)$"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Search posts by title or content
    """
    posts = crud.search_posts(db, query=q, status=status, skip=skip, limit=limit)
    return posts


@router.post("/", response_model=schemas.PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post: schemas.PostCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    """
    Create a new post (requires authentication)
    """
    return crud.create_post(db=db, post=post, author_id=current_user.id)


@router.get("/{post_id}", response_model=schemas.PostResponse)
def read_post(post_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific post by ID
    """
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post


@router.get("/slug/{slug}", response_model=schemas.PostResponse)
def read_post_by_slug(slug: str, db: Session = Depends(get_db)):
    """
    Retrieve a specific post by slug (for public URLs)
    """
    db_post = crud.get_post_by_slug(db, slug=slug)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return db_post


@router.put("/{post_id}", response_model=schemas.PostResponse)
def update_post(
    post_id: int,
    post: schemas.PostUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    """
    Update a post (requires authentication)
    """
    # Check if post exists
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user owns the post or is admin
    admin_username = "admin"  # This should match your ADMIN_USERNAME
    if db_post.author_id != current_user.id and current_user.username != admin_username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to edit this post"
        )
    
    updated_post = crud.update_post(db=db, post_id=post_id, post_update=post)
    if updated_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return updated_post


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    """
    Delete a post (requires authentication)
    """
    # Check if post exists
    db_post = crud.get_post(db, post_id=post_id)
    if db_post is None:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check if user owns the post or is admin
    admin_username = "admin"  # This should match your ADMIN_USERNAME
    if db_post.author_id != current_user.id and current_user.username != admin_username:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to delete this post"
        )
    
    success = crud.delete_post(db=db, post_id=post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return None 