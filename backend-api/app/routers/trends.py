from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from pydantic import BaseModel

from ..database import get_db
from ..auth import get_current_admin_user
from ..trends_service import trends_service

router = APIRouter()

class TrendingTopicResponse(BaseModel):
    topic: str
    category: str
    trend_score: int
    suggested_article_type: str
    suggested_template: str
    interest_value: int = None

class TrendsResponse(BaseModel):
    trending_topics: List[TrendingTopicResponse]
    last_updated: str = None
    total_found: int
    categories: List[str]

@router.get("/trends/legal-topics", response_model=TrendsResponse)
async def get_trending_legal_topics(
    current_user = Depends(get_current_admin_user)
):
    """Get trending legal topics for article suggestions"""
    try:
        result = await trends_service.get_topic_suggestions_for_cms()
        return TrendsResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch trending topics: {str(e)}")

@router.post("/trends/refresh")
async def refresh_trending_topics(
    current_user = Depends(get_current_admin_user)
):
    """Manually refresh trending topics cache"""
    try:
        await trends_service.get_trending_legal_topics()
        return {"message": "Trending topics refreshed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh trends: {str(e)}")
