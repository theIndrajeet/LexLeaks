from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from .. import crud, schemas, auth
from ..database import get_db

router = APIRouter(
    prefix="/impacts",
    tags=["impacts"]
)


@router.get("/", response_model=List[schemas.ImpactResponse])
def read_impacts(
    skip: int = 0,
    limit: int = 100,
    post_id: Optional[int] = Query(None, description="Filter by post ID"),
    type: Optional[str] = Query(None, regex="^(legal_action|policy_change|investigation|resignation|reform)$"),
    status: Optional[str] = Query(None, regex="^(pending|in_progress|completed)$"),
    db: Session = Depends(get_db)
):
    """
    Retrieve impacts with optional filtering
    """
    impacts = crud.get_impacts(db, skip=skip, limit=limit, post_id=post_id, type=type, status=status)
    return impacts


@router.post("/", response_model=schemas.ImpactResponse, status_code=status.HTTP_201_CREATED)
def create_impact(
    impact: schemas.ImpactCreate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    """
    Create a new impact (requires authentication)
    """
    # Only admins can create impacts
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create impacts"
        )
    
    try:
        return crud.create_impact(db=db, impact=impact)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{impact_id}", response_model=schemas.ImpactResponse)
def read_impact(impact_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a specific impact by ID
    """
    db_impact = crud.get_impact(db, impact_id=impact_id)
    if db_impact is None:
        raise HTTPException(status_code=404, detail="Impact not found")
    return db_impact


@router.put("/{impact_id}", response_model=schemas.ImpactResponse)
def update_impact(
    impact_id: int,
    impact: schemas.ImpactUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    """
    Update an impact (requires admin authentication)
    """
    # Only admins can update impacts
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can update impacts"
        )
    
    updated_impact = crud.update_impact(db=db, impact_id=impact_id, impact_update=impact)
    if updated_impact is None:
        raise HTTPException(status_code=404, detail="Impact not found")
    
    return updated_impact


@router.delete("/{impact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_impact(
    impact_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(auth.get_current_user)
):
    """
    Delete an impact (requires admin authentication)
    """
    # Only admins can delete impacts
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can delete impacts"
        )
    
    success = crud.delete_impact(db=db, impact_id=impact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Impact not found")
    
    return None 