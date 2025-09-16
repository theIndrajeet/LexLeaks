"""
Event-Driven Research API Endpoints
Orchestrator → Event Bus → Composable Services → Tooling Plane
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any
import asyncio
from ..event_driven_agent_system import event_driven_system
from ..deep_research_models import DeepResearchRequest

router = APIRouter(prefix="/api/event-driven-research", tags=["Event-Driven Research"])

@router.post("/start-research")
async def start_event_driven_research(request: DeepResearchRequest):
    """
    Start event-driven research with orchestrator → event bus → agents
    """
    try:
        run_id = await event_driven_system.start_research(
            topic=request.topic,
            jurisdictions=request.jurisdictions,
            depth_level=request.depth_level,
            audience=request.audience,
            focus_areas=request.focus_areas or []
        )
        
        return {
            "success": True,
            "run_id": run_id,
            "message": "Event-driven research started successfully",
            "architecture": "Orchestrator → Event Bus → Composable Services → Tooling Plane",
            "estimated_output": "50,000 words with integrity",
            "estimated_time": "30 minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting research: {str(e)}")

@router.get("/status/{run_id}")
async def get_research_status(run_id: str):
    """Get current status of event-driven research"""
    try:
        status = await event_driven_system.get_run_status(run_id)
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check for event-driven system"""
    try:
        return {
            "status": "healthy",
            "architecture": "Event-Driven Multi-Agent System",
            "components": [
                "Orchestrator",
                "Event Bus",
                "Planner Agent",
                "Retriever Agent", 
                "Writer Agent",
                "Quality Controller",
                "Compiler/Exporter"
            ],
            "active_runs": len(event_driven_system.active_runs),
            "message": "Event-driven system is operational"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.get("/runs")
async def get_all_runs():
    """Get all research runs"""
    try:
        runs = []
        for run_id, run_info in event_driven_system.active_runs.items():
            runs.append({
                "run_id": run_id,
                "status": run_info["status"],
                "topic": run_info["topic"],
                "started_at": run_info["started_at"].isoformat()
            })
        
        return {
            "total_runs": len(runs),
            "runs": runs
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting runs: {str(e)}")

@router.post("/stop/{run_id}")
async def stop_research(run_id: str):
    """Stop a research run"""
    try:
        if run_id in event_driven_system.active_runs:
            event_driven_system.active_runs[run_id]["status"] = "stopped"
            
            return {
                "success": True,
                "message": f"Research run {run_id} stopped successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Research run not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping research: {str(e)}")

@router.get("/results/{run_id}")
async def get_research_results(run_id: str):
    """Get completed research results"""
    try:
        # Get results from the system
        results = await event_driven_system.get_research_results(run_id)
        
        if "error" in results:
            return {
                "success": False,
                "run_id": run_id,
                "status": "processing",
                "message": "Research is still in progress. Please check status endpoint."
            }
        
        return {
            "success": True,
            "run_id": run_id,
            "status": "completed",
            "results": results,
            "message": "Research results retrieved successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting results: {str(e)}")

@router.get("/system-info")
async def get_system_info():
    """Get detailed system information"""
    try:
        return {
            "system_type": "Event-Driven Multi-Agent Research System",
            "architecture": {
                "orchestrator": "Creates run_id, plan, schedule",
                "event_bus": "Typed messages, backpressure",
                "agents": "Composable services",
                "tooling_plane": "Cite Extractor, Quote Verifier, Bluebook, Diff"
            },
            "model_plane": {
                "fast": "gemini-1.5-flash (Planning)",
                "standard": "gemini-1.5-pro (Writing)",
                "premium": "gemini-1.5-pro (QC)"
            },
            "connectors": [
                "Indian Kanoon",
                "Government Portals",
                "Case Law Databases"
            ],
            "export_formats": ["Markdown", "DOCX", "PDF"],
            "quality_gates": [
                "Citation Coverage",
                "Bluebook Compliance", 
                "Quote Fidelity",
                "Word Count",
                "Content Quality"
            ],
            "features": [
                "50,000 words with integrity",
                "No fluff, proper citations",
                "Quality control at every step",
                "Event-driven architecture",
                "Composable services",
                "Real-time monitoring"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting system info: {str(e)}")
