from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from pydantic import BaseModel

from ..indian_kanoon_service import IndianKanoonService

router = APIRouter()

# Initialize the service
kanoon_service = IndianKanoonService()

class CaseSearchRequest(BaseModel):
    query: str
    page: int = 0
    court_type: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None

class CaseSearchResponse(BaseModel):
    success: bool
    query: str
    page: int
    total_results: int
    cases: list
    error: Optional[str] = None

class CaseDetailsResponse(BaseModel):
    success: bool
    doc_id: str
    title: str
    court: str
    date: str
    judges: list
    parties: list
    content: str
    citations: list
    url: str
    related_cases: list
    error: Optional[str] = None

@router.get("/search", response_model=CaseSearchResponse)
async def search_cases(
    query: str = Query(..., description="Search query for cases"),
    page: int = Query(0, description="Page number (starting from 0)"),
    court_type: Optional[str] = Query(None, description="Filter by court type"),
    date_from: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="End date (YYYY-MM-DD)")
):
    """
    Search for legal cases using Indian Kanoon API
    
    - **query**: Search terms (case title, keywords, etc.)
    - **page**: Page number for pagination (default: 0)
    - **court_type**: Optional court filter
    - **date_from**: Optional start date filter
    - **date_to**: Optional end date filter
    """
    try:
        # Perform the search
        raw_results = await kanoon_service.search_cases(
            query=query,
            page=page,
            court_type=court_type,
            date_from=date_from,
            date_to=date_to
        )
        
        if not raw_results.get("success"):
            raise HTTPException(
                status_code=500,
                detail=raw_results.get("error", "Failed to search cases")
            )
        
        return CaseSearchResponse(**raw_results)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/case/{doc_id}", response_model=CaseDetailsResponse)
async def get_case_details(doc_id: str):
    """
    Get full details of a specific case by document ID
    
    - **doc_id**: Document ID from search results
    """
    try:
        # Get case details
        raw_details = await kanoon_service.get_case_details(doc_id)
        
        if not raw_details.get("success"):
            raise HTTPException(
                status_code=500,
                detail=raw_details.get("error", "Failed to fetch case details")
            )
        
        return CaseDetailsResponse(**raw_details)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/case/{doc_id}/original", response_model=CaseDetailsResponse)
async def get_case_original(doc_id: str):
    """
    Get original document of a case (complete text)
    
    - **doc_id**: Document ID from search results
    """
    try:
        # Get original document
        raw_details = await kanoon_service.get_case_original(doc_id)
        
        if not raw_details.get("success"):
            raise HTTPException(
                status_code=500,
                detail=raw_details.get("error", "Failed to fetch original document")
            )
        
        return CaseDetailsResponse(**raw_details)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Health check endpoint for Indian Kanoon service
    """
    return {
        "status": "healthy",
        "service": "Indian Kanoon API",
        "api_key_configured": bool(kanoon_service.api_key)
    }
