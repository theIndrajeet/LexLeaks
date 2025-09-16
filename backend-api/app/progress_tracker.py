"""
Progress Tracker for Deep Research System
Tracks progress, estimates time, and provides real-time updates
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import asyncio
from collections import defaultdict

from .deep_research_models import (
    ResearchPhase, PhaseProgress, ResearchProgress
)

class ProgressTracker:
    """Tracks research progress and provides time estimates"""
    
    def __init__(self):
        # Store progress for each research ID
        self.research_progress: Dict[str, ResearchProgress] = {}
        # Store generated content for each research ID
        self.generated_content: Dict[str, Dict[str, Any]] = {}
        
        # Phase time estimates (in minutes)
        self.phase_estimates = {
            ResearchPhase.PLANNING: {"min": 2, "max": 5, "typical": 3},
            ResearchPhase.SOURCE_DISCOVERY: {"min": 10, "max": 25, "typical": 15},
            ResearchPhase.CONTENT_EXTRACTION: {"min": 10, "max": 20, "typical": 15},
            ResearchPhase.WRITING_SYNTHESIS: {"min": 15, "max": 30, "typical": 20},
            ResearchPhase.QA_REVIEW: {"min": 5, "max": 15, "typical": 10},
            ResearchPhase.EXPORT_FINALIZATION: {"min": 2, "max": 5, "typical": 3}
        }
        
        # Activity messages for user display
        self.activity_messages = {
            ResearchPhase.PLANNING: [
                "Creating research outline...",
                "Analyzing topic requirements...",
                "Generating section structure...",
                "Planning research strategy..."
            ],
            ResearchPhase.SOURCE_DISCOVERY: [
                "Searching Indian Kanoon database...",
                "Finding relevant case law...",
                "Discovering statutory provisions...",
                "Collecting legal precedents...",
                "Analyzing search results..."
            ],
            ResearchPhase.CONTENT_EXTRACTION: [
                "Extracting key legal principles...",
                "Analyzing case holdings...",
                "Processing statutory text...",
                "Identifying relevant citations...",
                "Building evidence graph..."
            ],
            ResearchPhase.WRITING_SYNTHESIS: [
                "Writing executive summary...",
                "Synthesizing legal framework...",
                "Analyzing case law patterns...",
                "Drafting risk assessment...",
                "Creating comprehensive analysis..."
            ],
            ResearchPhase.QA_REVIEW: [
                "Verifying citations...",
                "Checking Bluebook format...",
                "Validating legal reasoning...",
                "Ensuring consistency...",
                "Final quality checks..."
            ],
            ResearchPhase.EXPORT_FINALIZATION: [
                "Formatting document...",
                "Creating table of authorities...",
                "Generating appendices...",
                "Finalizing report..."
            ]
        }
        
        # Track activity message index for rotation
        self.activity_index = defaultdict(int)
    
    def initialize_research(self, research_id: str, topic: str, depth_level: str = "comprehensive") -> ResearchProgress:
        """Initialize progress tracking for a new research"""
        
        # Calculate time estimates based on depth level
        time_multiplier = 1.0
        if depth_level == "comprehensive":
            time_multiplier = 1.2
        elif depth_level == "quick":
            time_multiplier = 0.7
        
        # Create phase progress objects
        phases = []
        total_estimated = 0
        
        for phase in [ResearchPhase.PLANNING, ResearchPhase.SOURCE_DISCOVERY, 
                     ResearchPhase.CONTENT_EXTRACTION, ResearchPhase.WRITING_SYNTHESIS,
                     ResearchPhase.QA_REVIEW, ResearchPhase.EXPORT_FINALIZATION]:
            
            estimated_time = int(self.phase_estimates[phase]["typical"] * time_multiplier)
            total_estimated += estimated_time
            
            phase_name = self._get_phase_display_name(phase)
            phases.append(PhaseProgress(
                phase=phase,
                phase_name=phase_name,
                estimated_minutes=estimated_time
            ))
        
        # Create research progress object
        now = datetime.utcnow()
        progress = ResearchProgress(
            research_id=research_id,
            total_estimated_minutes=total_estimated,
            remaining_minutes=float(total_estimated),
            current_phase=ResearchPhase.PLANNING,
            current_phase_name=self._get_phase_display_name(ResearchPhase.PLANNING),
            current_activity="Initializing research for: " + topic[:50] + "...",
            phases=phases,
            started_at=now,
            estimated_completion=now + timedelta(minutes=total_estimated)
        )
        
        self.research_progress[research_id] = progress
        return progress
    
    def update_phase(self, research_id: str, phase: ResearchPhase, 
                    status: str = "in_progress", progress_percentage: float = 0.0,
                    activity: Optional[str] = None) -> Optional[ResearchProgress]:
        """Update the current phase and progress"""
        
        if research_id not in self.research_progress:
            return None
        
        progress = self.research_progress[research_id]
        now = datetime.utcnow()
        
        # Update current phase info
        progress.current_phase = phase
        progress.current_phase_name = self._get_phase_display_name(phase)
        
        # Update activity message
        if activity:
            progress.current_activity = activity
        else:
            progress.current_activity = self._get_next_activity_message(research_id, phase)
        
        # Update phase status
        for phase_progress in progress.phases:
            if phase_progress.phase == phase:
                phase_progress.status = status
                phase_progress.progress_percentage = progress_percentage
                
                if status == "in_progress" and not phase_progress.started_at:
                    phase_progress.started_at = now
                elif status == "completed":
                    phase_progress.completed_at = now
                    phase_progress.progress_percentage = 100.0
                    if phase_progress.started_at:
                        phase_progress.actual_minutes = (now - phase_progress.started_at).total_seconds() / 60
        
        # Calculate overall progress
        total_weight = sum(p.estimated_minutes for p in progress.phases)
        completed_weight = sum(
            p.estimated_minutes * (p.progress_percentage / 100.0)
            for p in progress.phases
        )
        progress.overall_progress_percentage = (completed_weight / total_weight * 100) if total_weight > 0 else 0
        
        # Update time estimates
        progress.elapsed_minutes = (now - progress.started_at).total_seconds() / 60
        
        # Recalculate remaining time based on actual vs estimated pace
        remaining_phases = [p for p in progress.phases if p.status != "completed"]
        if remaining_phases:
            # Adjust estimates based on actual performance
            pace_factor = 1.0
            completed_phases = [p for p in progress.phases if p.status == "completed" and p.actual_minutes]
            if completed_phases:
                actual_total = sum(p.actual_minutes for p in completed_phases if p.actual_minutes)
                estimated_total = sum(p.estimated_minutes for p in completed_phases)
                if estimated_total > 0:
                    pace_factor = actual_total / estimated_total
            
            remaining_estimate = sum(p.estimated_minutes * pace_factor for p in remaining_phases)
            current_phase_remaining = 0
            for p in progress.phases:
                if p.phase == phase and p.status == "in_progress":
                    current_phase_remaining = p.estimated_minutes * pace_factor * (1 - progress_percentage / 100)
                    break
            
            progress.remaining_minutes = current_phase_remaining + sum(
                p.estimated_minutes * pace_factor 
                for p in remaining_phases 
                if p.phase != phase
            )
            progress.estimated_completion = now + timedelta(minutes=progress.remaining_minutes)
        else:
            progress.remaining_minutes = 0
            progress.estimated_completion = now
        
        return progress
    
    def complete_research(self, research_id: str) -> Optional[ResearchProgress]:
        """Mark research as completed"""
        
        if research_id not in self.research_progress:
            return None
        
        progress = self.research_progress[research_id]
        progress.is_completed = True
        progress.actual_completion = datetime.utcnow()
        progress.current_phase = ResearchPhase.COMPLETED
        progress.current_phase_name = "Completed"
        progress.current_activity = "Research completed successfully!"
        progress.overall_progress_percentage = 100.0
        progress.remaining_minutes = 0
        
        # Mark all phases as completed
        for phase in progress.phases:
            if phase.status != "completed":
                phase.status = "completed"
                phase.progress_percentage = 100.0
                if not phase.completed_at:
                    phase.completed_at = datetime.utcnow()
        
        return progress
    
    def mark_error(self, research_id: str, phase: ResearchPhase, error_message: str) -> Optional[ResearchProgress]:
        """Mark a phase as failed with error"""
        
        if research_id not in self.research_progress:
            return None
        
        progress = self.research_progress[research_id]
        progress.has_errors = True
        progress.current_activity = f"Error: {error_message}"
        
        for phase_progress in progress.phases:
            if phase_progress.phase == phase:
                phase_progress.status = "failed"
                phase_progress.error_message = error_message
                break
        
        return progress
    
    def get_progress(self, research_id: str) -> Optional[ResearchProgress]:
        """Get current progress for a research"""
        return self.research_progress.get(research_id)
    
    def get_progress_summary(self, research_id: str) -> Dict[str, Any]:
        """Get a simplified progress summary for frontend"""
        
        progress = self.get_progress(research_id)
        if not progress:
            return {"error": "Research not found"}
        
        return {
            "research_id": progress.research_id,
            "overall_progress": round(progress.overall_progress_percentage, 1),
            "current_phase": progress.current_phase_name,
            "current_activity": progress.current_activity,
            "elapsed_time": f"{int(progress.elapsed_minutes)}m {int((progress.elapsed_minutes % 1) * 60)}s",
            "remaining_time": f"{int(progress.remaining_minutes)}m {int((progress.remaining_minutes % 1) * 60)}s",
            "estimated_completion": progress.estimated_completion.isoformat(),
            "is_completed": progress.is_completed,
            "has_errors": progress.has_errors,
            "phases": [
                {
                    "name": phase.phase_name,
                    "status": phase.status,
                    "progress": round(phase.progress_percentage, 1)
                }
                for phase in progress.phases
            ]
        }
    
    def _get_phase_display_name(self, phase: ResearchPhase) -> str:
        """Get user-friendly phase name"""
        
        display_names = {
            ResearchPhase.PLANNING: "Planning & Outline",
            ResearchPhase.SOURCE_DISCOVERY: "Source Discovery",
            ResearchPhase.CONTENT_EXTRACTION: "Content Extraction",
            ResearchPhase.WRITING_SYNTHESIS: "Writing & Synthesis",
            ResearchPhase.QA_REVIEW: "QA & Review",
            ResearchPhase.EXPORT_FINALIZATION: "Export & Finalization",
            ResearchPhase.COMPLETED: "Completed"
        }
        return display_names.get(phase, phase.value)
    
    def _get_next_activity_message(self, research_id: str, phase: ResearchPhase) -> str:
        """Get rotating activity message for phase"""
        
        if phase not in self.activity_messages:
            return "Processing..."
        
        messages = self.activity_messages[phase]
        if not messages:
            return "Processing..."
        
        # Get current index for this research/phase combo
        key = f"{research_id}_{phase.value}"
        index = self.activity_index[key]
        
        # Get message and increment index
        message = messages[index % len(messages)]
        self.activity_index[key] = (index + 1) % len(messages)
        
        return message
    
    def store_generated_content(self, research_id: str, content: Dict[str, Any]) -> None:
        """Store generated content for a research"""
        self.generated_content[research_id] = content
    
    def get_generated_content(self, research_id: str) -> Optional[Dict[str, Any]]:
        """Get generated content for a research"""
        return self.generated_content.get(research_id)

# Global instance
progress_tracker = ProgressTracker()
