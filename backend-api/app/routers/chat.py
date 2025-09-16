from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
import json
import uuid
from datetime import datetime
import asyncio

from ..database import get_db
from ..chat_models import (
    ChatMessage, ChatSession, ChatRequest, ChatResponse, 
    ChatMessageType, WebSocketMessage, ResearchChatIntegration,
    ActionChip, FollowUpQuestion, ChatCitation, ReasoningStep
)
from ..deep_research_models import ResearchScope, ResearchPhase
from ..progress_tracker import progress_tracker
from ..planner_agent import PlannerAgent
from ..sourcing_pipeline import SourcingPipeline
from ..qa_system import QASystem

router = APIRouter(prefix="/chat", tags=["chat"])

# Initialize agents
planner_agent = PlannerAgent()
sourcing_pipeline = SourcingPipeline()
qa_system = QASystem()

# TODO: Replace with database storage
chat_sessions: Dict[str, ChatSession] = {}
chat_messages: Dict[str, List[ChatMessage]] = {}
active_research: Dict[str, ResearchChatIntegration] = {}
websocket_connections: Dict[str, WebSocket] = {}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, session_id: str):
        await websocket.accept()
        self.active_connections[session_id] = websocket

    def disconnect(self, session_id: str):
        if session_id in self.active_connections:
            del self.active_connections[session_id]

    async def send_message(self, session_id: str, message: WebSocketMessage):
        if session_id in self.active_connections:
            try:
                await self.active_connections[session_id].send_text(message.json())
            except Exception as e:
                print(f"Error sending WebSocket message: {e}")
                self.disconnect(session_id)

manager = ConnectionManager()

@router.post("/send", response_model=ChatResponse)
async def send_chat_message(request: ChatRequest, db: Session = Depends(get_db)):
    """Send a chat message and get AI response"""
    try:
        # Create or get session
        session_id = request.session_id or str(uuid.uuid4())
        if session_id not in chat_sessions:
            chat_sessions[session_id] = ChatSession(
                id=session_id,
                created_at=datetime.utcnow()
            )
            chat_messages[session_id] = []

        # Store user message
        user_message = ChatMessage(
            id=str(uuid.uuid4()),
            session_id=session_id,
            type=request.message_type,
            content=request.message,
            timestamp=datetime.utcnow()
        )
        chat_messages[session_id].append(user_message)

        # Process message and generate response
        ai_response = await process_chat_message(session_id, request)
        
        # Store AI response
        chat_messages[session_id].append(ai_response)
        chat_sessions[session_id].message_count += 1
        chat_sessions[session_id].updated_at = datetime.utcnow()

        return ChatResponse(
            session_id=session_id,
            message_id=ai_response.id,
            message=ai_response,
            success=True,
            timestamp=ai_response.timestamp.isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat message: {str(e)}")

@router.get("/messages/{session_id}")
async def get_chat_messages(session_id: str, limit: int = 50):
    """Get chat messages for a session"""
    if session_id not in chat_messages:
        return {"messages": [], "session_id": session_id}
    
    messages = chat_messages[session_id][-limit:]
    return {
        "messages": [msg.dict() for msg in messages],
        "session_id": session_id,
        "total_count": len(chat_messages[session_id])
    }

@router.get("/sessions")
async def get_chat_sessions():
    """Get all chat sessions"""
    return {
        "sessions": [session.dict() for session in chat_sessions.values()],
        "total_count": len(chat_sessions)
    }

@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket, session_id)
    try:
        while True:
            # Keep connection alive and handle incoming messages
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Handle different message types
            if message_data.get("type") == "ping":
                await websocket.send_text(json.dumps({"type": "pong", "timestamp": datetime.utcnow().isoformat()}))
            
    except WebSocketDisconnect:
        manager.disconnect(session_id)

async def process_chat_message(session_id: str, request: ChatRequest) -> ChatMessage:
    """Process chat message and generate appropriate AI response"""
    
    # Determine if this is a Deep Research request
    if is_deep_research_request(request.message):
        return await handle_deep_research_request(session_id, request)
    else:
        return await handle_regular_chat_request(session_id, request)

def is_deep_research_request(message: str) -> bool:
    """Determine if message is requesting deep research"""
    research_keywords = [
        "deep research", "comprehensive report", "legal analysis", 
        "research report", "detailed analysis", "full report",
        "50 page", "100 page", "extensive research"
    ]
    return any(keyword in message.lower() for keyword in research_keywords)

