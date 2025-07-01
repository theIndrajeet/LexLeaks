from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import crud, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)


@router.get("/", response_model=List[schemas.PostSummary])
def read_posts(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = Query(None, regex="^(draft|published|archived)$"),
    db: Session = Depends(get_db)
):
    """
    Retrieve posts with optional status filter
    """
    posts = crud.get_posts(db, skip=skip, limit=limit, status=status)
    return posts


@router.get("/published", response_model=List[schemas.PostSummary])
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