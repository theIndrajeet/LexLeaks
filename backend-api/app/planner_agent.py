import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
import google.generativeai as genai
from .config import GEMINI_API_KEY
from .deep_research_models import ResearchScope, ReportOutline, Section

class PlannerAgent:
    """Creates comprehensive legal research outlines"""
    
    def __init__(self):
        self.gemini_model = None
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-pro')
    
    async def create_outline(self, scope: ResearchScope) -> ReportOutline:
        """Generate a comprehensive research outline"""
        
        # Create the outline using Gemini
        outline_data = await self._generate_outline_with_gemini(scope)
        
        # Parse and structure the outline
        outline = self._parse_outline_data(outline_data, scope)
        
        return outline
    
    async def _generate_outline_with_gemini(self, scope: ResearchScope) -> Dict[str, Any]:
        """Use Gemini to generate the research outline"""
        
        prompt = f"""You are a legal research expert. Create a comprehensive legal research outline for: {scope.topic}

Context:
- Jurisdiction: {', '.join(scope.jurisdictions)}
- Time Window: {scope.time_window or 'All relevant time periods'}
- Audience: {scope.audience}
- Depth Level: {scope.depth_level}
- Focus Areas: {', '.join(scope.focus_areas) if scope.focus_areas else 'All relevant areas'}

IMPORTANT: Respond ONLY with valid JSON. Do not include any explanatory text, markdown formatting, or code blocks.

Create an outline with exactly 6 main sections following this structure:

{{
  "title": "Comprehensive Legal Research Report: {scope.topic}",
  "sections": [
    {{
      "id": "section_1",
      "title": "Executive Summary",
      "outline_path": "1",
      "estimated_pages": 3,
      "required_sources": ["statute", "case", "guidance"],
      "priority": "high"
    }},
    {{
      "id": "section_2",
      "title": "Legal Framework Analysis",
      "outline_path": "2",
      "estimated_pages": 15,
      "required_sources": ["statute", "regulation", "guidance"],
      "priority": "high"
    }},
    {{
      "id": "section_3",
      "title": "Case Law Synthesis",
      "outline_path": "3",
      "estimated_pages": 20,
      "required_sources": ["case", "order"],
      "priority": "high"
    }},
    {{
      "id": "section_4",
      "title": "Practical Implementation",
      "outline_path": "4",
      "estimated_pages": 10,
      "required_sources": ["guidance", "order", "news"],
      "priority": "medium"
    }},
    {{
      "id": "section_5",
      "title": "Risk Assessment",
      "outline_path": "5",
      "estimated_pages": 10,
      "required_sources": ["case", "order", "guidance"],
      "priority": "high"
    }},
    {{
      "id": "section_6",
      "title": "Appendices",
      "outline_path": "6",
      "estimated_pages": 10,
      "required_sources": ["case", "statute", "guidance"],
      "priority": "low"
    }}
  ],
  "total_estimated_pages": 68,
  "research_plan": {{
    "primary_sources": ["Indian Kanoon", "Government Gazettes", "Supreme Court Website"],
    "secondary_sources": ["Perplexity", "Academic Papers", "Legal Journals"],
    "estimated_duration": "45 minutes",
    "quality_requirements": [
      "Minimum 1 citation per 80-120 words",
      "Primary sources first (statutes > SC cases > HC cases > commentary)",
      "Sources ≤18 months old for current developments",
      "Bluebook citation format"
    ]
  }}
}}

Customize the section titles and content to be specific to "{scope.topic}" while maintaining this exact JSON structure."""
        
        if self.gemini_model:
            try:
                response = self.gemini_model.generate_content(prompt)
                
                # Check if response has content
                if not response.text or not response.text.strip():
                    print("Gemini returned empty response, using fallback")
                    return self._create_fallback_outline(scope)
                
                # Clean the response text (remove markdown code blocks if present)
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text.replace('```json', '').replace('```', '').strip()
                elif response_text.startswith('```'):
                    response_text = response_text.replace('```', '').strip()
                
                # Try to parse JSON
                outline_data = json.loads(response_text)
                print(f"Successfully generated outline with Gemini: {outline_data.get('title', 'Unknown')}")
                return outline_data
                
            except json.JSONDecodeError as e:
                print(f"Error parsing Gemini JSON response: {e}")
                print(f"Raw response: {response.text[:200]}...")
                return self._create_fallback_outline(scope)
            except Exception as e:
                print(f"Error generating outline with Gemini: {e}")
                return self._create_fallback_outline(scope)
        else:
            print("No Gemini API key configured, using fallback")
            return self._create_fallback_outline(scope)
    
    def _create_fallback_outline(self, scope: ResearchScope) -> Dict[str, Any]:
        """Create a fallback outline when Gemini is not available"""
        
        return {
            "title": f"Legal Research Report: {scope.topic}",
            "sections": [
                {
                    "id": "section_1",
                    "title": "Executive Summary",
                    "outline_path": "1",
                    "estimated_pages": 3,
                    "required_sources": ["statute", "case", "guidance"],
                    "priority": "high"
                },
                {
                    "id": "section_2",
                    "title": "Legal Framework Analysis",
                    "outline_path": "2",
                    "estimated_pages": 15,
                    "required_sources": ["statute", "regulation", "guidance"],
                    "priority": "high"
                },
                {
                    "id": "section_3",
                    "title": "Case Law Synthesis",
                    "outline_path": "3",
                    "estimated_pages": 20,
                    "required_sources": ["case", "order"],
                    "priority": "high"
                },
                {
                    "id": "section_4",
                    "title": "Practical Implementation",
                    "outline_path": "4",
                    "estimated_pages": 10,
                    "required_sources": ["guidance", "order", "news"],
                    "priority": "medium"
                },
                {
                    "id": "section_5",
                    "title": "Risk Assessment",
                    "outline_path": "5",
                    "estimated_pages": 10,
                    "required_sources": ["case", "order", "guidance"],
                    "priority": "high"
                },
                {
                    "id": "section_6",
                    "title": "Appendices",
                    "outline_path": "6",
                    "estimated_pages": 10,
                    "required_sources": ["case", "statute", "guidance"],
                    "priority": "low"
                }
            ],
            "total_estimated_pages": 68,
            "research_plan": {
                "primary_sources": ["Indian Kanoon", "Government Gazettes", "Supreme Court Website"],
                "secondary_sources": ["Perplexity", "Academic Papers", "Legal Journals"],
                "estimated_duration": "45 minutes",
                "quality_requirements": [
                    "Minimum 1 citation per 80-120 words",
                    "Primary sources first (statutes > SC cases > HC cases > commentary)",
                    "Sources ≤18 months old for current developments",
                    "Bluebook citation format"
                ]
            }
        }
    
    def _parse_outline_data(self, outline_data: Dict[str, Any], scope: ResearchScope) -> ReportOutline:
        """Parse the outline data into a ReportOutline object"""
        
        sections = []
        for section_data in outline_data["sections"]:
            section = Section(
                id=section_data["id"],
                title=section_data["title"],
                outline_path=section_data["outline_path"],
                estimated_pages=section_data["estimated_pages"],
                status="planned"
            )
            sections.append(section)
        
        outline = ReportOutline(
            id=f"outline_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            title=outline_data["title"],
            sections=sections,
            total_estimated_pages=outline_data["total_estimated_pages"],
            research_plan=outline_data["research_plan"],
            approved=False
        )
        
        return outline
    
    async def refine_outline(self, outline: ReportOutline, feedback: str) -> ReportOutline:
        """Refine the outline based on user feedback"""
        
        prompt = f"""
        Refine this legal research outline based on the feedback: {feedback}
        
        Current outline:
        {json.dumps(outline.dict(), indent=2)}
        
        Please provide an improved version that addresses the feedback while maintaining the comprehensive structure.
        Return the same JSON format as before.
        """
        
        if self.gemini_model:
            try:
                response = self.gemini_model.generate_content(prompt)
                refined_data = json.loads(response.text)
                return self._parse_outline_data(refined_data, ResearchScope(topic=outline.title))
            except Exception as e:
                print(f"Error refining outline: {e}")
                return outline
        else:
            return outline