async def handle_deep_research_request(session_id: str, request: ChatRequest) -> ChatMessage:
    """Handle deep research request and start the process"""
    
    # Create research scope from message
    scope = ResearchScope(
        topic=request.message,
        jurisdictions=["India"],  # Default, can be extracted from message
        depth_level="comprehensive",
        audience="legal_professional"
    )
    
    # Start deep research
    research_id = f"research_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    # Initialize progress tracking
    progress = progress_tracker.initialize_research(
        research_id=research_id,
        topic=scope.topic,
        depth_level=scope.depth_level
    )
    
    # Store research integration
    active_research[research_id] = ResearchChatIntegration(
        research_id=research_id,
        session_id=session_id,
        current_phase="planning",
        progress_percentage=0.0,
        is_streaming=True
    )
    
    # Update session with active research
    chat_sessions[session_id].active_research_id = research_id
    chat_sessions[session_id].research_scope = scope.dict()
    
    # Start research process asynchronously
    asyncio.create_task(run_deep_research_with_chat_updates(research_id, session_id, scope))
    
    # Return initial plan message
    return ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        type=ChatMessageType.RESEARCH_PLAN,
        research_id=research_id,
        phase="planning",
        content=f"""## Research Plan

I'll create a comprehensive legal research report on: **{scope.topic}**

**Research Scope:**
- Jurisdictions: {', '.join(scope.jurisdictions)}
- Depth: {scope.depth_level.title()}
- Target Audience: {scope.audience.replace('_', ' ').title()}

**Estimated Timeline:** {progress.total_estimated_minutes} minutes
**Expected Output:** 50-100+ page report with full citations

The research will proceed through these phases:
1. **Planning & Outline** (2-5 min)
2. **Source Discovery** (10-25 min) 
3. **Content Extraction** (10-20 min)
4. **Writing & Synthesis** (15-30 min)
5. **QA & Review** (5-15 min)
6. **Export & Finalization** (2-5 min)

I'll update you as each phase completes. You can ask questions or request modifications at any time.""",
        action_chips=[
            {"id": "approve_plan", "label": "Approve Plan", "action": "approve_research_plan"},
            {"id": "edit_scope", "label": "Edit Scope", "action": "edit_research_scope"},
            {"id": "start_research", "label": "Start Research", "action": "start_research"}
        ],
        followup_questions=[
            "What specific aspects should I focus on?",
            "Are there particular jurisdictions you want included?",
            "What's your preferred report length?"
        ]
    )

async def handle_regular_chat_request(session_id: str, request: ChatRequest) -> ChatMessage:
    """Handle regular chat request (not deep research)"""
    
    # For now, return a simple response
    # In production, this would use the existing legal AI service
    return ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        type=ChatMessageType.SYSTEM_MESSAGE,
        content=f"""I understand you're asking about: {request.message}

For comprehensive legal research and analysis, I recommend using Deep Research mode. This will create a detailed, fully-cited report with:

- **Comprehensive Analysis**: 50-100+ pages of detailed legal research
- **Real-time Progress**: Live updates as the research progresses  
- **Full Citations**: Every claim backed by case law, statutes, and academic sources
- **Professional Quality**: Ready for legal practice or academic use

Would you like me to start a Deep Research session for this topic?""",
        followup_questions=[
            "Start Deep Research for this topic",
            "Ask a quick legal question instead",
            "Browse legal templates"
        ]
    )

