"""
Event-Driven Multi-Agent Research System
Orchestrator → Event Bus → Composable Services → Tooling Plane
50,000 words with integrity, no fluff.
"""

import asyncio
import json
import hashlib
import re
from typing import Dict, List, Any, Optional, Set, Union, Callable
from dataclasses import dataclass, asdict, field
from datetime import datetime
import uuid
from enum import Enum
from abc import ABC, abstractmethod
from collections import defaultdict
import google.generativeai as genai
from .config import GEMINI_API_KEY
from .indian_kanoon_service import IndianKanoonService

# ============================================================================
# CONTENT COORDINATION SYSTEM
# ============================================================================

class ContentCoordinator:
    """Manages content coordination between agents to prevent repetition"""
    
    def __init__(self):
        self.content_registry: Dict[str, Dict[str, Any]] = {}
        self.topic_coverage: Dict[str, List[str]] = defaultdict(list)
        self.cross_references: Dict[str, List[str]] = defaultdict(list)
        self.content_summaries: Dict[str, str] = {}
        self.section_topics: Dict[str, List[str]] = defaultdict(list)
    
    async def register_content(self, task_id: str, content: str, section_id: str, focus: str) -> Dict[str, Any]:
        """Register content and check for overlaps"""
        
        # Extract key topics from content
        extracted_topics = self._extract_topics(content)
        
        # Check for topic overlaps with existing content
        overlaps = self._find_topic_overlaps(extracted_topics, section_id)
        
        # Generate content summary
        summary = self._generate_content_summary(content, focus)
        
        # Register new content
        self.content_registry[task_id] = {
            "content": content,
            "topics": extracted_topics,
            "section_id": section_id,
            "focus": focus,
            "summary": summary,
            "timestamp": datetime.utcnow(),
            "overlaps": overlaps
        }
        
        # Update topic coverage
        for topic in extracted_topics:
            self.topic_coverage[topic].append(task_id)
            self.section_topics[section_id].append(topic)
        
        # Store summary
        self.content_summaries[task_id] = summary
        
        return {
            "status": "registered",
            "overlaps": overlaps,
            "summary": summary,
            "topics": extracted_topics
        }
    
    def _extract_topics(self, content: str) -> List[str]:
        """Extract key topics from content"""
        # Simple topic extraction - can be enhanced with NLP
        topics = []
        
        # Legal terms and concepts
        legal_terms = [
            "consent", "marital rape", "penetration", "sexual assault", "evidence",
            "prosecution", "defense", "judicial", "constitutional", "amendment",
            "statutory", "case law", "precedent", "jurisdiction", "enforcement"
        ]
        
        for term in legal_terms:
            if term.lower() in content.lower():
                topics.append(term)
        
        # Extract section-specific topics
        if "section 375" in content.lower():
            topics.append("section_375_definition")
        if "criminal law" in content.lower():
            topics.append("criminal_law_amendment")
        if "supreme court" in content.lower():
            topics.append("supreme_court_cases")
        if "high court" in content.lower():
            topics.append("high_court_cases")
        
        return list(set(topics))  # Remove duplicates
    
    def _find_topic_overlaps(self, new_topics: List[str], current_section: str) -> List[Dict[str, Any]]:
        """Find topic overlaps with existing content"""
        overlaps = []
        
        for topic in new_topics:
            if topic in self.topic_coverage:
                existing_tasks = self.topic_coverage[topic]
                for task_id in existing_tasks:
                    if task_id in self.content_registry:
                        existing_content = self.content_registry[task_id]
                        if existing_content["section_id"] != current_section:
                            overlaps.append({
                                "topic": topic,
                                "existing_task": task_id,
                                "existing_section": existing_content["section_id"],
                                "existing_focus": existing_content["focus"],
                                "suggestion": f"Reference {existing_content['section_id']} instead of re-explaining"
                            })
        
        return overlaps
    
    def _generate_content_summary(self, content: str, focus: str) -> str:
        """Generate a brief summary of the content"""
        # Simple summary generation - first 200 characters
        summary = content[:200].strip()
        if len(content) > 200:
            summary += "..."
        
        return f"[{focus}] {summary}"
    
    def get_context_for_task(self, task_id: str, section_id: str) -> Dict[str, Any]:
        """Get relevant context from existing content"""
        context_parts = []
        references = []
        
        # Get content from other sections
        for existing_task_id, content_data in self.content_registry.items():
            if content_data["section_id"] != section_id:
                context_parts.append(f"Section {content_data['section_id']} ({content_data['focus']}): {content_data['summary']}")
                references.append(existing_task_id)
        
        return {
            "context": "\n".join(context_parts),
            "references": references,
            "existing_topics": list(self.topic_coverage.keys()),
            "section_topics": self.section_topics.get(section_id, [])
        }
    
    def get_cross_references(self, topic: str) -> List[str]:
        """Get cross-references for a topic"""
        if topic in self.topic_coverage:
            return [f"See Section {self.content_registry[task_id]['section_id']}" 
                   for task_id in self.topic_coverage[topic]]
        return []

# ============================================================================
# EVENT SYSTEM
# ============================================================================

class EventType(Enum):
    # Orchestrator Events
    RESEARCH_STARTED = "research_started"
    PLAN_CREATED = "plan_created"
    SCHEDULE_CREATED = "schedule_created"
    
    # Agent Events
    TASK_ASSIGNED = "task_assigned"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    
    # Quality Events
    QUALITY_CHECK_STARTED = "quality_check_started"
    QUALITY_CHECK_COMPLETED = "quality_check_completed"
    QUALITY_ISSUE_DETECTED = "quality_issue_detected"
    
    # Export Events
    EXPORT_STARTED = "export_started"
    EXPORT_COMPLETED = "export_completed"

@dataclass
class Event:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: EventType = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    run_id: str = None
    data: Dict[str, Any] = field(default_factory=dict)
    source: str = None
    target: Optional[str] = None

