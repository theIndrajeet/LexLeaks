"""
Multi-Agent Research API Endpoints
25-Agent System for Comprehensive Legal Research
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, List, Any
import asyncio
from ..multi_agent_system import multi_agent_system
from ..deep_research_models import DeepResearchRequest, ResearchProgress

router = APIRouter(prefix="/api/multi-agent-research", tags=["Multi-Agent Research"])

@router.post("/start-research")
async def start_multi_agent_research(request: DeepResearchRequest):
    """
    Start comprehensive multi-agent research
    25 agents: 5 coordinators + 20 specialized writers
    Each writer produces 2500 words, total: 50,000 words
    """
    try:
        research_id = await multi_agent_system.start_research(
            topic=request.topic,
            jurisdictions=request.jurisdictions,
            depth_level=request.depth_level,
            audience=request.audience,
            focus_areas=request.focus_areas or [],
            word_count=getattr(request, 'word_count', 50000),
            num_agents=getattr(request, 'num_agents', 20),
            words_per_agent=getattr(request, 'words_per_agent', 2500)
        )
        
        return {
            "success": True,
            "research_id": research_id,
            "message": "Multi-agent research started successfully",
            "agents_count": 25,
            "estimated_output": "50,000 words",
            "estimated_time": "15-20 minutes"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting research: {str(e)}")

@router.get("/status/{research_id}")
async def get_research_status(research_id: str):
    """Get current status of multi-agent research"""
    try:
        status = multi_agent_system.get_research_status(research_id)
        return status
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")

@router.get("/output/{research_id}")
async def get_research_output(research_id: str):
    """Get completed research output"""
    try:
        output = multi_agent_system.get_research_output(research_id)
        return output
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting output: {str(e)}")

@router.get("/agents")
async def get_agents_info():
    """Get information about all 25 agents"""
    try:
        agents_info = []
        for agent in multi_agent_system.agents.values():
            agents_info.append({
                "id": agent.id,
                "name": agent.name,
                "role": agent.role.value,
                "type": agent.agent_type.value,
                "specialization": agent.specialization,
                "expertise_level": agent.expertise_level,
                "status": agent.status,
                "current_task": agent.current_task,
                "word_count": agent.word_count
            })
        
        return {
            "total_agents": len(agents_info),
            "coordinators": len([a for a in agents_info if a["type"] == "coordinator"]),
            "writers": len([a for a in agents_info if a["type"] == "writer"]),
            "agents": agents_info
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting agents info: {str(e)}")

@router.get("/tasks/{research_id}")
async def get_research_tasks(research_id: str):
    """Get all tasks for a research session"""
    try:
        tasks = []
        for task in multi_agent_system.tasks.values():
            if task.id.startswith(f"task_{research_id}_"):
                tasks.append({
                    "id": task.id,
                    "section_title": task.section_title,
                    "assigned_agent": task.assigned_agent_id,
                    "status": task.status,
                    "word_target": task.word_target,
                    "word_count": task.word_count,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat() if task.created_at else None,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None
                })
        
        return {
            "research_id": research_id,
            "total_tasks": len(tasks),
            "tasks": tasks
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting tasks: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check for multi-agent system"""
    try:
        active_agents = len([agent for agent in multi_agent_system.agents.values() 
                           if agent.status in ["working", "assigned"]])
        
        return {
            "status": "healthy",
            "total_agents": len(multi_agent_system.agents),
            "active_agents": active_agents,
            "research_sessions": len(multi_agent_system.research_sessions),
            "message": "Multi-agent system is operational"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.post("/stop/{research_id}")
async def stop_research(research_id: str):
    """Stop a research session"""
    try:
        if research_id in multi_agent_system.research_sessions:
            # Mark all agents as idle
            for agent in multi_agent_system.agents.values():
                if agent.current_task and agent.current_task.startswith(f"task_{research_id}_"):
                    agent.status = "idle"
                    agent.current_task = None
            
            # Mark session as stopped
            multi_agent_system.research_sessions[research_id]["status"] = "stopped"
            
            return {
                "success": True,
                "message": f"Research session {research_id} stopped successfully"
            }
        else:
            raise HTTPException(status_code=404, detail="Research session not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping research: {str(e)}")

@router.get("/sessions")
async def get_all_sessions():
    """Get all research sessions"""
    try:
        sessions = []
        for session_id, session_data in multi_agent_system.research_sessions.items():
            sessions.append({
                "id": session_id,
                "topic": session_data["topic"],
                "status": session_data["status"],
                "created_at": session_data["created_at"].isoformat(),
                "agents_assigned": len(session_data.get("agents_assigned", [])),
                "tasks_created": len(session_data.get("tasks_created", [])),
                "completed_sections": len(session_data.get("completed_sections", []))
            })
        
        return {
            "total_sessions": len(sessions),
            "sessions": sessions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting sessions: {str(e)}")
