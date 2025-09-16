from typing import Dict, List, Optional, Literal, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

# Enums for type safety
class SourceKind(str, Enum):
    STATUTE = "statute"
    CASE = "case"
    ORDER = "order"
    GUIDANCE = "guidance"
    NEWS = "news"
    PAPER = "paper"
    REGULATION = "regulation"

class ClaimImportance(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

class ClaimStatus(str, Enum):
    DRAFT = "draft"
    VERIFIED = "verified"
    CONTRADICTED = "contradicted"

class SectionStatus(str, Enum):
    PLANNED = "planned"
    RESEARCHING = "researching"
    DRAFTING = "drafting"
    REVIEWING = "reviewing"
    COMPLETED = "completed"

class AgentType(str, Enum):
    PLANNER = "planner"
    SOURCER = "sourcer"
    EXTRACTOR = "extractor"
    WRITER = "writer"
    CRITIC = "critic"
    QA = "qa"
    COMPILER = "compiler"

# Core Data Models
class Source(BaseModel):
    id: str
    url: str
    title: str
    kind: SourceKind
    jurisdiction: Optional[str] = None
    court: Optional[str] = None
    date: Optional[datetime] = None
    snapshot_path: Optional[str] = None
    trust_score: float = 0.0
    treatment: Optional[str] = None  # "overruled", "distinguished", "followed"
    author: Optional[str] = None
    domain: Optional[str] = None
    word_count: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Extract(BaseModel):
    id: str
    source_id: str
    section: Optional[str] = None
    lines: Optional[str] = None
    quote: Optional[str] = None
    fact: str
    tags: List[str] = []
    confidence: float = 0.0
    line_ranges: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Claim(BaseModel):
    id: str
    text: str
    importance: ClaimImportance
    supports: List[str] = []  # Extract IDs
    contradicts: List[str] = []  # Extract IDs
    status: ClaimStatus = ClaimStatus.DRAFT
    confidence: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Section(BaseModel):
    id: str
    title: str
    outline_path: str  # e.g., "1.2.3"
    claims: List[str] = []  # Claim IDs
    draft_md: str = ""
    status: SectionStatus = SectionStatus.PLANNED
    word_count: int = 0
    citation_count: int = 0
    primary_sources: int = 0
    secondary_sources: int = 0
    estimated_pages: float = 0.0

class ResearchScope(BaseModel):
    topic: str
    jurisdictions: List[str] = ["India"]
    time_window: Optional[str] = None  # e.g., "2020-present"
    audience: str = "legal_professional"
    output_format: str = "comprehensive_report"
    focus_areas: List[str] = []
    depth_level: Literal["quick", "comprehensive", "deep_dive"] = "comprehensive"

class ReportOutline(BaseModel):
    id: str
    title: str
    sections: List[Section] = []
    total_estimated_pages: int = 0
    research_plan: Dict[str, Any] = {}
    approved: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class EvidenceGraph(BaseModel):
    claims: Dict[str, Claim] = {}
    extracts: Dict[str, Extract] = {}
    sources: Dict[str, Source] = {}
    contradictions: List[Dict[str, str]] = []  # [claim_id, contradicting_claim_id]
    support_networks: Dict[str, List[str]] = {}  # claim_id -> supporting_claim_ids

class QAMetrics(BaseModel):
    pin_density: float = 0.0  # citations per 100 words
    primary_source_ratio: float = 0.0
    stale_citation_ratio: float = 0.0
    contradiction_count: int = 0
    uncovered_sections: List[str] = []
    coverage_score: float = 0.0
    trust_score: float = 0.0

class DeepResearchReport(BaseModel):
    id: str
    scope: ResearchScope
    outline: ReportOutline
    evidence_graph: EvidenceGraph
    qa_metrics: QAMetrics
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "planning"
    progress_percentage: float = 0.0
    estimated_completion: Optional[datetime] = None

# Agent Communication Models
class AgentTask(BaseModel):
    id: str
    agent_type: AgentType
    task_data: Dict[str, Any]
    priority: int = 1
    dependencies: List[str] = []
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)

class AgentResult(BaseModel):
    task_id: str
    agent_type: AgentType
    success: bool
    result_data: Dict[str, Any]
    error_message: Optional[str] = None
    execution_time: float = 0.0
    completed_at: datetime = Field(default_factory=datetime.utcnow)

# Export Models
class ExportOptions(BaseModel):
    format: Literal["docx", "pdf", "html", "markdown"] = "docx"
    include_appendix: bool = True
    include_table_of_authorities: bool = True
    include_research_pack: bool = True
    citation_style: str = "bluebook"
    page_numbers: bool = True
    cross_references: bool = True

class ExportResult(BaseModel):
    report_id: str
    export_format: str
    file_path: str
    file_size: int
    export_metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)

# Progress Tracking Models
class ResearchPhase(str, Enum):
    PLANNING = "planning"
    SOURCE_DISCOVERY = "source_discovery"
    CONTENT_EXTRACTION = "content_extraction"
    WRITING_SYNTHESIS = "writing_synthesis"
    QA_REVIEW = "qa_review"
    EXPORT_FINALIZATION = "export_finalization"
    COMPLETED = "completed"

class PhaseProgress(BaseModel):
    phase: ResearchPhase
    phase_name: str
    status: Literal["pending", "in_progress", "completed", "failed"] = "pending"
    progress_percentage: float = 0.0
    estimated_minutes: int
    actual_minutes: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
class ResearchProgress(BaseModel):
    research_id: str
    total_estimated_minutes: int
    elapsed_minutes: float = 0.0
    remaining_minutes: float = 0.0
    overall_progress_percentage: float = 0.0
    current_phase: ResearchPhase
    current_phase_name: str
    current_activity: str = "Initializing..."
    phases: List[PhaseProgress]
    started_at: datetime = Field(default_factory=datetime.utcnow)
    estimated_completion: datetime
    actual_completion: Optional[datetime] = None
    is_completed: bool = False
    has_errors: bool = False

# Request model for deep research
class DeepResearchRequest(BaseModel):
    topic: str = Field(..., description="The research topic")
    jurisdictions: List[str] = Field(default_factory=list, description="List of jurisdictions to research")
    depth_level: Literal["quick", "comprehensive", "exhaustive"] = Field(default="comprehensive", description="Depth of research")
    audience: Literal["legal_professional", "student", "general"] = Field(default="legal_professional", description="Target audience")
    focus_areas: Optional[List[str]] = Field(default=None, description="Specific areas to focus on")
    timeline: Optional[str] = Field(default=None, description="Timeline for research")
    output_format: Optional[str] = Field(default=None, description="Desired output format")
    additional_requirements: Optional[str] = Field(default=None, description="Additional requirements")
    word_count: Optional[int] = Field(default=50000, description="Target word count for research")
    num_agents: Optional[int] = Field(default=20, description="Number of agents to use")
    words_per_agent: Optional[int] = Field(default=2500, description="Words per agent")