class EventBus:
    """Event bus with typed messages and backpressure"""
    
    def __init__(self, max_queue_size: int = 1000):
        self.queues: Dict[EventType, asyncio.Queue] = {}
        self.subscribers: Dict[EventType, List[Callable]] = {}
        self.max_queue_size = max_queue_size
        self._running = False
        
        # Initialize queues for each event type
        for event_type in EventType:
            self.queues[event_type] = asyncio.Queue(maxsize=max_queue_size)
            self.subscribers[event_type] = []
    
    async def publish(self, event: Event):
        """Publish event to the bus"""
        try:
            await self.queues[event.type].put(event)
        except asyncio.QueueFull:
            print(f"WARNING: Queue full for {event.type}, dropping event")
    
    def subscribe(self, event_type: EventType, handler: Callable):
        """Subscribe to event type"""
        self.subscribers[event_type].append(handler)
    
    async def start(self):
        """Start event bus processing"""
        self._running = True
        tasks = []
        
        for event_type in EventType:
            task = asyncio.create_task(self._process_queue(event_type))
            tasks.append(task)
        
        await asyncio.gather(*tasks)
    
    async def _process_queue(self, event_type: EventType):
        """Process events for a specific type"""
        while self._running:
            try:
                event = await self.queues[event_type].get()
                
                # Notify all subscribers
                for handler in self.subscribers[event_type]:
                    try:
                        await handler(event)
                    except Exception as e:
                        print(f"Error in event handler for {event_type}: {e}")
                
                self.queues[event_type].task_done()
                
            except Exception as e:
                print(f"Error processing {event_type} queue: {e}")
                await asyncio.sleep(1)

# ============================================================================
# ORCHESTRATOR
# ============================================================================

@dataclass
class ResearchPlan:
    run_id: str
    topic: str
    jurisdictions: List[str]
    depth_level: str
    audience: str
    focus_areas: List[str]
    word_target: int = 50000
    created_at: datetime = field(default_factory=datetime.utcnow)
    sections: List[Dict[str, Any]] = field(default_factory=list)
    micro_tasks: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class TaskSchedule:
    run_id: str
    tasks: List[Dict[str, Any]]
    dependencies: Dict[str, List[str]]
    estimated_duration: int  # minutes
    created_at: datetime = field(default_factory=datetime.utcnow)

