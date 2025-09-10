from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from pydantic import BaseModel

from ..database import get_db
from ..auth import get_current_admin_user
from ..legal_ai_service import legal_ai_service
from ..conversation_router import ConversationRouter

router = APIRouter()

# Structured message models
class StructuredMessage(BaseModel):
    type: str  # 'USER_QUERY' | 'FOLLOWUP' | 'SCOPE_UPDATE' | 'UI_EVENT' | 'META'
    action: Optional[str] = None  # 'RETRY_LAST' | 'WIDEN_SCOPE' | 'NARROW_TO_SC' | etc.
    text: Optional[str] = None
    state_delta: Optional[Dict[str, Any]] = {}

class LegalQueryRequest(BaseModel):
    session_id: Optional[str] = None
    message: StructuredMessage

class LegalQueryResponse(BaseModel):
    session_id: str
    turn_id: str
    answer: Dict[str, Any]
    reasoning_trail: List[Dict[str, Any]]
    citations: List[Dict[str, Any]]
    followups: List[str]
    memory_update: Dict[str, Any]
    telemetry: Dict[str, Any]
    success: bool
    timestamp: str

@router.post("/query", response_model=LegalQueryResponse)
async def process_legal_query(
    request: LegalQueryRequest
):
    """
    Process a structured legal query using JurisBrain AI with conversation routing.
    
    Supports structured messages to separate intent from content:
    - **USER_QUERY**: New legal questions
    - **FOLLOWUP**: Actions like "Try again", "Narrow scope"  
    - **SCOPE_UPDATE**: Update search parameters
    - **META**: General guidance requests
    
    Prevents UI control text from being treated as legal queries.
    Returns comprehensive legal analysis with case law references and current developments.
    """
    try:
        # Initialize conversation router
        conversation_router = ConversationRouter(legal_ai_service)
        
        # Route the conversation turn based on message type
        result = await conversation_router.route_turn(
            message=request.message.dict(),
            session_id=request.session_id
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500, 
                detail=result.get("error", "Failed to process legal query")
            )
        
        return LegalQueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Legal query processing failed: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """
    Check the health of the Legal AI service and its dependencies
    """
    try:
        # Check individual components
        health_status = {
            "service": "JurisBrain AI",
            "status": "healthy",
            "components": {
                "gemini": "unknown",
                "perplexity": "unknown",
                "indian_kanoon": "unknown"
            },
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        # Check Gemini
        if legal_ai_service.gemini_api_key:
            health_status["components"]["gemini"] = "configured"
        else:
            health_status["components"]["gemini"] = "not_configured"
        
        # Check Perplexity
        if legal_ai_service.perplexity_api_key:
            health_status["components"]["perplexity"] = "configured"
        else:
            health_status["components"]["perplexity"] = "not_configured"
        
        # Check Indian Kanoon
        if legal_ai_service.kanoon_service.api_key:
            health_status["components"]["indian_kanoon"] = "configured"
        else:
            health_status["components"]["indian_kanoon"] = "not_configured"
        
        # Overall status
        configured_services = sum(1 for status in health_status["components"].values() if status == "configured")
        if configured_services >= 2:  # Need at least 2 services
            health_status["status"] = "healthy"
        elif configured_services == 1:
            health_status["status"] = "degraded"
        else:
            health_status["status"] = "unhealthy"
        
        return health_status
        
    except Exception as e:
        return {
            "service": "JurisBrain AI",
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
        }

@router.get("/stats")
async def get_service_stats():
    """
    Get statistics about the Legal AI service
    """
    try:
        # This would typically come from a database or analytics service
        # For now, return basic configuration info
        return {
            "service": "JurisBrain AI",
            "configuration": {
                "gemini_configured": bool(legal_ai_service.gemini_api_key),
                "perplexity_configured": bool(legal_ai_service.perplexity_api_key),
                "indian_kanoon_configured": bool(legal_ai_service.kanoon_service.api_key)
            },
            "capabilities": {
                "query_understanding": "Gemini AI",
                "current_research": "Perplexity AI",
                "case_law_search": "Indian Kanoon",
                "synthesis": "Gemini AI"
            },
            "workflow": [
                "User Query",
                "Gemini Understanding",
                "Parallel Research (Perplexity + Indian Kanoon)",
                "Gemini Synthesis",
                "Final Answer"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get service stats: {str(e)}"
        )

@router.post("/test-query")
async def test_legal_query():
    """
    Test the Legal AI service with a sample query
    """
    try:
        test_query = "What are the legal implications of government surveillance in India?"
        test_context = "This is a test query to verify the Legal AI service functionality"
        
        result = await legal_ai_service.process_legal_query(
            query=test_query,
            context=test_context
        )
        
        return {
            "test_query": test_query,
            "test_context": test_context,
            "result": result,
            "test_timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Test query failed: {str(e)}"
        )

@router.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """
    Get information about a specific session
    """
    try:
        result = await legal_ai_service.get_session_info(session_id)
        
        if "error" in result:
            raise HTTPException(
                status_code=404,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session info: {str(e)}"
        )

@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear a session's memory
    """
    try:
        result = legal_ai_service.clear_session(session_id)
        
        if "error" in result:
            raise HTTPException(
                status_code=404,
                detail=result["error"]
            )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear session: {str(e)}"
        )
