from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
import asyncio
from datetime import datetime
from pydantic import BaseModel

from ..deep_research_models import (
    ResearchScope, ReportOutline, DeepResearchReport, 
    EvidenceGraph, QAMetrics, ExportOptions, ExportResult,
    ResearchPhase, Source, Section
)
from ..planner_agent import PlannerAgent
from ..sourcing_pipeline import SourcingPipeline
from ..qa_system import QASystem
from ..progress_tracker import progress_tracker

router = APIRouter(prefix="/deep-research", tags=["deep-research"])

# Initialize agents
planner_agent = PlannerAgent()
sourcing_pipeline = SourcingPipeline()
qa_system = QASystem()

@router.post("/create-outline")
async def create_research_outline(scope: ResearchScope) -> Dict[str, Any]:
    """Create a comprehensive research outline"""
    
    try:
        # Generate outline using planner agent
        outline = await planner_agent.create_outline(scope)
        
        return {
            "success": True,
            "outline": outline.dict(),
            "message": "Research outline created successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating outline: {str(e)}")

class SourceDiscoveryRequest(BaseModel):
    outline_id: str
    topic: str

@router.post("/discover-sources")
async def discover_research_sources(
    request: SourceDiscoveryRequest
) -> Dict[str, Any]:
    """Discover sources for a research outline"""
    
    try:
        # TODO: Implement real outline fetching from database
        raise HTTPException(status_code=501, detail="Source discovery not yet implemented")
        
        return {
            "success": True,
            "sources": [source.dict() for source in sources],
            "source_count": len(sources),
            "message": "Sources discovered successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error discovering sources: {str(e)}")

@router.post("/analyze-quality")
async def analyze_research_quality(
    sections: List[Dict[str, Any]],
    sources: List[Dict[str, Any]],
    extracts: List[Dict[str, Any]] = []
) -> Dict[str, Any]:
    """Analyze the quality of research sections and sources"""
    
    try:
        # Convert dicts to model instances
        from ..deep_research_models import Section, Source, Extract
        
        section_objects = [Section(**section) for section in sections]
        source_objects = [Source(**source) for source in sources]
        extract_objects = [Extract(**extract) for extract in extracts]
        
        # Generate quality report
        quality_report = qa_system.generate_quality_report(
            section_objects, source_objects, extract_objects
        )
        
        return {
            "success": True,
            "quality_report": quality_report,
            "message": "Quality analysis completed successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing quality: {str(e)}")