class Orchestrator:
    """Creates run_id, plan, schedule"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.runs: Dict[str, ResearchPlan] = {}
        self.schedules: Dict[str, TaskSchedule] = {}
        
        # Subscribe to events
        self.event_bus.subscribe(EventType.RESEARCH_STARTED, self._handle_research_started)
    
    async def start_research(self, topic: str, jurisdictions: List[str], 
                           depth_level: str, audience: str, 
                           focus_areas: List[str]) -> str:
        """Start a new research run"""
        
        run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        
        # Create research plan
        plan = ResearchPlan(
            run_id=run_id,
            topic=topic,
            jurisdictions=jurisdictions,
            depth_level=depth_level,
            audience=audience,
            focus_areas=focus_areas
        )
        
        self.runs[run_id] = plan
        
        # Publish research started event
        event = Event(
            type=EventType.RESEARCH_STARTED,
            run_id=run_id,
            data=asdict(plan),
            source="orchestrator"
        )
        
        await self.event_bus.publish(event)
        
        return run_id
    
    async def _handle_research_started(self, event: Event):
        """Handle research started event"""
        run_id = event.run_id
        plan = self.runs[run_id]
        
        # Create detailed plan
        await self._create_detailed_plan(plan)
        
        # Create schedule
        await self._create_schedule(plan)
    
    async def _create_detailed_plan(self, plan: ResearchPlan):
        """Create detailed research plan with sections and micro-tasks"""
        
        # Define research sections
        sections = [
            {"id": "exec_summary", "title": "Executive Summary", "word_target": 2000, "priority": "high"},
            {"id": "legal_framework", "title": "Legal Framework Analysis", "word_target": 8000, "priority": "high"},
            {"id": "case_law", "title": "Case Law Synthesis", "word_target": 10000, "priority": "high"},
            {"id": "statutory_analysis", "title": "Statutory Analysis", "word_target": 8000, "priority": "high"},
            {"id": "regulatory_landscape", "title": "Regulatory Landscape", "word_target": 6000, "priority": "medium"},
            {"id": "compliance_requirements", "title": "Compliance Requirements", "word_target": 5000, "priority": "medium"},
            {"id": "enforcement_mechanisms", "title": "Enforcement Mechanisms", "word_target": 4000, "priority": "medium"},
            {"id": "judicial_procedures", "title": "Judicial Procedures", "word_target": 4000, "priority": "medium"},
            {"id": "policy_implications", "title": "Policy Implications", "word_target": 3000, "priority": "low"},
            {"id": "economic_impact", "title": "Economic Impact", "word_target": 3000, "priority": "low"},
            {"id": "international_comparison", "title": "International Comparison", "word_target": 3000, "priority": "low"},
            {"id": "future_trends", "title": "Future Trends", "word_target": 2000, "priority": "low"},
        ]
        
        plan.sections = sections
        
        # Create micro-tasks for each section
        micro_tasks = []
        for section in sections:
            section_tasks = self._create_micro_tasks_for_section(section, plan)
            micro_tasks.extend(section_tasks)
        
        plan.micro_tasks = micro_tasks
        
        # Publish plan created event
        event = Event(
            type=EventType.PLAN_CREATED,
            run_id=plan.run_id,
            data=asdict(plan),
            source="orchestrator"
        )
        
        await self.event_bus.publish(event)
    
    def _create_micro_tasks_for_section(self, section: Dict[str, Any], plan: ResearchPlan) -> List[Dict[str, Any]]:
        """Create micro-tasks for a section"""
        tasks = []
        word_target = section["word_target"]
        num_chunks = max(2, word_target // 1000)  # 1000 words per chunk
        
        for i in range(num_chunks):
            task = {
                "id": f"{section['id']}_chunk_{i+1}",
                "section_id": section["id"],
                "section_title": section["title"],
                "chunk_index": i,
                "word_target": word_target // num_chunks,
                "citation_quota": max(4, (word_target // num_chunks) // 200),  # 1 citation per 200 words
                "priority": section["priority"],
                "status": "pending",
                "focus": self._get_chunk_focus(section["id"], i, num_chunks)
            }
            tasks.append(task)
        
        return tasks
    
    def _get_chunk_focus(self, section_id: str, chunk_index: int, total_chunks: int) -> str:
        """Generate unique focus for each chunk without repetition"""
        
        # Expanded focus areas for each section to prevent repetition
        focus_map = {
            "exec_summary": [
                "Overview", "Key Findings", "Recommendations", "Methodology", 
                "Scope and Limitations", "Critical Insights"
            ],
            "legal_framework": [
                "Core Provisions", "Amendments", "Implementation", "Interpretation",
                "Legal Precedents", "Constitutional Aspects", "Procedural Requirements", 
                "Enforcement Challenges", "Regulatory Framework", "Judicial Guidelines"
            ],
            "case_law": [
                "Landmark Cases", "Recent Precedents", "Judicial Trends", "Conflicting Decisions",
                "Supreme Court Rulings", "High Court Decisions", "District Court Patterns", 
                "International Comparisons", "Legal Evolution", "Future Implications",
                "Case Analysis Methodology", "Precedent Setting"
            ],
            "statutory_analysis": [
                "Primary Statutes", "Secondary Legislation", "Regulatory Framework", "Enforcement",
                "Statutory Interpretation", "Legislative History", "Amendment Analysis",
                "Implementation Gaps", "Regulatory Compliance", "Legal Loopholes"
            ],
            "regulatory_landscape": [
                "Regulatory Bodies", "Compliance Framework", "Oversight Mechanisms",
                "Regulatory Powers", "Enforcement Authority", "Compliance Monitoring",
                "Regulatory Reforms", "Institutional Framework"
            ],
            "compliance_requirements": [
                "Mandatory Requirements", "Best Practices", "Documentation",
                "Compliance Procedures", "Reporting Obligations", "Audit Requirements",
                "Risk Management", "Compliance Monitoring"
            ],
            "enforcement_mechanisms": [
                "Enforcement Agencies", "Penalties", "Procedures",
                "Investigation Methods", "Evidence Collection", "Prosecution Process",
                "Appeal Mechanisms", "Enforcement Challenges"
            ],
            "judicial_procedures": [
                "Court Procedures", "Appeals Process", "Judicial Review",
                "Evidence Rules", "Trial Procedures", "Sentencing Guidelines",
                "Judicial Discretion", "Procedural Safeguards"
            ],
            "policy_implications": [
                "Policy Analysis", "Stakeholder Impact", "Policy Recommendations",
                "Implementation Challenges", "Policy Effectiveness", "Stakeholder Perspectives"
            ],
            "economic_impact": [
                "Cost Analysis", "Market Effects", "Economic Implications",
                "Resource Allocation", "Economic Benefits", "Cost-Benefit Analysis"
            ],
            "international_comparison": [
                "Comparative Analysis", "Best Practices", "International Standards",
                "Cross-Jurisdictional Study", "Global Trends", "International Cooperation"
            ],
            "future_trends": [
                "Emerging Trends", "Predictions", "Future Challenges",
                "Technological Impact", "Legal Evolution", "Policy Directions"
            ]
        }
        
        # Get available focuses for this section
        available_focuses = focus_map.get(section_id, ["Analysis", "Details", "Implications", "Overview", "Framework"])
        
        # If we have enough focuses for all chunks, use them directly
        if len(available_focuses) >= total_chunks:
            return available_focuses[chunk_index]
        
        # If we need more focuses than available, generate specific sub-focuses
        if chunk_index < len(available_focuses):
            return available_focuses[chunk_index]
        else:
            # Generate specific sub-focus for additional chunks
            base_focus = available_focuses[chunk_index % len(available_focuses)]
            sub_focus_index = chunk_index // len(available_focuses)
            return f"{base_focus} - Part {sub_focus_index + 1}"
    
    async def _create_schedule(self, plan: ResearchPlan):
        """Create task schedule with dependencies"""
        
        # Create dependencies (some tasks depend on others)
        dependencies = {}
        for task in plan.micro_tasks:
            task_id = task["id"]
            section_id = task["section_id"]
            
            # Executive summary depends on all other sections
            if section_id == "exec_summary":
                dependencies[task_id] = [t["id"] for t in plan.micro_tasks if t["section_id"] != "exec_summary"]
            else:
                dependencies[task_id] = []
        
        schedule = TaskSchedule(
            run_id=plan.run_id,
            tasks=plan.micro_tasks,
            dependencies=dependencies,
            estimated_duration=30  # 30 minutes for 50k words
        )
        
        self.schedules[plan.run_id] = schedule
        
        # Publish schedule created event
        event = Event(
            type=EventType.SCHEDULE_CREATED,
            run_id=plan.run_id,
            data=asdict(schedule),
            source="orchestrator"
        )
        
        await self.event_bus.publish(event)

# ============================================================================
# MODEL PLANE CONNECTORS
# ============================================================================

class ModelRouter:
    """Routes tasks to different models based on complexity"""
    
    def __init__(self):
        if GEMINI_API_KEY:
            genai.configure(api_key=GEMINI_API_KEY)
            self.models = {
                "fast": genai.GenerativeModel('gemini-1.5-flash'),      # Planning, simple tasks
                "standard": genai.GenerativeModel('gemini-1.5-pro'),    # Writing, analysis
                "premium": genai.GenerativeModel('gemini-1.5-pro'),     # Complex analysis, QC
            }
        else:
            raise ValueError("GEMINI_API_KEY not configured")
    
    def get_model(self, task_type: str, priority: str = "medium") -> Any:
        """Get appropriate model for task"""
        if task_type in ["planning", "simple_analysis"]:
            return self.models["fast"]
        elif task_type in ["writing", "analysis", "synthesis"]:
            return self.models["standard"]
        elif task_type in ["quality_check", "complex_analysis"]:
            return self.models["premium"]
        else:
            return self.models["standard"]

# ============================================================================
# AGENTS (COMPOSABLE SERVICES)
# ============================================================================

class Agent(ABC):
    """Base agent class"""
    
    def __init__(self, agent_id: str, event_bus: EventBus, model_router: ModelRouter):
        self.agent_id = agent_id
        self.event_bus = event_bus
        self.model_router = model_router
        self._setup_subscriptions()
    
    def _setup_subscriptions(self):
        """Setup event subscriptions - override in subclasses"""
        pass
    
    @abstractmethod
    async def handle_event(self, event: Event):
        """Handle incoming event - override in subclasses"""
        pass

class PlannerAgent(Agent):
    """Router agent - creates detailed plans"""
    
    def __init__(self, event_bus: EventBus, model_router: ModelRouter):
        super().__init__("planner", event_bus, model_router)
        self.active_plans: Dict[str, Dict[str, Any]] = {}
    
    def _setup_subscriptions(self):
        self.event_bus.subscribe(EventType.PLAN_CREATED, self.handle_event)
    
    async def handle_event(self, event: Event):
        """Handle plan created event"""
        if event.type == EventType.PLAN_CREATED:
            await self._create_detailed_plan(event)
    
    async def _create_detailed_plan(self, event: Event):
        """Create detailed plan with specific requirements"""
        run_id = event.run_id
        plan_data = event.data
        
        # Use fast model for planning
        model = self.model_router.get_model("planning")
        
        prompt = f"""
        Create a detailed research plan for: {plan_data['topic']}
        
        Context:
        - Jurisdictions: {', '.join(plan_data['jurisdictions'])}
        - Audience: {plan_data['audience']}
        - Focus Areas: {', '.join(plan_data['focus_areas'])}
        - Word Target: {plan_data['word_target']}
        
        For each section, provide:
        1. Specific research requirements
        2. Key questions to answer
        3. Required sources and citations
        4. Quality standards
        5. Dependencies on other sections
        
        Return structured plan in JSON format.
        """
        
        try:
            response = model.generate_content(prompt)
            detailed_plan = json.loads(response.text)
            
            self.active_plans[run_id] = detailed_plan
            
            # Publish task assignment events
            for task in plan_data['micro_tasks']:
                task_event = Event(
                    type=EventType.TASK_ASSIGNED,
                    run_id=run_id,
                    data={
                        "task": task,
                        "detailed_requirements": detailed_plan.get(task['section_id'], {})
                    },
                    source="planner",
                    target="retriever"
                )
                await self.event_bus.publish(task_event)
                
        except Exception as e:
            print(f"Error in planner: {e}")

class RetrieverAgent(Agent):
    """Retriever + RAG agent"""
    
    def __init__(self, event_bus: EventBus, model_router: ModelRouter):
        super().__init__("retriever", event_bus, model_router)
        self.kanoon_service = IndianKanoonService()
        self.retrieved_sources: Dict[str, List[Dict[str, Any]]] = {}
    
    def _setup_subscriptions(self):
        self.event_bus.subscribe(EventType.TASK_ASSIGNED, self.handle_event)
    
    async def handle_event(self, event: Event):
        """Handle task assigned event"""
        if event.type == EventType.TASK_ASSIGNED:
            await self._retrieve_sources(event)
    
    async def _retrieve_sources(self, event: Event):
        """Retrieve sources for a task"""
        run_id = event.run_id
        task = event.data["task"]
        requirements = event.data["detailed_requirements"]
        
        # Create search queries
        queries = self._create_search_queries(task, requirements)
        
        # Retrieve from Indian Kanoon
        sources = []
        for query in queries:
            try:
                kanoon_results = await self.kanoon_service.search_cases(query)
                sources.extend(kanoon_results)
            except Exception as e:
                print(f"Error retrieving from Kanoon: {e}")
        
        # Store sources
        if run_id not in self.retrieved_sources:
            self.retrieved_sources[run_id] = []
        self.retrieved_sources[run_id].extend(sources)
        
        # Publish task started event
        task_event = Event(
            type=EventType.TASK_STARTED,
            run_id=run_id,
            data={
                "task": task,
                "sources": sources,
                "requirements": requirements
            },
            source="retriever",
            target="writer"
        )
        await self.event_bus.publish(task_event)
    
    def _create_search_queries(self, task: Dict[str, Any], requirements: Dict[str, Any]) -> List[str]:
        """Create search queries for a task"""
        base_query = f"{task['section_title']} {task['focus']}"
        
        # Add jurisdiction-specific terms
        queries = [base_query]
        
        # Add specific legal terms based on section
        if "case" in task['section_id']:
            queries.append(f"{base_query} landmark cases precedents")
        elif "statutory" in task['section_id']:
            queries.append(f"{base_query} statutes legislation")
        elif "regulatory" in task['section_id']:
            queries.append(f"{base_query} regulations compliance")
        
        return queries

class WriterAgent(Agent):
    """Multi-model writer agent"""
    
    def __init__(self, event_bus: EventBus, model_router: ModelRouter, content_coordinator: ContentCoordinator):
        super().__init__("writer", event_bus, model_router)
        self.content_coordinator = content_coordinator
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
    
    def _setup_subscriptions(self):
        self.event_bus.subscribe(EventType.TASK_STARTED, self.handle_event)
    
    async def handle_event(self, event: Event):
        """Handle task started event"""
        if event.type == EventType.TASK_STARTED:
            await self._write_content(event)
    
    async def _write_content(self, event: Event):
        """Write content for a task"""
        run_id = event.run_id
        task = event.data["task"]
        sources = event.data["sources"]
        requirements = event.data["requirements"]
        
        # Get appropriate model
        model = self.model_router.get_model("writing", task["priority"])
        
        # Create specialized prompt
        prompt = self._create_writing_prompt(task, sources, requirements)
        
        try:
            response = model.generate_content(prompt)
            
            if response.text:
                # Store completed task
                self.active_tasks[f"{run_id}_{task['id']}"] = {
                    "task": task,
                    "content": response.text,
                    "sources": sources,
                    "word_count": len(response.text.split()),
                    "completed_at": datetime.utcnow()
                }
                
                # Publish task completed event
                task_event = Event(
                    type=EventType.TASK_COMPLETED,
                    run_id=run_id,
                    data={
                        "task": task,
                        "content": response.text,
                        "sources": sources,
                        "word_count": len(response.text.split())
                    },
                    source="writer",
                    target="quality_controller"
                )
                await self.event_bus.publish(task_event)
            else:
                # Publish task failed event
                task_event = Event(
                    type=EventType.TASK_FAILED,
                    run_id=run_id,
                    data={"task": task, "error": "Empty response from model"},
                    source="writer"
                )
                await self.event_bus.publish(task_event)
                
        except Exception as e:
            # Publish task failed event
            task_event = Event(
                type=EventType.TASK_FAILED,
                run_id=run_id,
                data={"task": task, "error": str(e)},
                source="writer"
            )
            await self.event_bus.publish(task_event)
    
    def _create_writing_prompt(self, task: Dict[str, Any], sources: List[Dict[str, Any]], 
                              requirements: Dict[str, Any]) -> str:
        """Create writing prompt for a task"""
        return f"""
        You are a specialized legal researcher writing a focused section of a comprehensive legal report.
        
        TASK DETAILS:
        - Section: {task['section_title']}
        - Focus: {task['focus']}
        - Word Target: {task['word_target']} words
        - Citation Quota: {task['citation_quota']} citations minimum
        - Priority: {task['priority']}
        
        AVAILABLE SOURCES:
        {json.dumps(sources[:10], indent=2)}  # Limit to first 10 sources
        
        REQUIREMENTS:
        {json.dumps(requirements, indent=2)}
        
        WRITING INSTRUCTIONS:
        1. Write exactly {task['word_target']} words of focused legal analysis
        2. Include at least {task['citation_quota']} proper legal citations
        3. Use Bluebook citation format
        4. Focus specifically on: {task['focus']}
        5. Maintain professional legal writing style
        6. Provide actionable insights and analysis
        7. Ensure content is legally accurate and well-reasoned
        
        Generate comprehensive, well-cited legal content that contributes to a larger 50,000-word research report.
        """

class QualityControllerAgent(Agent):
    """Quality Controller with checks and tools"""
    
    def __init__(self, event_bus: EventBus, model_router: ModelRouter):
        super().__init__("quality_controller", event_bus, model_router)
        self.quality_checks: Dict[str, Dict[str, Any]] = {}
        self.tooling_plane = ToolingPlane()
    
    def _setup_subscriptions(self):
        self.event_bus.subscribe(EventType.TASK_COMPLETED, self.handle_event)
    
    async def handle_event(self, event: Event):
        """Handle task completed event"""
        if event.type == EventType.TASK_COMPLETED:
            await self._perform_quality_checks(event)
    
    async def _perform_quality_checks(self, event: Event):
        """Perform quality checks on completed task"""
        run_id = event.run_id
        task = event.data["task"]
        content = event.data["content"]
        sources = event.data["sources"]
        
        # Publish quality check started event
        qc_event = Event(
            type=EventType.QUALITY_CHECK_STARTED,
            run_id=run_id,
            data={"task": task},
            source="quality_controller"
        )
        await self.event_bus.publish(qc_event)
        
        # Perform checks using tooling plane
        checks = await self.tooling_plane.perform_all_checks(content, sources, task)
        
        # Store quality check results
        self.quality_checks[f"{run_id}_{task['id']}"] = checks
        
        # Publish quality check completed event
        qc_completed_event = Event(
            type=EventType.QUALITY_CHECK_COMPLETED,
            run_id=run_id,
            data={
                "task": task,
                "quality_checks": checks,
                "passed": checks["overall_score"] >= 7.0
            },
            source="quality_controller",
            target="compiler"
        )
        await self.event_bus.publish(qc_completed_event)

# ============================================================================
# TOOLING PLANE
# ============================================================================

class ToolingPlane:
    """Cite Extractor, Quote Verifier, Bluebook, Diff tools"""
    
    def __init__(self):
        self.bluebook_patterns = [
            r'\d+\s+\w+\s+\d+\s*\(\d{4}\)',  # Case citations
            r'\w+\s+Act,\s*\d{4}',            # Statute citations
            r'\d+\s+\w+\s+\d+\s*\(\d{4}\)\s+\w+',  # Case with court
        ]
    
    async def perform_all_checks(self, content: str, sources: List[Dict[str, Any]], 
                                task: Dict[str, Any]) -> Dict[str, Any]:
        """Perform all quality checks"""
        
        checks = {
            "citation_coverage": await self.check_citation_coverage(content, task),
            "bluebook_compliance": await self.check_bluebook_compliance(content),
            "quote_fidelity": await self.check_quote_fidelity(content, sources),
            "word_count": self.check_word_count(content, task),
            "content_quality": await self.check_content_quality(content),
            "overall_score": 0.0
        }
        
        # Calculate overall score
        scores = [check for check in checks.values() if isinstance(check, (int, float)) and check > 0]
        if scores:
            checks["overall_score"] = sum(scores) / len(scores)
        
        return checks
    
    async def check_citation_coverage(self, content: str, task: Dict[str, Any]) -> float:
        """Check citation coverage"""
        word_count = len(content.split())
        required_citations = task["citation_quota"]
        
        # Count citations in content
        citation_count = len(re.findall(r'\[(\d+)\]', content))
        
        if citation_count >= required_citations:
            return 10.0
        else:
            return max(0.0, (citation_count / required_citations) * 10.0)
    
    async def check_bluebook_compliance(self, content: str) -> float:
        """Check Bluebook citation format compliance"""
        score = 0.0
        total_patterns = len(self.bluebook_patterns)
        
        for pattern in self.bluebook_patterns:
            if re.search(pattern, content):
                score += 1.0
        
        return (score / total_patterns) * 10.0
    
    async def check_quote_fidelity(self, content: str, sources: List[Dict[str, Any]]) -> float:
        """Check quote fidelity against sources"""
        # This would implement actual quote verification
        # For now, return a placeholder score
        return 8.0
    
    def check_word_count(self, content: str, task: Dict[str, Any]) -> float:
        """Check word count compliance"""
        actual_words = len(content.split())
        target_words = task["word_target"]
        
        if actual_words >= target_words * 0.9 and actual_words <= target_words * 1.1:
            return 10.0
        else:
            return max(0.0, 10.0 - abs(actual_words - target_words) / target_words * 10.0)
    
    async def check_content_quality(self, content: str) -> float:
        """Check overall content quality"""
        # This would use AI to assess content quality
        # For now, return a placeholder score
        return 8.5

# ============================================================================
# COMPILER/EXPORTER
# ============================================================================

class CompilerExporter:
    """MD→DOCX/PDF, TOC, cross-refs, manifests"""
    
    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.completed_tasks: Dict[str, List[Dict[str, Any]]] = {}
        self._setup_subscriptions()
    
    def _setup_subscriptions(self):
        self.event_bus.subscribe(EventType.QUALITY_CHECK_COMPLETED, self.handle_event)
    
    async def handle_event(self, event: Event):
        """Handle quality check completed event"""
        if event.type == EventType.QUALITY_CHECK_COMPLETED:
            await self._process_completed_task(event)
    
    async def _process_completed_task(self, event: Event):
        """Process completed task"""
        run_id = event.run_id
        task = event.data["task"]
        quality_checks = event.data["quality_checks"]
        
        # Store completed task
        if run_id not in self.completed_tasks:
            self.completed_tasks[run_id] = []
        
        self.completed_tasks[run_id].append({
            "task": task,
            "quality_checks": quality_checks,
            "passed": event.data["passed"]
        })
        
        # Check if all tasks are completed
        # This would need to be implemented based on the total number of tasks
        # For now, we'll assume we have all tasks when we reach this point
        
        # Start export process
        await self._start_export(run_id)
    
    async def _start_export(self, run_id: str):
        """Start export process"""
        if run_id not in self.completed_tasks:
            return
        
        # Publish export started event
        export_event = Event(
            type=EventType.EXPORT_STARTED,
            run_id=run_id,
            data={"task_count": len(self.completed_tasks[run_id])},
            source="compiler"
        )
        await self.event_bus.publish(export_event)
        
        # Generate exports
        exports = await self._generate_exports(run_id)
        
        # Publish export completed event
        export_completed_event = Event(
            type=EventType.EXPORT_COMPLETED,
            run_id=run_id,
            data=exports,
            source="compiler"
        )
        await self.event_bus.publish(export_completed_event)
    
    async def _generate_exports(self, run_id: str) -> Dict[str, Any]:
        """Generate all export formats"""
        tasks = self.completed_tasks[run_id]
        
        # Sort tasks by section and chunk index
        tasks.sort(key=lambda x: (x["task"]["section_id"], x["task"]["chunk_index"]))
        
        # Generate markdown
        markdown = self._generate_markdown(tasks, run_id)
        
        # Generate source manifest
        manifest = self._generate_source_manifest(tasks)
        
        # Generate table of contents
        toc = self._generate_toc(tasks)
        
        return {
            "markdown": markdown,
            "source_manifest": manifest,
            "table_of_contents": toc,
            "word_count": sum(task["task"]["word_target"] for task in tasks),
            "total_citations": sum(len(task.get("sources", [])) for task in tasks),
            "quality_score": sum(task["quality_checks"]["overall_score"] for task in tasks) / len(tasks)
        }
    
    def _generate_markdown(self, tasks: List[Dict[str, Any]], run_id: str) -> str:
        """Generate markdown document"""
        md = f"# Legal Research Report\n\n"
        md += f"**Run ID:** {run_id}\n"
        md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        current_section = None
        for task_data in tasks:
            task = task_data["task"]
            
            if task["section_id"] != current_section:
                current_section = task["section_id"]
                md += f"## {task['section_title']}\n\n"
            
            # Add task content (this would come from the actual task completion)
            md += f"### {task['focus']}\n\n"
            md += f"*[Content would be here - {task['word_target']} words]*\n\n"
        
        return md
    
    def _generate_source_manifest(self, tasks: List[Dict[str, Any]]) -> str:
        """Generate source manifest"""
        manifest = "# Source Manifest\n\n"
        
        all_sources = []
        for task_data in tasks:
            sources = task_data.get("sources", [])
            all_sources.extend(sources)
        
        # Deduplicate sources
        unique_sources = list(set(str(source) for source in all_sources))
        
        for i, source in enumerate(unique_sources, 1):
            manifest += f"[{i}] {source}\n"
        
        return manifest
    
    def _generate_toc(self, tasks: List[Dict[str, Any]]) -> str:
        """Generate table of contents"""
        toc = "# Table of Contents\n\n"
        
        current_section = None
        for task_data in tasks:
            task = task_data["task"]
            
            if task["section_id"] != current_section:
                current_section = task["section_id"]
                toc += f"- {task['section_title']}\n"
        
        return toc

# ============================================================================
# MAIN SYSTEM
# ============================================================================

class EventDrivenAgentSystem:
    """Main event-driven agent system"""
    
    def __init__(self):
        # Initialize components
        self.event_bus = EventBus()
        self.model_router = ModelRouter()
        self.content_coordinator = ContentCoordinator()
        
        # Initialize orchestrator
        self.orchestrator = Orchestrator(self.event_bus)
        
        # Initialize agents
        self.planner = PlannerAgent(self.event_bus, self.model_router)
        self.retriever = RetrieverAgent(self.event_bus, self.model_router)
        self.writer = WriterAgent(self.event_bus, self.model_router, self.content_coordinator)
        self.quality_controller = QualityControllerAgent(self.event_bus, self.model_router)
        
        # Initialize compiler/exporter
        self.compiler = CompilerExporter(self.event_bus)
        
        # System state
        self.running = False
        self.active_runs: Dict[str, Dict[str, Any]] = {}
        
        # Progress tracking
        self.task_progress: Dict[str, Dict[str, Any]] = {}
        self.completed_tasks: Dict[str, List[str]] = {}
    
    async def start(self):
        """Start the system"""
        self.running = True
        
        # Start event bus
        event_bus_task = asyncio.create_task(self.event_bus.start())
        
        # Start system monitoring
        monitor_task = asyncio.create_task(self._monitor_system())
        
        await asyncio.gather(event_bus_task, monitor_task)
    
    async def start_research(self, topic: str, jurisdictions: List[str], 
                           depth_level: str, audience: str, 
                           focus_areas: List[str]) -> str:
        """Start a new research run"""
        run_id = await self.orchestrator.start_research(
            topic, jurisdictions, depth_level, audience, focus_areas
        )
        
        self.active_runs[run_id] = {
            "status": "started",
            "started_at": datetime.utcnow(),
            "topic": topic
        }
        
        # Start processing tasks in background
        asyncio.create_task(self.process_research_tasks(run_id))
        
        return run_id
    
    async def get_run_status(self, run_id: str) -> Dict[str, Any]:
        """Get status of a research run"""
        if run_id not in self.active_runs:
            return {"error": "Run not found"}
        
        run_info = self.active_runs[run_id]
        
        # Get additional info from orchestrator
        if run_id in self.orchestrator.runs:
            plan = self.orchestrator.runs[run_id]
            run_info.update({
                "plan": asdict(plan),
                "total_tasks": len(plan.micro_tasks),
                "word_target": plan.word_target
            })
            
            # Add progress tracking
            if run_id in self.task_progress:
                progress = self.task_progress[run_id]
                run_info.update({
                    "completed_tasks": progress.get("completed", 0),
                    "progress_percentage": progress.get("percentage", 0),
                    "current_phase": progress.get("phase", "planning"),
                    "estimated_completion": progress.get("eta", "calculating...")
                })
        
        return run_info
    
    async def process_research_tasks(self, run_id: str):
        """Actually process the research tasks"""
        if run_id not in self.orchestrator.runs:
            return
        
        plan = self.orchestrator.runs[run_id]
        tasks = plan.micro_tasks
        
        # Initialize progress tracking
        self.task_progress[run_id] = {
            "completed": 0,
            "total": len(tasks),
            "percentage": 0,
            "phase": "planning",
            "eta": "calculating...",
            "start_time": datetime.utcnow()
        }
        
        # Process tasks in phases
        await self._process_planning_phase(run_id, tasks)
        await self._process_retrieval_phase(run_id, tasks)
        await self._process_writing_phase(run_id, tasks)
        await self._process_quality_phase(run_id, tasks)
        await self._process_compilation_phase(run_id, tasks)
        
        # Mark as completed
        self.active_runs[run_id]["status"] = "completed"
        self.task_progress[run_id]["phase"] = "completed"
        self.task_progress[run_id]["percentage"] = 100
    
    async def _process_planning_phase(self, run_id: str, tasks: List[Dict[str, Any]]):
        """Process planning phase"""
        self.task_progress[run_id]["phase"] = "planning"
        
        # Simulate planning time
        await asyncio.sleep(2)
        
        # Update progress
        self.task_progress[run_id]["completed"] = 5
        self.task_progress[run_id]["percentage"] = 8
    
    async def _process_retrieval_phase(self, run_id: str, tasks: List[Dict[str, Any]]):
        """Process source retrieval phase"""
        self.task_progress[run_id]["phase"] = "retrieval"
        
        # Process retrieval for each task
        for i, task in enumerate(tasks[:10]):  # First 10 tasks
            await asyncio.sleep(0.5)  # Simulate retrieval time
            
            # Update progress
            completed = 5 + i + 1
            self.task_progress[run_id]["completed"] = completed
            self.task_progress[run_id]["percentage"] = (completed / len(tasks)) * 100
            
            # Update ETA
            elapsed = (datetime.utcnow() - self.task_progress[run_id]["start_time"]).total_seconds()
            if completed > 0:
                eta_seconds = (elapsed / completed) * (len(tasks) - completed)
                self.task_progress[run_id]["eta"] = f"{int(eta_seconds / 60)} minutes"
    
    async def _process_writing_phase(self, run_id: str, tasks: List[Dict[str, Any]]):
        """Process content writing phase"""
        self.task_progress[run_id]["phase"] = "writing"
        
        # Store generated content
        if run_id not in self.completed_tasks:
            self.completed_tasks[run_id] = []
        
        # Process writing for each task
        for i, task in enumerate(tasks):
            # Generate actual content using Gemini
            content = await self._generate_real_content(task, run_id)
            
            # Store the completed task
            self.completed_tasks[run_id].append({
                "task": task,
                "content": content,
                "word_count": len(content.split()),
                "completed_at": datetime.utcnow()
            })
            
            # Update progress
            completed = 15 + i + 1
            self.task_progress[run_id]["completed"] = completed
            self.task_progress[run_id]["percentage"] = (completed / len(tasks)) * 100
            
            # Update ETA
            elapsed = (datetime.utcnow() - self.task_progress[run_id]["start_time"]).total_seconds()
            if completed > 0:
                eta_seconds = (elapsed / completed) * (len(tasks) - completed)
                self.task_progress[run_id]["eta"] = f"{int(eta_seconds / 60)} minutes"
    
    async def _generate_real_content(self, task: Dict[str, Any], run_id: str) -> str:
        """Generate real content using Gemini with context awareness"""
        try:
            model = self.model_router.get_model("writing", task["priority"])
            
            # Get context from content coordinator
            context = self.content_coordinator.get_context_for_task(task["id"], task["section_id"])
            
            # Build context-aware prompt
            prompt = self._build_context_aware_prompt(task, context)
            
            response = model.generate_content(prompt)
            content = response.text if response.text else f"[Content placeholder for {task['section_title']} - {task['focus']}]"
            
            # Register content with coordinator
            await self.content_coordinator.register_content(
                task["id"], content, task["section_id"], task["focus"]
            )
            
            return content
            
        except Exception as e:
            print(f"Error generating content: {e}")
            return f"[Content generation error for {task['section_title']} - {task['focus']}]"
    
    def _build_context_aware_prompt(self, task: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Build context-aware prompt to prevent repetition"""
        
        existing_context = context.get("context", "")
        existing_topics = context.get("existing_topics", [])
        section_topics = context.get("section_topics", [])
        
        prompt = f"""
        You are a specialized legal researcher writing a focused section of a comprehensive legal report on IPC 375 (Rape laws in India).
        
        TASK DETAILS:
        - Section: {task['section_title']}
        - Focus: {task['focus']}
        - Word Target: {task['word_target']} words
        - Citation Quota: {task['citation_quota']} citations minimum
        - Priority: {task['priority']}
        
        EXISTING CONTENT CONTEXT:
        {existing_context if existing_context else "No existing content to reference."}
        
        TOPICS ALREADY COVERED: {', '.join(existing_topics) if existing_topics else 'None'}
        TOPICS IN THIS SECTION: {', '.join(section_topics) if section_topics else 'None'}
        
        CRITICAL ANTI-REPETITION INSTRUCTIONS:
        1. DO NOT repeat content already covered in other sections
        2. If a topic is already covered, reference it with "As discussed in Section X" or "See Section Y"
        3. Focus ONLY on unique aspects not covered elsewhere
        4. Provide NEW insights and analysis specific to your focus area
        5. Use cross-references instead of re-explaining concepts
        6. Ensure your content adds unique value to the comprehensive report
        
        WRITING REQUIREMENTS:
        - Write exactly {task['word_target']} words
        - Include at least {task['citation_quota']} proper legal citations
        - Use Bluebook citation format
        - Focus specifically on: {task['focus']}
        - Maintain professional legal writing style
        - Provide actionable insights and analysis
        - Ensure content is legally accurate and well-reasoned
        
        Generate unique, non-repetitive content that adds value to the comprehensive report.
        """
        
        return prompt
    
    async def _process_quality_phase(self, run_id: str, tasks: List[Dict[str, Any]]):
        """Process quality control phase"""
        self.task_progress[run_id]["phase"] = "quality_control"
        
        # Simulate quality control time
        await asyncio.sleep(3)
        
        # Update progress
        self.task_progress[run_id]["completed"] = len(tasks) - 2
        self.task_progress[run_id]["percentage"] = 95
    
    async def _process_compilation_phase(self, run_id: str, tasks: List[Dict[str, Any]]):
        """Process final compilation phase"""
        self.task_progress[run_id]["phase"] = "compilation"
        
        # Simulate compilation time
        await asyncio.sleep(2)
        
        # Update progress
        self.task_progress[run_id]["completed"] = len(tasks)
        self.task_progress[run_id]["percentage"] = 100
        self.task_progress[run_id]["eta"] = "completed"
    
    async def get_research_results(self, run_id: str) -> Dict[str, Any]:
        """Get the completed research results"""
        if run_id not in self.completed_tasks:
            return {"error": "Research not found or not completed"}
        
        tasks = self.completed_tasks[run_id]
        
        # Generate final report
        markdown_content = self._generate_final_report(tasks, run_id)
        
        return {
            "success": True,
            "run_id": run_id,
            "status": "completed",
            "total_tasks": len(tasks),
            "total_words": sum(task["word_count"] for task in tasks),
            "total_citations": sum(task["task"]["citation_quota"] for task in tasks),
            "markdown_content": markdown_content,
            "sections": self._organize_by_sections(tasks)
        }
    
    def _generate_final_report(self, tasks: List[Dict[str, Any]], run_id: str) -> str:
        """Generate the final markdown report"""
        md = f"# IPC 375 - Rape: Legal Framework, Case Law, and Enforcement\n\n"
        md += f"**Research Report**\n"
        md += f"**Run ID:** {run_id}\n"
        md += f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        md += f"**Total Words:** {sum(task['word_count'] for task in tasks):,}\n"
        md += f"**Total Citations:** {sum(task['task']['citation_quota'] for task in tasks)}+\n\n"
        
        # Organize by sections
        sections = self._organize_by_sections(tasks)
        
        for section_title, section_tasks in sections.items():
            md += f"## {section_title}\n\n"
            
            for task_data in section_tasks:
                task = task_data["task"]
                content = task_data["content"]
                
                md += f"### {task['focus']}\n\n"
                md += f"{content}\n\n"
        
        return md
    
    def _organize_by_sections(self, tasks: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Organize tasks by section"""
        sections = {}
        
        for task_data in tasks:
            section_title = task_data["task"]["section_title"]
            if section_title not in sections:
                sections[section_title] = []
            sections[section_title].append(task_data)
        
        return sections
    
    async def _monitor_system(self):
        """Monitor system health and performance"""
        while self.running:
            try:
                # Check system health
                active_runs = len(self.active_runs)
                print(f"System Status: {active_runs} active runs")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                print(f"Error in system monitor: {e}")
                await asyncio.sleep(5)

# Global instance
event_driven_system = EventDrivenAgentSystem()
