from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from enum import Enum

# Chat Message Types for Deep Research
class ChatMessageType(str, Enum):
    USER_QUERY = "user_query"
    RESEARCH_PLAN = "research_plan"
    STATUS_UPDATE = "status_update"
    SECTION_DRAFT = "section_draft"
    QA_FLAG = "qa_flag"
    EXPORT_READY = "export_ready"
    SYSTEM_MESSAGE = "system_message"

# Chat Message Model
class ChatMessage(BaseModel):
    id: str
    session_id: str
    type: ChatMessageType
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Deep Research specific fields
    research_id: Optional[str] = None
    phase: Optional[str] = None
    progress_percentage: Optional[float] = None
    
    # Message metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    # For AI messages
    reasoning_trail: Optional[List[Dict[str, Any]]] = None
    citations: Optional[List[Dict[str, Any]]] = None
    followup_questions: Optional[List[str]] = None
    action_chips: Optional[List[Dict[str, Any]]] = None

# Chat Session Model
class ChatSession(BaseModel):
    id: str
    user_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Active research
    active_research_id: Optional[str] = None
    research_scope: Optional[Dict[str, Any]] = None
    
    # Session state
    is_active: bool = True
    message_count: int = 0

# Chat Request/Response Models
class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    message_type: ChatMessageType = ChatMessageType.USER_QUERY
    research_scope: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    session_id: str
    message_id: str
    message: ChatMessage
    success: bool
    timestamp: str

# WebSocket Message Models
class WebSocketMessage(BaseModel):
    type: Literal["progress_update", "status_change", "new_message", "research_complete", "error"]
    data: Dict[str, Any]
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

# Research Integration Models
class ResearchChatIntegration(BaseModel):
    research_id: str
    session_id: str
    current_phase: str
    progress_percentage: float
    last_message_id: Optional[str] = None
    is_streaming: bool = False

# Action Chip Models
class ActionChip(BaseModel):
    id: str
    label: str
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True

# Follow-up Question Model
class FollowUpQuestion(BaseModel):
    id: str
    text: str
    action: str
    parameters: Dict[str, Any] = Field(default_factory=dict)

# Citation Model for Chat
class ChatCitation(BaseModel):
    id: str
    title: str
    url: str
    court_or_source: str
    date: str
    type: str  # 'case', 'statute', 'news', 'academic'
    trust_score: float
    pin_number: int

# Reasoning Step Model
class ReasoningStep(BaseModel):
    step: str
    notes: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    phase: Optional[str] = None