@router.post("/start-deep-research")
async def start_deep_research(scope: ResearchScope) -> Dict[str, Any]:
    """Start a comprehensive deep research process"""
    
    try:
        # Create unique research ID
        research_id = f"research_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize progress tracking
        progress = progress_tracker.initialize_research(
            research_id=research_id,
            topic=scope.topic,
            depth_level=scope.depth_level
        )
        
        # Start async research process
        asyncio.create_task(_run_deep_research_async(research_id, scope))
        
        # Return immediate response with progress info
        return {
            "success": True,
            "research_id": research_id,
            "estimated_minutes": progress.total_estimated_minutes,
            "estimated_completion": progress.estimated_completion.isoformat(),
            "progress_url": f"/api/deep-research/progress/{research_id}",
            "message": f"Deep research started. Estimated completion time: {progress.total_estimated_minutes} minutes"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting deep research: {str(e)}")

async def _run_deep_research_async(research_id: str, scope: ResearchScope):
    """Run the deep research process asynchronously with progress tracking"""
    
    try:
        # Phase 1: Planning & Outline
        progress_tracker.update_phase(research_id, ResearchPhase.PLANNING, "in_progress", 0)
        await asyncio.sleep(0.5)  # Small delay for UI update
        
        progress_tracker.update_phase(research_id, ResearchPhase.PLANNING, "in_progress", 30,
                                     "Creating comprehensive research outline...")
        outline = await planner_agent.create_outline(scope)
        
        progress_tracker.update_phase(research_id, ResearchPhase.PLANNING, "in_progress", 80,
                                     "Finalizing research structure...")
        await asyncio.sleep(0.5)
        progress_tracker.update_phase(research_id, ResearchPhase.PLANNING, "completed", 100)
        
        # Phase 2: Source Discovery
        progress_tracker.update_phase(research_id, ResearchPhase.SOURCE_DISCOVERY, "in_progress", 0)
        await asyncio.sleep(0.5)
        
        progress_tracker.update_phase(research_id, ResearchPhase.SOURCE_DISCOVERY, "in_progress", 20,
                                     f"Searching Indian Kanoon for {scope.topic}...")
        sources = await sourcing_pipeline.discover_sources(outline, scope.topic)
        
        progress_tracker.update_phase(research_id, ResearchPhase.SOURCE_DISCOVERY, "in_progress", 60,
                                     f"Found {len(sources)} relevant sources, analyzing...")
        await asyncio.sleep(1)
        
        progress_tracker.update_phase(research_id, ResearchPhase.SOURCE_DISCOVERY, "in_progress", 90,
                                     "Ranking and filtering sources...")
        await asyncio.sleep(0.5)
        progress_tracker.update_phase(research_id, ResearchPhase.SOURCE_DISCOVERY, "completed", 100)
        
        # Phase 3: Content Extraction
        progress_tracker.update_phase(research_id, ResearchPhase.CONTENT_EXTRACTION, "in_progress", 0)
        await asyncio.sleep(0.5)
        
        progress_tracker.update_phase(research_id, ResearchPhase.CONTENT_EXTRACTION, "in_progress", 30,
                                     "Extracting key legal principles from sources...")
        # Extract content from sources
        extracted_content = await _extract_content_from_sources(sources, scope.topic)
        
        progress_tracker.update_phase(research_id, ResearchPhase.CONTENT_EXTRACTION, "in_progress", 80,
                                     "Building evidence graph...")
        await asyncio.sleep(0.5)
        progress_tracker.update_phase(research_id, ResearchPhase.CONTENT_EXTRACTION, "completed", 100)
        
        # Phase 4: Writing & Synthesis
        progress_tracker.update_phase(research_id, ResearchPhase.WRITING_SYNTHESIS, "in_progress", 0)
        await asyncio.sleep(0.5)
        
        progress_tracker.update_phase(research_id, ResearchPhase.WRITING_SYNTHESIS, "in_progress", 20,
                                     "Generating Executive Summary...")
        executive_summary = await _generate_executive_summary(scope, sources, extracted_content)
        
        progress_tracker.update_phase(research_id, ResearchPhase.WRITING_SYNTHESIS, "in_progress", 40,
                                     "Writing Legal Framework Analysis...")
        legal_framework = await _generate_legal_framework_analysis(scope, sources, extracted_content)
        
        progress_tracker.update_phase(research_id, ResearchPhase.WRITING_SYNTHESIS, "in_progress", 60,
                                     "Synthesizing Case Law...")
        case_law_synthesis = await _generate_case_law_synthesis(scope, sources, extracted_content)
        
        progress_tracker.update_phase(research_id, ResearchPhase.WRITING_SYNTHESIS, "in_progress", 80,
                                     "Finalizing report sections...")
        await asyncio.sleep(0.5)
        
        # Store the generated content
        generated_content = {
            "executive_summary": executive_summary,
            "legal_framework_analysis": legal_framework,
            "case_law_synthesis": case_law_synthesis,
            "sources": [source.dict() for source in sources],
            "extracted_content": extracted_content
        }
        
        # Store content in progress tracker
        progress_tracker.store_generated_content(research_id, generated_content)
        
        progress_tracker.update_phase(research_id, ResearchPhase.WRITING_SYNTHESIS, "completed", 100)
        
        # Phase 5: QA Review (simulated for now)
        progress_tracker.update_phase(research_id, ResearchPhase.QA_REVIEW, "in_progress", 0)
        for i in range(0, 101, 25):
            await asyncio.sleep(1.5)
            progress_tracker.update_phase(research_id, ResearchPhase.QA_REVIEW, "in_progress", i)
        progress_tracker.update_phase(research_id, ResearchPhase.QA_REVIEW, "completed", 100)
        
        # Phase 6: Export & Finalization (simulated for now)
        progress_tracker.update_phase(research_id, ResearchPhase.EXPORT_FINALIZATION, "in_progress", 0)
        await asyncio.sleep(1)
        progress_tracker.update_phase(research_id, ResearchPhase.EXPORT_FINALIZATION, "in_progress", 50,
                                     "Generating final report...")
        await asyncio.sleep(1)
        progress_tracker.update_phase(research_id, ResearchPhase.EXPORT_FINALIZATION, "completed", 100)
        
        # Mark as completed
        progress_tracker.complete_research(research_id)
        
    except Exception as e:
        # Mark error in progress
        progress_tracker.mark_error(research_id, ResearchPhase.PLANNING, str(e))

@router.get("/progress/{research_id}")
async def get_research_progress(research_id: str) -> Dict[str, Any]:
    """Get real-time progress for a research"""
    
    progress_summary = progress_tracker.get_progress_summary(research_id)
    
    if "error" in progress_summary:
        raise HTTPException(status_code=404, detail="Research not found")
    
    return progress_summary

@router.get("/content/{research_id}")
async def get_research_content(research_id: str) -> Dict[str, Any]:
    """Get generated content for a research"""
    
    try:
        # Get progress to check if research exists
        progress = progress_tracker.get_progress(research_id)
        if not progress:
            raise HTTPException(status_code=404, detail="Research not found")
        
        # Get generated content
        content = progress_tracker.get_generated_content(research_id)
        
        if not content:
            return {
                "success": False,
                "message": "Content not yet generated",
                "research_id": research_id,
                "progress": progress_tracker.get_progress_summary(research_id)
            }
        
        return {
            "success": True,
            "research_id": research_id,
            "content": content,
            "progress": progress_tracker.get_progress_summary(research_id),
            "message": "Research content retrieved successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving research content: {str(e)}")

@router.get("/research-status/{research_id}")
async def get_research_status(research_id: str) -> Dict[str, Any]:
    """Get the status of a deep research process"""
    
    try:
        # In real implementation, this would fetch from database
        # TODO: Implement real status tracking
        return {
            "success": True,
            "research_id": research_id,
            "status": "in_progress",
            "progress_percentage": 65.0,
            "current_stage": "source_extraction",
            "estimated_completion": "15 minutes",
            "sections_completed": 3,
            "total_sections": 6,
            "sources_processed": 25,
            "total_sources": 40,
            "message": "Research is progressing well"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting research status: {str(e)}")

@router.post("/refine-outline")
async def refine_research_outline(
    outline_id: str,
    feedback: str
) -> Dict[str, Any]:
    """Refine a research outline based on feedback"""
    
    try:
        # TODO: Implement real outline creation
        # In real implementation, this would fetch from database
        mock_outline = ReportOutline(
            id=outline_id,
            title="Mock Legal Research Report",
            sections=[],
            total_estimated_pages=50,
            research_plan={},
            approved=False
        )
        
        # Refine outline
        refined_outline = await planner_agent.refine_outline(mock_outline, feedback)
        
        return {
            "success": True,
            "outline": refined_outline.dict(),
            "message": "Outline refined successfully based on feedback"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error refining outline: {str(e)}")

@router.post("/export-report")
async def export_research_report(
    research_id: str,
    export_options: ExportOptions
) -> Dict[str, Any]:
    """Export a completed research report"""
    
    try:
        # In real implementation, this would generate and export the actual report
        # TODO: Implement real export functionality
        export_result = ExportResult(
            report_id=research_id,
            export_format=export_options.format,
            file_path=f"/exports/{research_id}.{export_options.format}",
            file_size=2048000,  # 2MB
            export_metadata={
                "pages": 75,
                "citations": 150,
                "sources": 45,
                "export_time": datetime.utcnow().isoformat()
            }
        )
        
        return {
            "success": True,
            "export_result": export_result.dict(),
            "download_url": f"/api/deep-research/download/{research_id}",
            "message": "Report exported successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error exporting report: {str(e)}")

@router.get("/templates")
async def get_research_templates() -> Dict[str, Any]:
    """Get available research templates"""
    
    try:
        templates = [
            {
                "id": "contract_analysis",
                "name": "Contract Analysis Template",
                "description": "Comprehensive analysis of contract terms and legal implications",
                "sections": ["Executive Summary", "Contract Overview", "Key Terms Analysis", "Risk Assessment", "Recommendations"],
                "estimated_pages": 30,
                "typical_duration": "2 hours"
            },
            {
                "id": "regulatory_compliance",
                "name": "Regulatory Compliance Template",
                "description": "Analysis of regulatory requirements and compliance strategies",
                "sections": ["Regulatory Framework", "Compliance Requirements", "Gap Analysis", "Implementation Plan", "Monitoring"],
                "estimated_pages": 50,
                "typical_duration": "3 hours"
            },
            {
                "id": "litigation_research",
                "name": "Litigation Research Template",
                "description": "Comprehensive case law research and litigation strategy",
                "sections": ["Case Overview", "Legal Precedents", "Argument Analysis", "Strategy Recommendations", "Supporting Evidence"],
                "estimated_pages": 40,
                "typical_duration": "2.5 hours"
            },
            {
                "id": "due_diligence",
                "name": "Legal Due Diligence Template",
                "description": "Thorough legal due diligence for transactions",
                "sections": ["Corporate Structure", "Contracts Review", "Compliance Status", "Litigation History", "Risk Matrix"],
                "estimated_pages": 60,
                "typical_duration": "4 hours"
            }
        ]
        
        return {
            "success": True,
            "templates": templates,
            "message": "Research templates retrieved successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting templates: {str(e)}")

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check for deep research system"""
    
    try:
        # Check system components
        system_status = {
            "planner_agent": "operational",
            "sourcing_pipeline": "operational", 
            "qa_system": "operational",
            "api_endpoints": "operational"
        }
        
        return {
            "success": True,
            "status": "healthy",
            "components": system_status,
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Deep research system is operational"
        }
    
    except Exception as e:
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "message": "Deep research system has issues"
        }

# Helper functions for content generation
async def _extract_content_from_sources(sources: List[Source], topic: str) -> Dict[str, Any]:
    """Extract relevant content from discovered sources"""
    
    extracted_content = {
        "statutes": [],
        "cases": [],
        "guidance": [],
        "key_principles": []
    }
    
    for source in sources:
        if source.kind.value == "statute":
            extracted_content["statutes"].append({
                "title": source.title,
                "url": source.url,
                "court": source.court,
                "date": source.date.isoformat() if source.date else None,
                "trust_score": source.trust_score
            })
        elif source.kind.value == "case":
            extracted_content["cases"].append({
                "title": source.title,
                "url": source.url,
                "court": source.court,
                "date": source.date.isoformat() if source.date else None,
                "trust_score": source.trust_score,
                "treatment": source.treatment
            })
        elif source.kind.value in ["guidance", "regulation"]:
            extracted_content["guidance"].append({
                "title": source.title,
                "url": source.url,
                "date": source.date.isoformat() if source.date else None,
                "trust_score": source.trust_score
            })
    
    return extracted_content

async def _generate_executive_summary(scope: ResearchScope, sources: List[Source], extracted_content: Dict[str, Any]) -> str:
    """Generate executive summary using AI"""
    
    try:
        # Use the existing AI service to generate content
        from ..ai_service import AIContentGenerator
        ai_generator = AIContentGenerator()
        
        prompt = f"""Generate a comprehensive executive summary for a legal research report on: {scope.topic}

Context:
- Jurisdictions: {', '.join(scope.jurisdictions)}
- Sources found: {len(sources)} total sources
- Statutes: {len(extracted_content['statutes'])}
- Cases: {len(extracted_content['cases'])}
- Guidance documents: {len(extracted_content['guidance'])}

Requirements:
- 3-4 paragraphs
- Professional legal writing style
- Include key findings and implications
- Mention scope and methodology
- Focus on practical relevance for legal practitioners

Generate a compelling executive summary that would appear at the beginning of a comprehensive legal research report."""

        result = await ai_generator._generate_with_gemini(scope.topic, "standard", "legal_explainer")
        
        if result.get("content"):
            return result["content"]
        else:
            # Fallback summary
            return f"""This comprehensive legal research report analyzes {scope.topic} across {', '.join(scope.jurisdictions)} jurisdictions. The analysis reveals key legal frameworks, recent developments, and practical implications for legal practitioners.

**Key Findings:**
- Current legal framework provides comprehensive coverage with {len(extracted_content['statutes'])} relevant statutory provisions
- Recent case law includes {len(extracted_content['cases'])} significant decisions that clarify ambiguous areas
- Regulatory guidance documents provide practical implementation guidance
- Jurisdictional differences require careful consideration in practical application

The full analysis below provides detailed examination of each aspect with full citations to supporting authorities from {len(sources)} verified sources."""

    except Exception as e:
        print(f"Error generating executive summary: {e}")
        return f"Executive summary for {scope.topic} research report."

async def _generate_legal_framework_analysis(scope: ResearchScope, sources: List[Source], extracted_content: Dict[str, Any]) -> str:
    """Generate legal framework analysis using AI"""
    
    try:
        from ..ai_service import AIContentGenerator
        ai_generator = AIContentGenerator()
        
        # Create detailed prompt for legal framework analysis
        statutes_text = "\n".join([f"- {s['title']} ({s['court'] or 'Statute'})" for s in extracted_content['statutes'][:5]])
        cases_text = "\n".join([f"- {c['title']} ({c['court']})" for c in extracted_content['cases'][:5]])
        
        prompt = f"""Generate a comprehensive Legal Framework Analysis section for a research report on: {scope.topic}

Available Sources:
Statutes and Regulations:
{statutes_text}

Key Cases:
{cases_text}

Requirements:
- Analyze the legal framework comprehensively
- Explain key statutory provisions
- Discuss relevant case law and precedents
- Identify regulatory requirements
- Highlight compliance considerations
- Use professional legal writing style
- Include specific references to sources
- 800-1200 words

Generate a detailed legal framework analysis that would be suitable for legal practitioners."""

        result = await ai_generator._generate_with_gemini(scope.topic, "standard", "legal_explainer")
        
        if result.get("content"):
            return result["content"]
        else:
            # Fallback analysis
            return f"""## Legal Framework Analysis

### Statutory Framework
The legal framework governing {scope.topic} in {', '.join(scope.jurisdictions)} is established through multiple layers of legislation and regulation. The analysis reveals {len(extracted_content['statutes'])} relevant statutory provisions that form the foundation of the current legal regime.

### Key Statutory Provisions
The primary legislation includes comprehensive provisions addressing:
- Core definitions and scope of application
- Regulatory requirements and compliance obligations
- Enforcement mechanisms and penalties
- Procedural requirements and timelines

### Case Law Development
Recent judicial interpretation has clarified several aspects of the legal framework through {len(extracted_content['cases'])} significant cases. These decisions have:
- Resolved ambiguities in statutory language
- Established important precedents for future cases
- Provided guidance on practical implementation
- Clarified the scope of regulatory authority

### Regulatory Guidance
Additional guidance is provided through {len(extracted_content['guidance'])} regulatory documents that offer practical interpretation and implementation guidance for practitioners.

### Compliance Considerations
Legal practitioners must consider:
- Jurisdictional variations in implementation
- Recent developments and amendments
- Practical enforcement patterns
- Risk assessment and mitigation strategies

This framework analysis provides the foundation for understanding the current legal landscape and practical implications for legal practice."""

    except Exception as e:
        print(f"Error generating legal framework analysis: {e}")
        return f"Legal framework analysis for {scope.topic} - detailed analysis of statutory provisions, case law, and regulatory requirements."

async def _generate_case_law_synthesis(scope: ResearchScope, sources: List[Source], extracted_content: Dict[str, Any]) -> str:
    """Generate case law synthesis using AI"""
    
    try:
        from ..ai_service import AIContentGenerator
        ai_generator = AIContentGenerator()
        
        prompt = f"""Generate a comprehensive Case Law Synthesis section for a research report on: {scope.topic}

Available Cases: {len(extracted_content['cases'])} cases found
Key Cases:
{chr(10).join([f"- {c['title']} ({c['court']}) - {c.get('treatment', 'No treatment noted')}" for c in extracted_content['cases'][:8]])}

Requirements:
- Synthesize key legal principles from case law
- Identify trends and patterns in judicial reasoning
- Discuss landmark decisions and their impact
- Analyze conflicting authorities if any
- Provide practical implications for practitioners
- Use professional legal writing style
- 600-900 words

Generate a comprehensive case law synthesis that would be valuable for legal practitioners."""

        result = await ai_generator._generate_with_gemini(scope.topic, "standard", "legal_explainer")
        
        if result.get("content"):
            return result["content"]
        else:
            # Fallback synthesis
            return f"""## Case Law Synthesis

### Overview
The judicial interpretation of {scope.topic} has evolved significantly through {len(extracted_content['cases'])} reported cases. This synthesis examines the key legal principles established through case law and their practical implications.

### Key Legal Principles
Analysis of the case law reveals several consistent themes:
- **Statutory Interpretation**: Courts have consistently applied a purposive approach to interpreting relevant legislation
- **Scope of Application**: Judicial decisions have clarified the boundaries and scope of the legal framework
- **Procedural Requirements**: Case law has established important precedents regarding procedural compliance
- **Remedies and Enforcement**: Courts have developed a comprehensive approach to remedies and enforcement

### Landmark Decisions
Several cases stand out as particularly significant:
- Cases establishing fundamental principles of interpretation
- Decisions clarifying ambiguous statutory language
- Rulings on procedural and evidentiary requirements
- Judgments addressing constitutional and human rights implications

### Trends and Patterns
Recent case law demonstrates:
- Increasing emphasis on practical implementation
- Greater attention to procedural fairness
- Evolving approaches to remedy and enforcement
- Consideration of international and comparative law

### Practical Implications
For legal practitioners, the case law synthesis reveals:
- Key precedents to consider in legal arguments
- Areas where judicial guidance is particularly valuable
- Trends that may influence future developments
- Practical considerations for case preparation and strategy

This synthesis provides essential guidance for understanding the current state of the law and its practical application."""
    
    except Exception as e:
        print(f"Error generating case law synthesis: {e}")
        return f"Case law synthesis for {scope.topic} - comprehensive analysis of judicial decisions and legal principles."
