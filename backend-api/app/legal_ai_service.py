import os
import httpx
import google.generativeai as genai
from typing import Optional, Dict, Any, List
import json
from datetime import datetime
import re
import asyncio
import uuid

from .indian_kanoon_service import IndianKanoonService
from .ai_service import AIContentGenerator

class LegalAIService:
    """
    Enhanced Legal AI Service implementing the workflow:
    User Query → Gemini (Understanding) → Perplexity (Research) → Indian Kanoon (Case Law) → Gemini (Synthesis) → Final Answer
    
    Now with conversational memory and session management
    """
    
    def __init__(self):
        # Initialize services
        self.kanoon_service = IndianKanoonService()
        self.ai_generator = AIContentGenerator()
        
        # API keys
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY")
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Configure Gemini
        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Perplexity API endpoint
        self.perplexity_url = "https://api.perplexity.ai/chat/completions"
        
        # Session management (in-memory for now, can be moved to Redis/DB later)
        self.sessions = {}
    
    async def process_legal_query(self, query: str, context: Optional[str] = None, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Main method implementing the complete legal AI workflow with conversational memory
        
        Args:
            query: User's legal question
            context: Optional additional context
            session_id: Optional session ID for conversational memory
            
        Returns:
            Dictionary containing comprehensive legal analysis with conversational features
        """
        try:
            # Get or create session
            session = self._get_or_create_session(session_id)
            
            # Step 1: Gemini Understanding Phase (with session context)
            query_analysis = await self._gemini_understanding_phase(query, context, session)
            
            # Step 2: Parallel Research Phase (Perplexity + Indian Kanoon)
            research_results = await self._parallel_research_phase(query_analysis)
            
            # Step 3: Gemini Synthesis Phase (with conversational context)
            final_answer = await self._gemini_synthesis_phase(
                query, query_analysis, research_results, session
            )
            
            # Update session memory
            self._update_session_memory(session, query, query_analysis, research_results, final_answer)
            
            # Generate follow-up questions
            follow_ups = await self._generate_follow_up_questions(query, final_answer, session)
            
            # Generate turn ID
            turn_id = f"t_{session['conversation_count']:03d}"
            
            # Extract citations
            citations = self._extract_citations(research_results)
            
            # Build reasoning trail
            reasoning_trail = [
                {"step": "Understanding", "notes": query_analysis.get("strategy", "Analyzing query")},
                {"step": "Research", "notes": f"Found {len(research_results.get('perplexity_results', []))} web sources, {len(research_results.get('kanoon_results', []))} case law results"},
                {"step": "Synthesis", "notes": "Combining sources into comprehensive answer"}
            ]
            
            return {
                "session_id": session["id"],
                "turn_id": turn_id,
                "answer": {
                    "summary": final_answer.get("summary", final_answer.get("comprehensive_answer", "")[:100] + "..."),
                    "text": final_answer.get("comprehensive_answer", ""),
                    "confidence": "high" if self._calculate_confidence_score(research_results) > 0.8 else "medium"
                },
                "reasoning_trail": reasoning_trail,
                "citations": citations,
                "followups": follow_ups,
                "memory_update": {
                    "scope": session.get("scope", {}),
                    "facts": session.get("facts", [])[-5:]  # Last 5 facts
                },
                "telemetry": {
                    "mode": "deep",
                    "tools_used": ["understand", "case_search", "synthesis"],
                    "duration_ms": 0  # TODO: Add timing
                },
                "success": True,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to process legal query: {str(e)}",
                "query": query,
                "session_id": session_id,
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def _gemini_understanding_phase(self, query: str, context: Optional[str] = None, session: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Step 1: Gemini analyzes the query and creates search strategy
        """
        if not self.gemini_api_key:
            return self._fallback_query_analysis(query)
        
        try:
            understanding_prompt = f"""
            You are a legal AI assistant. Analyze this legal query and provide structured information for research.
            
            Query: "{query}"
            Context: "{context or 'No additional context provided'}"
            
            Please provide a JSON response with:
            1. "legal_area": Primary legal domain (e.g., "Constitutional Law", "Criminal Law", "Contract Law")
            2. "key_concepts": Array of key legal concepts to search for
            3. "jurisdiction": Legal jurisdiction (default: "India")
            4. "query_type": Type of query ("precedent_search", "current_law", "recent_developments", "general_legal")
            5. "search_strategy": Object with:
               - "perplexity_focus": What to research on Perplexity (current developments, news, commentary)
               - "kanoon_focus": What to search on Indian Kanoon (case law, precedents, judgments)
            6. "complexity_level": "simple", "moderate", or "complex"
            7. "expected_sources": Array of expected source types
            
            Focus on Indian law unless specified otherwise. Be specific and actionable.
            """
            
            response = self.gemini_model.generate_content(understanding_prompt)
            
            if response.text:
                try:
                    # Try to parse JSON response
                    analysis = json.loads(response.text)
                    return analysis
                except json.JSONDecodeError:
                    # Fallback to text parsing
                    return self._parse_understanding_text(response.text, query)
            
            return self._fallback_query_analysis(query)
            
        except Exception as e:
            return {
                "legal_area": "General Law",
                "key_concepts": query.split()[:5],
                "jurisdiction": "India",
                "query_type": "general_legal",
                "search_strategy": {
                    "perplexity_focus": f"recent developments in {query}",
                    "kanoon_focus": f"case law related to {query}"
                },
                "complexity_level": "moderate",
                "expected_sources": ["case_law", "statutes"],
                "analysis_error": str(e)
            }
    
    async def _parallel_research_phase(self, query_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Step 2: Run Perplexity and Indian Kanoon searches in parallel
        """
        try:
            # Extract search parameters
            key_concepts = query_analysis.get("key_concepts", [])
            perplexity_focus = query_analysis.get("search_strategy", {}).get("perplexity_focus", "")
            kanoon_focus = query_analysis.get("search_strategy", {}).get("kanoon_focus", "")
            
            # Create search queries
            perplexity_query = perplexity_focus or " ".join(key_concepts[:3])
            kanoon_query = kanoon_focus or " ".join(key_concepts[:3])
            
            # Run searches in parallel
            perplexity_task = self._perplexity_research(perplexity_query)
            kanoon_task = self._kanoon_research(kanoon_query)
            
            # Wait for both to complete
            perplexity_results, kanoon_results = await asyncio.gather(
                perplexity_task, kanoon_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(perplexity_results, Exception):
                perplexity_results = {"error": str(perplexity_results)}
            if isinstance(kanoon_results, Exception):
                kanoon_results = {"error": str(kanoon_results)}
            
            return {
                "perplexity_research": perplexity_results,
                "kanoon_case_law": kanoon_results,
                "search_queries": {
                    "perplexity": perplexity_query,
                    "kanoon": kanoon_query
                },
                "research_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "perplexity_research": {"error": f"Research phase failed: {str(e)}"},
                "kanoon_case_law": {"error": f"Research phase failed: {str(e)}"},
                "search_queries": {"perplexity": "", "kanoon": ""},
                "research_timestamp": datetime.utcnow().isoformat()
            }
    
    async def _perplexity_research(self, query: str) -> Dict[str, Any]:
        """
        Research using Perplexity AI for current developments and commentary
        """
        if not self.perplexity_api_key:
            return {"error": "Perplexity API key not configured"}
        
        try:
            research_prompt = f"""
            Research and provide comprehensive information about this legal topic: {query}
            
            Focus on:
            1. Recent legal developments and news
            2. Current laws and regulations
            3. Academic commentary and analysis
            4. Policy implications
            5. Recent court cases or judgments
            
            Provide factual, well-sourced information. Focus on Indian law unless specified otherwise.
            Be comprehensive but concise. Include relevant dates and sources where possible.
            """
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.perplexity_url,
                    headers={
                        "Authorization": f"Bearer {self.perplexity_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "sonar-pro",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a legal research assistant specializing in Indian law. Provide accurate, current, and well-sourced legal information."
                            },
                            {
                                "role": "user",
                                "content": research_prompt
                            }
                        ]
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "research_content": data['choices'][0]['message']['content'],
                        "source": "Perplexity AI",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                else:
                    return {
                        "error": f"Perplexity API error: {response.status_code}",
                        "response": response.text
                    }
                    
        except Exception as e:
            return {"error": f"Perplexity research failed: {str(e)}"}
    
    async def _kanoon_research(self, query: str) -> Dict[str, Any]:
        """
        Research using Indian Kanoon for case law and precedents
        """
        try:
            # Search for cases
            search_results = await self.kanoon_service.search_cases(query, page=0)
            
            if not search_results.get("success"):
                return {
                    "error": f"Indian Kanoon search failed: {search_results.get('error', 'Unknown error')}"
                }
            
            # Get detailed information for top cases
            detailed_cases = []
            cases = search_results.get("results", [])
            
            for case in cases[:5]:  # Limit to top 5 cases
                case_details = await self.kanoon_service.get_case_details(case["doc_id"])
                if case_details.get("success"):
                    detailed_cases.append(case_details)
            
            return {
                "success": True,
                "total_cases_found": search_results.get("total_results", 0),
                "detailed_cases": detailed_cases,
                "search_query": query,
                "source": "Indian Kanoon",
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Indian Kanoon research failed: {str(e)}"}
    
    async def _gemini_synthesis_phase(
        self, 
        original_query: str, 
        query_analysis: Dict[str, Any], 
        research_results: Dict[str, Any],
        session: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Step 3: Gemini synthesizes all research into comprehensive answer
        """
        if not self.gemini_api_key:
            return self._fallback_synthesis(original_query, research_results)
        
        try:
            # Prepare synthesis prompt
            synthesis_prompt = self._create_synthesis_prompt(
                original_query, query_analysis, research_results
            )
            
            response = self.gemini_model.generate_content(synthesis_prompt)
            
            if response.text:
                return {
                    "success": True,
                    "comprehensive_answer": response.text,
                    "synthesis_method": "Gemini AI",
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return self._fallback_synthesis(original_query, research_results)
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Synthesis failed: {str(e)}",
                "fallback_answer": self._create_fallback_answer(original_query, research_results)
            }
    
    def _create_synthesis_prompt(
        self, 
        original_query: str, 
        query_analysis: Dict[str, Any], 
        research_results: Dict[str, Any]
    ) -> str:
        """
        Create comprehensive synthesis prompt for Gemini
        """
        # Extract research content
        perplexity_content = ""
        if research_results.get("perplexity_research", {}).get("success"):
            perplexity_content = research_results["perplexity_research"]["research_content"]
        
        kanoon_cases = research_results.get("kanoon_case_law", {}).get("detailed_cases", [])
        
        # Format case law information
        case_law_context = ""
        if kanoon_cases:
            case_law_context = "\n\nRelevant Case Law from Indian Kanoon:\n"
            for i, case in enumerate(kanoon_cases, 1):
                case_law_context += f"\n{i}. {case.get('title', 'Unknown Case')}\n"
                case_law_context += f"   Court: {case.get('court', 'Unknown')}\n"
                case_law_context += f"   Date: {case.get('date', 'Unknown')}\n"
                case_law_context += f"   Key Points: {case.get('content', '')[:500]}...\n"
                case_law_context += f"   URL: {case.get('url', '')}\n"
        
        return f"""
        You are JurisBrain, an AI legal assistant. Provide a comprehensive, accurate, and helpful answer to this legal question.
        
        Original Query: {original_query}
        
        Query Analysis:
        - Legal Area: {query_analysis.get('legal_area', 'General Law')}
        - Key Concepts: {', '.join(query_analysis.get('key_concepts', []))}
        - Jurisdiction: {query_analysis.get('jurisdiction', 'India')}
        - Query Type: {query_analysis.get('query_type', 'general_legal')}
        
        Current Research and Developments:
        {perplexity_content}
        
        {case_law_context}
        
        Please provide your answer in the following structure:
        
        1. **Quick Take** (2-3 sentences): A clear, concise answer to the question
        
        2. **Detailed Legal Analysis**: 
           - Current legal position
           - Relevant case law and precedents
           - Statutory provisions (if applicable)
           - Recent developments or changes
        
        3. **Practical Implications**: What this means in practice
        
        4. **Important Considerations**: Any caveats, exceptions, or additional factors
        
        5. **Sources and Citations**: Reference the cases and sources used
        
        Make your answer:
        - Accurate and well-researched
        - Easy to understand for non-lawyers
        - Comprehensive but not overwhelming
        - Properly cited with case references
        - Professional and helpful tone
        
        Remember: This is for educational purposes only and does not constitute legal advice.
        """
    
    def _fallback_query_analysis(self, query: str) -> Dict[str, Any]:
        """
        Fallback query analysis when Gemini is not available
        """
        return {
            "legal_area": "General Law",
            "key_concepts": query.split()[:5],
            "jurisdiction": "India",
            "query_type": "general_legal",
            "search_strategy": {
                "perplexity_focus": f"recent developments in {query}",
                "kanoon_focus": f"case law related to {query}"
            },
            "complexity_level": "moderate",
            "expected_sources": ["case_law", "statutes"]
        }
    
    def _parse_understanding_text(self, text: str, query: str) -> Dict[str, Any]:
        """
        Parse Gemini's text response when JSON parsing fails
        """
        return {
            "legal_area": "General Law",
            "key_concepts": query.split()[:5],
            "jurisdiction": "India",
            "query_type": "general_legal",
            "search_strategy": {
                "perplexity_focus": f"recent developments in {query}",
                "kanoon_focus": f"case law related to {query}"
            },
            "complexity_level": "moderate",
            "expected_sources": ["case_law", "statutes"],
            "raw_analysis": text
        }
    
    def _fallback_synthesis(self, query: str, research_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback synthesis when Gemini is not available
        """
        return {
            "success": True,
            "comprehensive_answer": self._create_fallback_answer(query, research_results),
            "synthesis_method": "Fallback",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _create_fallback_answer(self, query: str, research_results: Dict[str, Any]) -> str:
        """
        Create a basic answer when AI synthesis fails
        """
        answer = f"Legal Analysis for: {query}\n\n"
        
        # Add Perplexity research if available
        if research_results.get("perplexity_research", {}).get("success"):
            answer += "Current Developments:\n"
            answer += research_results["perplexity_research"]["research_content"][:500] + "...\n\n"
        
        # Add case law if available
        cases = research_results.get("kanoon_case_law", {}).get("detailed_cases", [])
        if cases:
            answer += "Relevant Case Law:\n"
            for case in cases[:3]:
                answer += f"- {case.get('title', 'Unknown Case')} ({case.get('court', 'Unknown Court')})\n"
        
        answer += "\nNote: This is a basic analysis. For comprehensive legal advice, consult a qualified attorney."
        
        return answer
    
    def _calculate_confidence_score(self, research_results: Dict[str, Any]) -> float:
        """
        Calculate confidence score based on available research
        """
        score = 0.0
        
        # Base score for having a query
        score += 0.1
        
        # Score for Perplexity research
        if research_results.get("perplexity_research", {}).get("success"):
            score += 0.3
        
        # Score for Indian Kanoon research
        kanoon_results = research_results.get("kanoon_case_law", {})
        if kanoon_results.get("success"):
            score += 0.4
            # Bonus for multiple cases
            case_count = len(kanoon_results.get("detailed_cases", []))
            if case_count > 0:
                score += 0.1
            if case_count > 2:
                score += 0.1
        
        return min(score, 1.0)
    
    def _extract_data_sources(self, research_results: Dict[str, Any]) -> List[Dict[str, str]]:
        """
        Extract and format data sources
        """
        sources = []
        
        # Add Perplexity source
        if research_results.get("perplexity_research", {}).get("success"):
            sources.append({
                "name": "Perplexity AI",
                "type": "Current Research",
                "description": "Real-time legal developments and commentary"
            })
        
        # Add Indian Kanoon sources
        cases = research_results.get("kanoon_case_law", {}).get("detailed_cases", [])
        for case in cases:
            sources.append({
                "name": case.get("title", "Unknown Case"),
                "type": "Case Law",
                "court": case.get("court", "Unknown Court"),
                "date": case.get("date", "Unknown Date"),
                "url": case.get("url", "")
            })
        
        return sources
    
    def _extract_citations(self, research_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract citations from research results"""
        citations = []
        pin_counter = 1
        
        # Extract from Indian Kanoon results
        kanoon_results = research_results.get("kanoon_results", [])
        for result in kanoon_results[:5]:  # Limit to top 5
            citations.append({
                "pin": pin_counter,
                "type": "case",
                "title": result.get("title", "Unknown Case"),
                "court_or_source": result.get("court", "Unknown Court"),
                "date": result.get("date", "Unknown Date"),
                "url": result.get("url", ""),
                "snippet": result.get("snippet", "")[:200] + "...",
                "lines": "L1-L50",  # Placeholder
                "weight": "binding"
            })
            pin_counter += 1
        
        # Extract from Perplexity results
        perplexity_results = research_results.get("perplexity_results", [])
        for result in perplexity_results[:3]:  # Limit to top 3
            citations.append({
                "pin": pin_counter,
                "type": "web",
                "title": result.get("title", "Unknown Source"),
                "court_or_source": result.get("domain", "Web Source"),
                "date": result.get("date", "Recent"),
                "url": result.get("url", ""),
                "snippet": result.get("snippet", "")[:200] + "...",
                "lines": "N/A",
                "weight": "secondary"
            })
            pin_counter += 1
        
        return citations
    
    # ===== CONVERSATIONAL FEATURES =====
    
    def _get_or_create_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get existing session or create new one"""
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]
        
        # Create new session
        new_session_id = session_id or str(uuid.uuid4())
        session = {
            "id": new_session_id,
            "created_at": datetime.utcnow().isoformat(),
            "conversation_count": 0,
            "facts": [],
            "scope": {},
            "preferences": {
                "citation_style": "inline_pins",
                "export_format": "pdf",
                "answer_style": "comprehensive"
            },
            "history": []
        }
        
        self.sessions[new_session_id] = session
        return session
    
    def _update_session_memory(self, session: Dict[str, Any], query: str, query_analysis: Dict[str, Any], 
                              research_results: Dict[str, Any], final_answer: Dict[str, Any]):
        """Update session memory with new information"""
        session["conversation_count"] += 1
        
        # Extract facts from query analysis
        if "key_concepts" in query_analysis:
            for concept in query_analysis["key_concepts"]:
                if concept not in session["facts"]:
                    session["facts"].append(concept)
        
        # Update scope
        if "jurisdiction" in query_analysis:
            session["scope"]["jurisdiction"] = query_analysis["jurisdiction"]
        if "legal_area" in query_analysis:
            session["scope"]["legal_area"] = query_analysis["legal_area"]
        
        # Add to history
        session["history"].append({
            "query": query,
            "timestamp": datetime.utcnow().isoformat(),
            "legal_area": query_analysis.get("legal_area", "General Law"),
            "confidence": self._calculate_confidence_score(research_results)
        })
        
        # Keep only last 10 conversations in history
        if len(session["history"]) > 10:
            session["history"] = session["history"][-10:]
    
    async def _generate_follow_up_questions(self, query: str, final_answer: Dict[str, Any], 
                                          session: Dict[str, Any]) -> List[str]:
        """Generate follow-up questions based on the answer and session context"""
        if not self.gemini_api_key:
            return self._get_default_follow_ups(query, session)
        
        try:
            follow_up_prompt = f"""
            Based on this legal query and answer, generate 2-3 relevant follow-up questions that a user might ask.
            
            Original Query: {query}
            Answer: {final_answer.get('comprehensive_answer', '')[:500]}...
            
            Session Context:
            - Legal Area: {session.get('scope', {}).get('legal_area', 'General Law')}
            - Jurisdiction: {session.get('scope', {}).get('jurisdiction', 'India')}
            - Previous Facts: {', '.join(session.get('facts', [])[:5])}
            - Conversation Count: {session.get('conversation_count', 0)}
            
            Generate follow-up questions that:
            1. Are specific and actionable
            2. Build on the current answer
            3. Explore related legal aspects
            4. Are appropriate for the user's level (consider conversation count)
            
            Return as a JSON array of strings.
            """
            
            response = self.gemini_model.generate_content(follow_up_prompt)
            
            if response.text:
                try:
                    follow_ups = json.loads(response.text)
                    return follow_ups[:3]  # Limit to 3 questions
                except json.JSONDecodeError:
                    return self._get_default_follow_ups(query, session)
            
            return self._get_default_follow_ups(query, session)
            
        except Exception as e:
            return self._get_default_follow_ups(query, session)
    
    def _get_default_follow_ups(self, query: str, session: Dict[str, Any]) -> List[str]:
        """Default follow-up questions when AI generation fails"""
        legal_area = session.get('scope', {}).get('legal_area', 'General Law')
        jurisdiction = session.get('scope', {}).get('jurisdiction', 'India')
        
        follow_ups = [
            f"What are the recent developments in {legal_area} in {jurisdiction}?",
            f"Are there any exceptions to this rule in {jurisdiction}?",
            f"What are the practical implications of this in real cases?"
        ]
        
        return follow_ups[:3]
    
    async def get_session_info(self, session_id: str) -> Dict[str, Any]:
        """Get information about a session"""
        if session_id not in self.sessions:
            return {"error": "Session not found"}
        
        session = self.sessions[session_id]
        return {
            "session_id": session_id,
            "created_at": session["created_at"],
            "conversation_count": session["conversation_count"],
            "facts": session["facts"],
            "scope": session["scope"],
            "preferences": session["preferences"],
            "recent_history": session["history"][-3:]  # Last 3 conversations
        }
    
    def clear_session(self, session_id: str) -> Dict[str, str]:
        """Clear a session's memory"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return {"message": "Session cleared successfully"}
        return {"error": "Session not found"}

# Initialize the service
legal_ai_service = LegalAIService()