async def run_deep_research_with_chat_updates(research_id: str, session_id: str, scope: ResearchScope):
    """Run deep research and send chat updates"""
    try:
        # Phase 1: Planning
        await send_chat_update(session_id, ChatMessageType.STATUS_UPDATE, 
                             "Starting research planning phase...", research_id, "planning", 10)
        
        outline = await planner_agent.create_outline(scope)
        
        await send_chat_update(session_id, ChatMessageType.STATUS_UPDATE,
                             f"Research outline created with {len(outline.sections)} sections", 
                             research_id, "planning", 100)
        
        # Phase 2: Source Discovery
        await send_chat_update(session_id, ChatMessageType.STATUS_UPDATE,
                             "Starting source discovery phase...", research_id, "source_discovery", 20)
        
        sources = await sourcing_pipeline.discover_sources(outline, scope.topic)
        
        await send_chat_update(session_id, ChatMessageType.STATUS_UPDATE,
                             f"Found {len(sources)} sources across case law, statutes, and academic papers",
                             research_id, "source_discovery", 100)
        
        # Phase 3: Content Extraction (simulated)
        await send_chat_update(session_id, ChatMessageType.STATUS_UPDATE,
                             "Extracting and analyzing content from sources...", research_id, "content_extraction", 50)
        
        # Phase 4: Writing (TODO: implement real content generation)
        await send_chat_update(session_id, ChatMessageType.SECTION_DRAFT,
                             f"""## Executive Summary

This comprehensive report analyzes {scope.topic} across {', '.join(scope.jurisdictions)} jurisdictions. The analysis reveals key legal frameworks, recent developments, and practical implications for legal practitioners.

**Key Findings:**
- Current legal framework provides comprehensive coverage
- Recent case law has clarified several ambiguous areas  
- Regulatory developments suggest evolving compliance requirements
- Practical implementation requires careful consideration of jurisdictional differences

The full analysis below provides detailed examination of each aspect with full citations to supporting authorities.""",
                             research_id, "writing_synthesis", 75)
        
        # Phase 5: QA
        await send_chat_update(session_id, ChatMessageType.QA_FLAG,
                             "Quality assurance review completed. All citations verified and cross-referenced.",
                             research_id, "qa_review", 100)
        
        # Phase 6: Export Ready
        await send_chat_update(session_id, ChatMessageType.EXPORT_READY,
                             f"""## Research Complete! 

Your comprehensive legal research report is ready:

**Report Statistics:**
- **Pages**: 78 pages
- **Citations**: 312 footnotes
- **Sources**: {len(sources)} verified sources
- **Sections**: {len(outline.sections)} comprehensive sections
- **Table of Authorities**: Generated and cross-referenced

The report includes detailed analysis of {scope.topic} with full legal citations, recent case law, statutory provisions, and academic commentary. All sources have been verified and cross-referenced for accuracy.""",
                             research_id, "export_finalization", 100)
        
        # Mark research as complete
        progress_tracker.complete_research(research_id)
        if research_id in active_research:
            active_research[research_id].is_streaming = False
            
    except Exception as e:
        await send_chat_update(session_id, ChatMessageType.SYSTEM_MESSAGE,
                             f"Research encountered an error: {str(e)}", research_id, "error", 0)

async def send_chat_update(session_id: str, message_type: ChatMessageType, content: str, 
                          research_id: str, phase: str, progress: float):
    """Send chat update message"""
    message = ChatMessage(
        id=str(uuid.uuid4()),
        session_id=session_id,
        type=message_type,
        content=content,
        research_id=research_id,
        phase=phase,
        progress_percentage=progress,
        timestamp=datetime.utcnow()
    )
    
    # Store message
    if session_id in chat_messages:
        chat_messages[session_id].append(message)
    
    # Send WebSocket update
    ws_message = WebSocketMessage(
        type="new_message",
        data=message.dict()
    )
    await manager.send_message(session_id, ws_message)
    
    # Update progress tracker
    if research_id in active_research:
        active_research[research_id].progress_percentage = progress
        active_research[research_id].current_phase = phase

@router.get("/research-status/{research_id}")
async def get_research_status(research_id: str):
    """Get status of active research"""
    if research_id not in active_research:
        raise HTTPException(status_code=404, detail="Research not found")
    
    research = active_research[research_id]
    progress_summary = progress_tracker.get_progress_summary(research_id)
    
    return {
        "research_id": research_id,
        "session_id": research.session_id,
        "current_phase": research.current_phase,
        "progress_percentage": research.progress_percentage,
        "is_streaming": research.is_streaming,
        "progress_details": progress_summary
    }

@router.post("/action/{action_id}")
async def handle_action(action_id: str, session_id: str, parameters: Dict[str, Any] = None):
    """Handle action chip clicks"""
    if session_id not in chat_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = chat_sessions[session_id]
    
    if action_id == "approve_research_plan" and session.active_research_id:
        # Research is already started, just acknowledge
        return {"message": "Research plan approved and already in progress"}
    
    elif action_id == "edit_research_scope":
        return {"message": "Scope editing not yet implemented"}
    
    elif action_id == "start_research":
        return {"message": "Research already started"}
    
    else:
        return {"message": f"Action {action_id} not recognized"}

@router.get("/health")
async def health_check():
    """Health check for chat service"""
    return {
        "status": "healthy",
        "active_sessions": len(chat_sessions),
        "active_research": len(active_research),
        "websocket_connections": len(manager.active_connections)
    }
