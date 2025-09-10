"""
Conversation Router for JurisBrain AI

Implements server-authoritative routing for structured messages.
Separates intent from content and handles follow-up actions properly.
"""

from typing import Dict, Any, Optional
from .legal_ai_service import LegalAIService

class ConversationRouter:
    """
    Routes conversation turns based on message type and action.
    Prevents UI control text from being treated as legal queries.
    """
    
    def __init__(self, legal_ai_service: LegalAIService):
        self.legal_ai_service = legal_ai_service
        # Control phrases that should never be treated as legal queries
        self.CONTROL_SET = {
            "try again", "retry", "simplify your question", "refresh", 
            "simplify", "again", "more details", "explain further",
            "narrow", "widen", "show more", "show less"
        }
    
    async def route_turn(self, message: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Route the conversation turn based on message type and action.
        
        Args:
            message: Structured message with type, action, text, and state_delta
            session_id: Optional session ID for continuity
            
        Returns:
            Response following the strict contract format
        """
        try:
            # Get or create session
            session = self.legal_ai_service._get_or_create_session(session_id)
            
            msg_type = message.get("type", "USER_QUERY")
            action = message.get("action")
            text = message.get("text")
            state_delta = message.get("state_delta", {})
            
            # Route based on message type
            if msg_type == "FOLLOWUP":
                return await self._handle_followup(action, session, state_delta)
            elif msg_type == "SCOPE_UPDATE":
                return await self._handle_scope_update(session, state_delta)
            elif msg_type == "USER_QUERY":
                return await self._handle_user_query(text, session)
            elif msg_type == "META":
                return self._handle_meta_request()
            else:
                # Safety net for control phrases
                if text and (self._is_control_phrase(text) or len(text.split()) < 3):
                    return await self._handle_followup("RETRY_LAST", session, {})
                return await self._handle_user_query(text, session)
                
        except Exception as e:
            return self._error_response(f"Routing failed: {str(e)}", session_id)
    
    def _is_control_phrase(self, text: str) -> bool:
        """Check if text is a UI control phrase"""
        return text.strip().lower() in self.CONTROL_SET
    
    async def _handle_followup(self, action: str, session: Dict[str, Any], state_delta: Dict[str, Any]) -> Dict[str, Any]:
        """Handle follow-up actions like RETRY_LAST, NARROW_SCOPE, etc."""
        
        if action == "RETRY_LAST":
            # Get the last user query from session
            last_query = session.get("last_user_query")
            if last_query:
                return await self.legal_ai_service.process_legal_query(
                    query=last_query,
                    session_id=session["id"],
                    context="Retrying previous query"
                )
            else:
                return self._error_response("No previous query to retry", session["id"])
                
        elif action == "NARROW_TO_SC":
            # Update scope to Supreme Court only
            if "scope" not in session:
                session["scope"] = {}
            session["scope"]["court"] = "SC"
            session["scope"]["date_range"] = "2017-present"  # Recent SC cases
            
            last_query = session.get("last_user_query")
            if last_query:
                return await self.legal_ai_service.process_legal_query(
                    query=last_query,
                    session_id=session["id"],
                    context="Narrowed scope to Supreme Court cases"
                )
            else:
                return self._error_response("No previous query to re-run with narrowed scope", session["id"])
                
        elif action == "WIDEN_SCOPE":
            # Widen the scope to all courts
            if "scope" not in session:
                session["scope"] = {}
            session["scope"]["court"] = "All"
            session["scope"]["date_range"] = "2010-present"  # Wider date range
            
            last_query = session.get("last_user_query")
            if last_query:
                return await self.legal_ai_service.process_legal_query(
                    query=last_query,
                    session_id=session["id"],
                    context="Widened scope to all courts"
                )
            else:
                return self._error_response("No previous query to re-run with widened scope", session["id"])
                
        elif action == "SIMPLIFY_ANSWER":
            # Re-run with simplified output preference
            if "preferences" not in session:
                session["preferences"] = {}
            session["preferences"]["style"] = "concise"
            
            last_query = session.get("last_user_query")
            if last_query:
                return await self.legal_ai_service.process_legal_query(
                    query=last_query,
                    session_id=session["id"],
                    context="Providing simplified answer"
                )
            else:
                return self._error_response("No previous query to simplify", session["id"])
                
        elif action == "EXPAND_ANSWER":
            # Re-run with detailed output preference
            if "preferences" not in session:
                session["preferences"] = {}
            session["preferences"]["style"] = "detailed"
            
            last_query = session.get("last_user_query")
            if last_query:
                return await self.legal_ai_service.process_legal_query(
                    query=last_query,
                    session_id=session["id"],
                    context="Providing detailed answer"
                )
            else:
                return self._error_response("No previous query to expand", session["id"])
        
        return self._error_response(f"Unknown follow-up action: {action}", session["id"])
    
    async def _handle_scope_update(self, session: Dict[str, Any], state_delta: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scope updates"""
        if "scope" in state_delta:
            if "scope" not in session:
                session["scope"] = {}
            session["scope"].update(state_delta["scope"])
        
        last_query = session.get("last_user_query")
        if last_query:
            return await self.legal_ai_service.process_legal_query(
                query=last_query,
                session_id=session["id"],
                context="Updated search scope"
            )
        
        return self._error_response("No previous query to re-run with updated scope", session["id"])
    
    async def _handle_user_query(self, text: str, session: Dict[str, Any]) -> Dict[str, Any]:
        """Handle new user queries"""
        if not text or not text.strip():
            return self._error_response("No query text provided", session["id"])
        
        # Store the query in session for future follow-ups
        session["last_user_query"] = text.strip()
        
        return await self.legal_ai_service.process_legal_query(
            query=text.strip(),
            session_id=session["id"]
        )
    
    def _handle_meta_request(self) -> Dict[str, Any]:
        """Handle meta requests"""
        return {
            "success": True,
            "session_id": "new",
            "turn_id": "meta_001",
            "answer": {
                "summary": "What would you like to do next?",
                "text": "What would you like to do next?",
                "confidence": "high"
            },
            "reasoning_trail": [
                {"step": "Meta", "notes": "Providing guidance options"}
            ],
            "citations": [],
            "followups": [
                "Ask a legal question",
                "Search case law", 
                "Get recent updates"
            ],
            "memory_update": {
                "scope": {"jurisdiction": "India"},
                "facts": []
            },
            "telemetry": {
                "mode": "meta",
                "tools_used": ["guidance"],
                "duration_ms": 0
            },
            "timestamp": "2025-01-01T00:00:00.000000"
        }
    
    def _error_response(self, error_message: str, session_id: Optional[str]) -> Dict[str, Any]:
        """Generate standardized error response"""
        return {
            "success": False,
            "error": error_message,
            "session_id": session_id or "error",
            "turn_id": "error_001",
            "answer": {
                "summary": "Error occurred",
                "text": f"Sorry, I encountered an error: {error_message}",
                "confidence": "low"
            },
            "reasoning_trail": [
                {"step": "Error", "notes": error_message}
            ],
            "citations": [],
            "followups": ["Try again", "Ask a different question"],
            "memory_update": {"scope": {}, "facts": []},
            "telemetry": {
                "mode": "error",
                "tools_used": [],
                "duration_ms": 0
            },
            "timestamp": "2025-01-01T00:00:00.000000"
        }
