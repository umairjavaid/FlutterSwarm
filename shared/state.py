"""
Shared state management for FlutterSwarm agents.
Provides real-time synchronization and communication between all agents.
"""

import asyncio
import json
import uuid
import threading
import copy
import time
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pydantic import BaseModel
from config.config_manager import get_config

class CircuitBreaker:
    """Circuit breaker for preventing infinite loops and managing timeouts."""
    
    def __init__(self, max_iterations: int = 1000, max_time: float = 300.0, name: str = "unknown"):
        self.max_iterations = max_iterations
        self.max_time = max_time
        self.name = name
        self.start_time = time.time()
        self.iterations = 0
        self.should_stop = False
        
    def check(self) -> bool:
        """Check if circuit breaker should trip. Returns True if should continue, False if should stop."""
        if self.should_stop:
            return False
            
        self.iterations += 1
        elapsed = time.time() - self.start_time
        
        if self.iterations > self.max_iterations:
            print(f"⚠️ Circuit breaker {self.name}: Maximum iterations ({self.max_iterations}) exceeded")
            self.should_stop = True
            return False
            
        if elapsed > self.max_time:
            print(f"⚠️ Circuit breaker {self.name}: Maximum time ({self.max_time}s) exceeded")
            self.should_stop = True
            return False
            
        return True
    
    def reset(self):
        """Reset the circuit breaker."""
        self.start_time = time.time()
        self.iterations = 0
        self.should_stop = False

class AgentStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"

class MessageType(Enum):
    STATUS_UPDATE = "status_update"
    TASK_REQUEST = "task_request"
    TASK_COMPLETED = "task_completed"
    COLLABORATION_REQUEST = "collaboration_request"
    STATE_SYNC = "state_sync"
    ERROR_REPORT = "error_report"
    # Supervision message types
    PROCESS_HALT = "process_halt"
    SUPERVISION_ALERT = "supervision_alert"
    FEATURE_VALIDATION_REQUEST = "feature_validation_request"
    HEARTBEAT = "heartbeat"
    HEALTH_CHECK = "health_check"
    # Real-time awareness message types
    REAL_TIME_STATUS_BROADCAST = "real_time_status_broadcast"
    AGENT_ACTIVITY_UPDATE = "agent_activity_update"
    PROACTIVE_ASSISTANCE_OFFER = "proactive_assistance_offer"
    AWARENESS_SUBSCRIPTION = "awareness_subscription"
    CONSCIOUSNESS_UPDATE = "consciousness_update"
    PREDICTIVE_COLLABORATION = "predictive_collaboration"

@dataclass
class AgentMessage:
    id: str
    from_agent: str
    to_agent: Optional[str]  # None for broadcast
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: datetime
    priority: int = 1  # 1=low, 5=high

@dataclass
class AgentState:
    agent_id: str
    status: AgentStatus
    current_task: Optional[str]
    progress: float  # 0.0 to 1.0
    last_update: datetime
    capabilities: List[str]
    metadata: Dict[str, Any]

@dataclass
class ProjectState:
    project_id: str
    name: str
    description: str
    requirements: List[str]
    current_phase: str
    progress: float
    files_created: Dict[str, str]  # filename -> content
    architecture_decisions: List[Dict[str, Any]]
    test_results: Dict[str, Any]
    security_findings: List[Dict[str, Any]]
    performance_metrics: Dict[str, Any]
    documentation: Dict[str, str]
    deployment_config: Dict[str, Any]
    # Flutter project path
    project_path: Optional[str] = None
    # Supervision fields
    supervision_status: Optional[str] = None
    process_health_metrics: Dict[str, Any] = None
    failed_processes: List[str] = None
    recovered_processes: List[str] = None
    e2e_test_results: Dict[str, Any] = None
    incremental_progress: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.process_health_metrics is None:
            self.process_health_metrics = {}
        if self.failed_processes is None:
            self.failed_processes = []
        if self.recovered_processes is None:
            self.recovered_processes = []
        if self.e2e_test_results is None:
            self.e2e_test_results = {}
        if self.incremental_progress is None:
            self.incremental_progress = {}

@dataclass
class IssueReport:
    issue_id: str
    project_id: str
    reporter_agent: str
    issue_type: str
    severity: str  # critical, high, medium, low
    description: str
    affected_files: List[str]
    fix_suggestions: List[str]
    status: str  # open, in_progress, resolved, ignored
    timestamp: datetime
    assigned_agent: Optional[str] = None
    resolution_notes: Optional[str] = None

@dataclass
class ProcessSupervisionState:
    """State tracking for process supervision and health monitoring."""
    process_id: str
    agent_id: str
    task_type: str
    start_time: datetime
    last_heartbeat: datetime
    timeout_threshold: float
    status: str  # running, stuck, timeout, completed, failed
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    intervention_count: int = 0
    recovery_attempts: int = 0

@dataclass
class E2ETestingState:
    """State for end-to-end testing across platforms."""
    test_session_id: str
    project_id: str
    platforms_tested: List[str]
    test_results: Dict[str, Dict[str, Any]]  # platform -> results
    overall_status: str  # pending, running, passed, failed
    start_time: datetime
    end_time: Optional[datetime] = None
    failure_details: Dict[str, str] = None
    
    def __post_init__(self):
        if self.failure_details is None:
            self.failure_details = {}

@dataclass
class IncrementalImplementationState:
    """State for incremental feature implementation and validation."""
    feature_queue: List[Dict[str, Any]]
    current_feature: Optional[Dict[str, Any]]
    completed_features: List[str]
    failed_features: List[str]
    feature_dependencies: Dict[str, List[str]]
    rollback_points: Dict[str, str]  # feature_id -> git_commit_hash
    validation_results: Dict[str, Dict[str, Any]]
    
    def __post_init__(self):
        if self.feature_queue is None:
            self.feature_queue = []
        if self.completed_features is None:
            self.completed_features = []
        if self.failed_features is None:
            self.failed_features = []
        if self.feature_dependencies is None:
            self.feature_dependencies = {}
        if self.rollback_points is None:
            self.rollback_points = {}
        if self.validation_results is None:
            self.validation_results = {}

@dataclass
class RealTimeAwarenessState:
    """Tracks real-time awareness and collaboration state."""
    agent_subscriptions: Dict[str, List[str]]  # agent_id -> [subscribed_to_agent_ids]
    active_collaborations: Dict[str, Dict[str, Any]]  # collaboration_id -> details
    proactive_opportunities: List[Dict[str, Any]]  # detected collaboration opportunities
    shared_consciousness: Dict[str, Any]  # global shared state
    agent_activity_streams: Dict[str, List[Dict[str, Any]]]  # agent_id -> activity_log
    predictive_insights: Dict[str, List[Dict[str, Any]]]  # agent_id -> predictions
    real_time_metrics: Dict[str, Any]  # performance and awareness metrics

@dataclass
class AgentActivityEvent:
    """Represents a real-time activity event from an agent."""
    agent_id: str
    activity_type: str
    activity_details: Dict[str, Any]
    timestamp: datetime
    project_id: Optional[str]
    impact_level: str  # low, medium, high, critical
    collaboration_relevance: List[str]  # agent types that might be interested

class SharedState:
    """
    Central shared state manager for all agents.
    Provides real-time synchronization and communication.
    """
    
    def __init__(self):
        # Initialize event loop and async-safe locking
        try:
            self._config = get_config()
        except Exception as e:
            print(f"Warning: Failed to load config: {e}")
            self._config = None
            
        # Thread-safe initialization of async locks
        self._shutdown_event = threading.Event()
        self._lock = threading.RLock()  # Main thread synchronization lock
        self._sync_lock = threading.RLock()  # Only for sync initialization
        self._main_async_lock = None  # Will be initialized in async context
        self._async_locks: Dict[str, asyncio.Lock] = {}
        self._async_lock_creation_lock = threading.Lock()
        self._loop = None
        
        # State data structures
        self._agents: Dict[str, AgentState] = {}
        self._projects: Dict[str, ProjectState] = {}
        self._messages: List[AgentMessage] = []
        self._message_queue: Dict[str, List[AgentMessage]] = {}
        self._subscribers: Dict[str, List[Callable]] = {}
        self._current_project_id: Optional[str] = None
        self._issues: Dict[str, List[IssueReport]] = {}  # project_id -> issues
        
        # Supervision state tracking
        self._supervised_processes: Dict[str, ProcessSupervisionState] = {}
        self._e2e_testing_sessions: Dict[str, E2ETestingState] = {}
        self._incremental_states: Dict[str, IncrementalImplementationState] = {}  # project_id -> state
        
        # Real-time awareness state
        self._awareness_state = RealTimeAwarenessState(
            agent_subscriptions={},
            active_collaborations={},
            proactive_opportunities=[],
            shared_consciousness={},
            agent_activity_streams={},
            predictive_insights={},
            real_time_metrics={}
        )
        self._activity_event_buffer: List[AgentActivityEvent] = []
        self._broadcast_enabled = True
        
        # Configure limits from config with robust error handling
        try:
            if self._config:
                self._max_messages = self._config.get('communication.messaging.queue_size', 500)
                self._message_ttl = self._config.get('communication.messaging.message_ttl', 3600)
                self._max_collaborations = self._config.get('communication.collaboration.max_concurrent_collaborations', 5)
            else:
                raise Exception("Config not available")
        except Exception:
            # Use defaults if config access fails
            self._max_messages = 500
            self._message_ttl = 3600
            self._max_collaborations = 5
        self._max_activity_events = 1000  # Maximum activity events to keep in buffer
        
        # Async locks with proper initialization and thread safety
        self._async_locks: Dict[str, asyncio.Lock] = {}
        self._async_lock_creation_lock = threading.Lock()  # Protect async lock creation
        self._loop = None  # Store event loop reference
        self._state_versions: Dict[str, List[Dict[str, Any]]] = {}
        self._version_counter = 0
        
        # Task deduplication tracking
        self._completed_tasks: Dict[str, Dict[str, Any]] = {}  # task_hash -> result
    
    async def _get_async_lock(self, lock_name: str = "default") -> asyncio.Lock:
        """Get or create an async lock with the given name - thread-safe."""
        if lock_name not in self._async_locks:
            with self._async_lock_creation_lock:  # Protect creation with threading lock
                if lock_name not in self._async_locks:  # Double-check pattern
                    self._async_locks[lock_name] = asyncio.Lock()
        return self._async_locks[lock_name]
    
    async def shutdown(self) -> None:
        """Shutdown the shared state and cleanup resources."""
        print("🔄 Shutting down SharedState...")
        self._shutdown_event.set()
        
        # Cancel any ongoing async operations
        current_tasks = [task for task in asyncio.all_tasks() if not task.done()]
        if current_tasks:
            print(f"🔄 Cancelling {len(current_tasks)} pending tasks...")
            for task in current_tasks:
                task.cancel()
            
            # Wait for tasks to complete cancellation
            await asyncio.gather(*current_tasks, return_exceptions=True)
        
        print("✅ SharedState shutdown complete")
    
    def is_shutdown(self) -> bool:
        """Check if shutdown has been initiated."""
        return self._shutdown_event.is_set()
    
    def _use_sync_lock(self, method_name: str = "unknown"):
        """Context manager for sync operations - use sparingly and only for quick operations."""
        return self._sync_lock
        
    def register_agent(self, agent_id: str, capabilities: List[str], overwrite: bool = False) -> None:
        """Register a new agent with the shared state."""
        if not agent_id or not isinstance(agent_id, str):
            raise ValueError("Agent ID must be a non-empty string")
        if not isinstance(capabilities, list):
            raise ValueError("Capabilities must be a list")
            
        with self._lock:
            if agent_id in self._agents and not overwrite:
                print(f"Warning: Agent {agent_id} already registered. Use overwrite=True to replace.")
                return
                
            self._agents[agent_id] = AgentState(
                agent_id=agent_id,
                status=AgentStatus.IDLE,
                current_task=None,
                progress=0.0,
                last_update=datetime.now(),
                capabilities=capabilities,
                metadata={}
            )
            self._message_queue[agent_id] = []
            print(f"✅ Agent {agent_id} registered with capabilities: {capabilities}")
    
    def update_agent_status(self, agent_id: str, status: AgentStatus, 
                           current_task: Optional[str] = None, 
                           progress: float = None,
                           metadata: Dict[str, Any] = None) -> None:
        """Update agent status and notify other agents."""
        with self._lock:
            if agent_id not in self._agents:
                raise ValueError(f"Agent {agent_id} not registered")
            
            agent = self._agents[agent_id]
            agent.status = status
            agent.last_update = datetime.now()
            
            if current_task is not None:
                agent.current_task = current_task
            if progress is not None:
                agent.progress = progress
            if metadata is not None:
                agent.metadata.update(metadata)
            
            # Broadcast status update
            self._broadcast_message(
                from_agent=agent_id,
                message_type=MessageType.STATUS_UPDATE,
                content={
                    "status": status.value,
                    "current_task": current_task,
                    "progress": progress,
                    "metadata": metadata or {}
                }
            )
    
    def create_project(self, name: str, description: str, requirements: List[str]) -> str:
        """Create a new project and return its ID."""
        if not name or not isinstance(name, str):
            raise ValueError("Project name must be a non-empty string")
        if not isinstance(description, str):
            raise ValueError("Project description must be a string")
        if not isinstance(requirements, list):
            raise ValueError("Requirements must be a list")
            
        with self._lock:
            project_id = str(uuid.uuid4())
            try:
                self._projects[project_id] = ProjectState(
                    project_id=project_id,
                    name=name,
                    description=description,
                    requirements=requirements,
                    current_phase="planning",
                    progress=0.0,
                    files_created={},
                    architecture_decisions=[],
                    test_results={},
                    security_findings=[],
                    performance_metrics={},
                    documentation={},
                    deployment_config={},
                    project_path=None  # Will be set when Flutter project is created
                )
                self._current_project_id = project_id
                
                # Notify all agents about new project
                try:
                    self._broadcast_message(
                        from_agent="system",
                        message_type=MessageType.STATE_SYNC,
                        content={
                            "event": "project_created",
                            "project_id": project_id,
                            "project": asdict(self._projects[project_id])
                        }
                    )
                except Exception as e:
                    print(f"Warning: Failed to broadcast project creation: {e}")
                
                return project_id
            except Exception as e:
                # Cleanup on failure
                if project_id in self._projects:
                    del self._projects[project_id]
                if self._current_project_id == project_id:
                    self._current_project_id = None
                raise RuntimeError(f"Failed to create project: {e}") from e
    
    def create_project_with_id(self, project_id: str, name: str, description: str, requirements: List[str]) -> None:
        """Create a new project with a specific ID."""
        with self._lock:
            self._projects[project_id] = ProjectState(
                project_id=project_id,
                name=name,
                description=description,
                requirements=requirements,
                current_phase="planning",
                progress=0.0,
                files_created={},
                architecture_decisions=[],
                test_results={},
                security_findings=[],
                performance_metrics={},
                documentation={},
                deployment_config={},
                project_path=None  # Will be set when Flutter project is created
            )
            self._current_project_id = project_id
            
            # Notify all agents about new project
            self._broadcast_message(
                from_agent="system",
                message_type=MessageType.STATE_SYNC,
                content={
                    "event": "project_created",
                    "project_id": project_id,
                    "project": asdict(self._projects[project_id])
                }
            )
    
    def update_project(self, project_id: str, **updates) -> None:
        """Update project state."""
        with self._lock:
            if project_id not in self._projects:
                raise ValueError(f"Project {project_id} not found")
            
            project = self._projects[project_id]
            for key, value in updates.items():
                if hasattr(project, key):
                    setattr(project, key, value)
            
            # Notify agents about project update
            self._broadcast_message(
                from_agent="system",
                message_type=MessageType.STATE_SYNC,
                content={
                    "event": "project_updated",
                    "project_id": project_id,
                    "updates": updates
                }
            )
    
    def add_file_to_project(self, project_id: str, filename: str, content: str) -> None:
        """Add a file to the project."""
        with self._lock:
            if project_id not in self._projects:
                raise ValueError(f"Project {project_id} not found")
            
            self._projects[project_id].files_created[filename] = content
            
            self._broadcast_message(
                from_agent="system",
                message_type=MessageType.STATE_SYNC,
                content={
                    "event": "file_added",
                    "project_id": project_id,
                    "filename": filename
                }
            )
    
    def add_project_file(self, project_id: str, filename: str, content: str) -> None:
        """Alias for add_file_to_project for test compatibility."""
        return self.add_file_to_project(project_id, filename, content)
    
    def send_message(self, from_agent: str, to_agent: Optional[str], 
                    message_type: MessageType, content: Dict[str, Any],
                    priority: int = 1) -> str:
        """Send a message to specific agent or broadcast."""
        if not from_agent or not isinstance(from_agent, str):
            raise ValueError("from_agent must be a non-empty string")
        if not isinstance(message_type, MessageType):
            raise ValueError("message_type must be a MessageType enum value")
        if not isinstance(content, dict):
            raise ValueError("content must be a dictionary")
        if not isinstance(priority, int) or priority < 1 or priority > 5:
            raise ValueError("priority must be an integer between 1 and 5")
            
        message = AgentMessage(
            id=str(uuid.uuid4()),
            from_agent=from_agent,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            timestamp=datetime.now(),
            priority=priority
        )
        
        with self._lock:
            try:
                self._messages.append(message)
                # Clean up old messages if we exceed the limit
                if len(self._messages) > self._max_messages:
                    self._messages = self._messages[-self._max_messages:]
                max_per_agent = 100
                if to_agent:
                    # Direct message
                    if to_agent in self._message_queue:
                        self._message_queue[to_agent].append(message)
                        # Always trim to last 100 messages
                        if len(self._message_queue[to_agent]) > max_per_agent:
                            self._message_queue[to_agent] = self._message_queue[to_agent][-max_per_agent:]
                    else:
                        # Less noisy logging for missing agents, especially supervision
                        if to_agent == "supervision":
                            # Silently drop supervision messages if agent not registered
                            pass
                        else:
                            print(f"Warning: Target agent {to_agent} not registered, message not delivered")
                else:
                    # Broadcast to all agents except sender
                    for agent_id in self._message_queue:
                        if agent_id != from_agent:
                            try:
                                self._message_queue[agent_id].append(message)
                                # Always trim to last 100 messages
                                if len(self._message_queue[agent_id]) > max_per_agent:
                                    self._message_queue[agent_id] = self._message_queue[agent_id][-max_per_agent:]
                            except Exception as e:
                                print(f"Warning: Failed to deliver message to agent {agent_id}: {e}")
                
                return message.id
            except Exception as e:
                print(f"Error sending message: {e}")
                raise RuntimeError(f"Failed to send message: {e}") from e
    
    def get_messages(self, agent_id: str, mark_read: bool = True, limit: int = None) -> List[AgentMessage]:
        """Get messages for a specific agent."""
        with self._lock:
            if agent_id not in self._message_queue:
                return []
            
            messages = self._message_queue[agent_id].copy()
            if mark_read:
                self._message_queue[agent_id].clear()
            
            # Sort by priority (high first) and timestamp (newest first)
            sorted_messages = sorted(messages, key=lambda m: (-m.priority, -m.timestamp.timestamp()))
            
            if limit is not None:
                sorted_messages = sorted_messages[:limit]
                
            return sorted_messages
    
    def get_recent_messages(self, minutes: int = 10) -> List[AgentMessage]:
        """Get all messages from the last N minutes."""
        from datetime import timedelta
        
        with self._lock:
            cutoff_time = datetime.now() - timedelta(minutes=minutes)
            recent_messages = [
                msg for msg in self._messages 
                if msg.timestamp >= cutoff_time
            ]
            return recent_messages
    
    def get_project_state(self, project_id: Optional[str] = None) -> Optional[ProjectState]:
        """Get current project state."""
        with self._lock:
            pid = project_id or self._current_project_id
            return self._projects.get(pid) if pid else None
    
    def get_agent_states(self) -> Dict[str, AgentState]:
        """Get all agent states."""
        with self._lock:
            return self._agents.copy()
    
    def get_agent_state(self, agent_id: str) -> Optional[AgentState]:
        """Get specific agent state."""
        with self._lock:
            return self._agents.get(agent_id)
    
    def _broadcast_message(self, from_agent: str, message_type: MessageType, 
                          content: Dict[str, Any]) -> None:
        """Internal method to broadcast messages."""
        self.send_message(
            from_agent=from_agent,
            to_agent=None,  # Broadcast
            message_type=message_type,
            content=content
        )
    
    def subscribe_to_updates(self, agent_id: str, callback: Callable) -> None:
        """Subscribe to state updates."""
        with self._lock:
            if agent_id not in self._subscribers:
                self._subscribers[agent_id] = []
            self._subscribers[agent_id].append(callback)
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """Subscribe to specific event types."""
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)
    
    def _notify_subscribers(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notify all subscribers of an event."""
        with self._lock:
            if event_type in self._subscribers:
                for callback in self._subscribers[event_type]:
                    try:
                        callback(event_type, data)
                    except Exception as e:
                        print(f"Error notifying subscriber: {e}")
    
    def update_project_phase(self, project_id: str, phase: str) -> None:
        """Update project phase."""
        with self._lock:
            if project_id not in self._projects:
                raise ValueError(f"Project {project_id} not found")
            
            self._projects[project_id].current_phase = phase
            
            # Notify subscribers
            self._notify_subscribers("project_phase_changed", {
                "project_id": project_id,
                "new_phase": phase
            })
    
    def report_issue(self, project_id: str, issue_data: Dict[str, Any]) -> str:
        """Report a new issue found by an agent."""
        with self._lock:
            if project_id not in self._issues:
                self._issues[project_id] = []
            
            issue = IssueReport(
                issue_id=issue_data.get("id", f"issue_{len(self._issues[project_id]) + 1}"),
                project_id=project_id,
                reporter_agent=issue_data.get("reporter_agent", "unknown"),
                issue_type=issue_data.get("type", "general"),
                severity=issue_data.get("severity", "medium"),
                description=issue_data.get("description", ""),
                affected_files=issue_data.get("affected_files", []),
                fix_suggestions=issue_data.get("fix_suggestions", []),
                status="open",
                timestamp=datetime.now(),
                assigned_agent=issue_data.get("assigned_agent"),
                resolution_notes=None
            )
            
            self._issues[project_id].append(issue)
            
            # Notify all agents about the new issue
            self._broadcast_message(
                from_agent="shared_state",
                message_type=MessageType.STATUS_UPDATE,
                content={
                    "event": "issue_reported",
                    "project_id": project_id,
                    "issue": asdict(issue)
                }
            )
            
            return issue.issue_id
    
    def get_project_issues(self, project_id: str, status: str = None) -> List[IssueReport]:
        """Get all issues for a project, optionally filtered by status."""
        with self._lock:
            issues = self._issues.get(project_id, [])
            if status:
                return [issue for issue in issues if issue.status == status]
            return issues
    
    def update_issue_status(self, project_id: str, issue_id: str, status: str, 
                           assigned_agent: str = None, resolution_notes: str = None) -> bool:
        """Update the status of an issue."""
        with self._lock:
            issues = self._issues.get(project_id, [])
            for issue in issues:
                if issue.issue_id == issue_id:
                    issue.status = status
                    if assigned_agent:
                        issue.assigned_agent = assigned_agent
                    if resolution_notes:
                        issue.resolution_notes = resolution_notes
                    
                    # Notify agents about issue status change
                    self._broadcast_message(
                        from_agent="shared_state",
                        message_type=MessageType.STATUS_UPDATE,
                        content={
                            "event": "issue_status_changed",
                            "project_id": project_id,
                            "issue_id": issue_id,
                            "new_status": status
                        }
                    )
                    return True
            return False

    def get_collaboration_context(self, requesting_agent: str) -> Dict[str, Any]:
        """Get collaboration context for an agent."""
        with self._lock:
            context = {
                "requesting_agent": requesting_agent,
                "timestamp": datetime.now(),
                "agents": {agent_id: asdict(agent_state) for agent_id, agent_state in self._agents.items()},
                "current_project": None,
                "recent_messages": []
            }
            
            # Add current project info
            if self._current_project_id and self._current_project_id in self._projects:
                context["current_project"] = asdict(self._projects[self._current_project_id])
            
            # Add recent messages for the requesting agent
            agent_messages = self.get_messages(requesting_agent, mark_read=False, limit=10)
            context["recent_messages"] = [asdict(msg) for msg in agent_messages]
            
            return context
    
    # Supervision state management methods
    def register_supervised_process(self, process_id: str, agent_id: str, task_type: str, 
                                   timeout_threshold: float) -> None:
        """Register a new process for supervision."""
        with self._lock:
            now = datetime.now()
            self._supervised_processes[process_id] = ProcessSupervisionState(
                process_id=process_id,
                agent_id=agent_id,
                task_type=task_type,
                start_time=now,
                last_heartbeat=now,
                timeout_threshold=timeout_threshold,
                status="running"
            )
    
    def update_process_heartbeat(self, process_id: str, cpu_usage: float = 0.0, 
                                memory_usage: float = 0.0) -> None:
        """Update process heartbeat and resource usage."""
        with self._lock:
            if process_id in self._supervised_processes:
                process = self._supervised_processes[process_id]
                process.last_heartbeat = datetime.now()
                process.cpu_usage = cpu_usage
                process.memory_usage = memory_usage
    
    def get_supervised_processes(self) -> Dict[str, ProcessSupervisionState]:
        """Get all supervised processes."""
        with self._lock:
            return self._supervised_processes.copy()
    
    def get_stuck_processes(self, stuck_threshold: int = 120) -> List[ProcessSupervisionState]:
        """Get processes that appear stuck."""
        with self._lock:
            stuck = []
            now = datetime.now()
            for process in self._supervised_processes.values():
                if process.status == "running":
                    time_since_heartbeat = (now - process.last_heartbeat).total_seconds()
                    if time_since_heartbeat > stuck_threshold:
                        stuck.append(process)
            return stuck
    
    def get_timeout_processes(self) -> List[ProcessSupervisionState]:
        """Get processes that have exceeded their timeout threshold."""
        with self._lock:
            timeout = []
            now = datetime.now()
            for process in self._supervised_processes.values():
                if process.status == "running":
                    elapsed = (now - process.start_time).total_seconds()
                    if elapsed > process.timeout_threshold:
                        timeout.append(process)
            return timeout
    
    def mark_process_completed(self, process_id: str) -> None:
        """Mark a process as completed."""
        with self._lock:
            if process_id in self._supervised_processes:
                self._supervised_processes[process_id].status = "completed"
    
    def mark_process_failed(self, process_id: str, reason: str = "") -> None:
        """Mark a process as failed."""
        with self._lock:
            if process_id in self._supervised_processes:
                self._supervised_processes[process_id].status = "failed"
                # Log to project if available
                if self._current_project_id and self._current_project_id in self._projects:
                    project = self._projects[self._current_project_id]
                    project.failed_processes.append(f"{process_id}: {reason}")
    
    def increment_process_intervention(self, process_id: str) -> None:
        """Increment intervention count for a process."""
        with self._lock:
            if process_id in self._supervised_processes:
                self._supervised_processes[process_id].intervention_count += 1
    
    def start_e2e_testing_session(self, session_id: str, project_id: str, 
                                 platforms: List[str]) -> None:
        """Start a new E2E testing session."""
        with self._lock:
            self._e2e_testing_sessions[session_id] = E2ETestingState(
                test_session_id=session_id,
                project_id=project_id,
                platforms_tested=platforms,
                test_results={},
                overall_status="running",
                start_time=datetime.now()
            )
    
    def update_e2e_test_result(self, session_id: str, platform: str, 
                              results: Dict[str, Any]) -> None:
        """Update E2E test results for a platform."""
        with self._lock:
            if session_id in self._e2e_testing_sessions:
                session = self._e2e_testing_sessions[session_id]
                session.test_results[platform] = results
    
    def complete_e2e_testing_session(self, session_id: str, overall_status: str) -> None:
        """Complete an E2E testing session."""
        with self._lock:
            if session_id in self._e2e_testing_sessions:
                session = self._e2e_testing_sessions[session_id]
                session.overall_status = overall_status
                session.end_time = datetime.now()
                
                # Update project state
                if session.project_id in self._projects:
                    project = self._projects[session.project_id]
                    project.e2e_test_results = {
                        "session_id": session_id,
                        "status": overall_status,
                        "platforms": session.test_results,
                        "completed_at": session.end_time.isoformat()
                    }
    
    def get_incremental_state(self, project_id: str) -> Optional[IncrementalImplementationState]:
        """Get incremental implementation state for a project."""
        with self._lock:
            return self._incremental_states.get(project_id)
    
    def initialize_incremental_implementation(self, project_id: str, 
                                            feature_queue: List[Dict[str, Any]]) -> None:
        """Initialize incremental implementation for a project."""
        with self._lock:
            self._incremental_states[project_id] = IncrementalImplementationState(
                feature_queue=feature_queue,
                current_feature=None,
                completed_features=[],
                failed_features=[],
                feature_dependencies={},
                rollback_points={},
                validation_results={}
            )
    
    def start_feature_implementation(self, project_id: str, feature: Dict[str, Any]) -> None:
        """Start implementing a specific feature."""
        with self._lock:
            if project_id in self._incremental_states:
                state = self._incremental_states[project_id]
                state.current_feature = feature
    
    def complete_feature_implementation(self, project_id: str, feature_id: str, 
                                      success: bool, rollback_point: str = None) -> None:
        """Complete feature implementation."""
        with self._lock:
            if project_id in self._incremental_states:
                state = self._incremental_states[project_id]
                if success:
                    state.completed_features.append(feature_id)
                    if rollback_point:
                        state.rollback_points[feature_id] = rollback_point
                else:
                    state.failed_features.append(feature_id)
                state.current_feature = None

    # Real-time awareness methods
    def subscribe_agent_to_all(self, agent_id: str) -> None:
        """Subscribe an agent to all other agents' status updates."""
        with self._lock:
            if agent_id not in self._awareness_state.agent_subscriptions:
                self._awareness_state.agent_subscriptions[agent_id] = []
            
            # Subscribe to all existing agents
            for other_agent_id in self._agents.keys():
                if other_agent_id != agent_id:
                    if other_agent_id not in self._awareness_state.agent_subscriptions[agent_id]:
                        self._awareness_state.agent_subscriptions[agent_id].append(other_agent_id)
            
            # Initialize activity stream
            if agent_id not in self._awareness_state.agent_activity_streams:
                self._awareness_state.agent_activity_streams[agent_id] = []
    
    def broadcast_agent_activity(self, event: AgentActivityEvent) -> None:
        """Broadcast an agent activity event to all subscribed agents - COMPLETELY DISABLED to prevent loops."""
        # COMPLETELY DISABLED: Real-time activity broadcasting was causing endless loops
        # that prevent actual task execution. Only enable for specific debug purposes.
        if not self._broadcast_enabled:
            return
            
        # Skip all broadcasts except absolutely critical file creation events
        if event.activity_type not in ["file_created"]:
            return
            
        # Log the activity locally but don't broadcast
        self.logger.debug(f"Activity logged (not broadcasted): {event.agent_id} -> {event.activity_type}")
        return
    
    def _detect_collaboration_opportunities(self, event: AgentActivityEvent) -> None:
        """Detect proactive collaboration opportunities based on activity events."""
        try:
            # Look for patterns that suggest collaboration opportunities
            opportunity_type = self._classify_collaboration_opportunity(event)
            
            if opportunity_type:
                opportunity = {
                    "id": str(uuid.uuid4()),
                    "type": opportunity_type,
                    "source_event": asdict(event),
                    "detected_at": datetime.now().isoformat(),
                    "priority": self._calculate_opportunity_priority(event),
                    "details": self._generate_opportunity_details(event, opportunity_type)
                }
                
                # Add to opportunities list
                self._awareness_state.proactive_opportunities.append(opportunity)
                
                # Broadcast opportunity to relevant agents
                self._broadcast_collaboration_opportunity(opportunity)
                
        except Exception as e:
            print(f"Error detecting collaboration opportunities: {e}")
    
    def _classify_collaboration_opportunity(self, event: AgentActivityEvent) -> Optional[str]:
        """Classify the type of collaboration opportunity."""
        activity_type = event.activity_type
        agent_id = event.agent_id
        
        # Architecture decisions → Implementation preparation
        if agent_id == "architecture" and "decision" in activity_type:
            return "architecture_to_implementation"
        
        # Code generation → Testing preparation
        elif agent_id == "implementation" and "code" in activity_type:
            return "implementation_to_testing"
        
        # Security findings → Testing and implementation updates
        elif agent_id == "security" and "issue" in activity_type:
            return "security_to_multi_agent"
        
        # Performance issues → Optimization opportunities
        elif agent_id == "performance" and "issue" in activity_type:
            return "performance_to_optimization"
        
        # Testing failures → Implementation fixes
        elif agent_id == "testing" and "failure" in activity_type:
            return "testing_to_implementation"
        
        return None
    
    def _calculate_opportunity_priority(self, event: AgentActivityEvent) -> str:
        """Calculate priority of collaboration opportunity."""
        if event.impact_level == "critical":
            return "high"
        elif event.impact_level == "high":
            return "medium"
        else:
            return "low"
    
    def _generate_opportunity_details(self, event: AgentActivityEvent, opportunity_type: str) -> Dict[str, Any]:
        """Generate detailed information about the collaboration opportunity."""
        details = {
            "source_agent": event.agent_id,
            "activity_details": event.activity_details,
            "suggested_action": "",
            "target_agents": [],
            "expected_outcome": ""
        }
        
        if opportunity_type == "architecture_to_implementation":
            details.update({
                "suggested_action": "prepare_implementation_structure",
                "target_agents": ["implementation"],
                "expected_outcome": "faster_implementation_start"
            })
        
        elif opportunity_type == "implementation_to_testing":
            details.update({
                "suggested_action": "prepare_test_suite",
                "target_agents": ["testing"],
                "expected_outcome": "immediate_test_coverage"
            })
        
        elif opportunity_type == "security_to_multi_agent":
            details.update({
                "suggested_action": "address_security_concern",
                "target_agents": ["implementation", "testing"],
                "expected_outcome": "enhanced_security_posture"
            })
        
        return details
    
    def _broadcast_collaboration_opportunity(self, opportunity: Dict[str, Any]) -> None:
        """Broadcast collaboration opportunity to relevant agents."""
        target_agents = opportunity.get("details", {}).get("target_agents", [])
        
        for agent_id in target_agents:
            if agent_id in self._agents:
                self.send_message(
                    from_agent="shared_consciousness",
                    to_agent=agent_id,
                    message_type=MessageType.PROACTIVE_ASSISTANCE_OFFER,
                    content=opportunity
                )
    
    def update_shared_consciousness(self, key: str, value: Any) -> None:
        """Update the shared consciousness with new insights."""
        with self._lock:
            self._awareness_state.shared_consciousness[key] = {
                "value": value,
                "updated_at": datetime.now().isoformat(),
                "update_count": self._awareness_state.shared_consciousness.get(key, {}).get("update_count", 0) + 1
            }
    
    def get_shared_consciousness(self, key: str = None) -> Any:
        """Get shared consciousness data."""
        with self._lock:
            if key:
                return self._awareness_state.shared_consciousness.get(key)
            return self._awareness_state.shared_consciousness.copy()
    
    def _get_relevant_consciousness_for_agent(self, agent_id: str) -> Dict[str, Any]:
        """Get consciousness data relevant to a specific agent."""
        agent_capabilities = self._agents.get(agent_id, AgentState("", AgentStatus.IDLE, "", 0.0, datetime.now(), [], {})).capabilities
        
        relevant_consciousness = {}
        for key, data in self._awareness_state.shared_consciousness.items():
            # Include consciousness data relevant to agent's capabilities
            if any(capability in key for capability in agent_capabilities):
                relevant_consciousness[key] = data
            # Always include project-wide insights
            elif "project_" in key or "global_" in key:
                relevant_consciousness[key] = data
        
        return relevant_consciousness
    
    def get_current_project_id(self) -> Optional[str]:
        """Get the current project ID."""
        with self._lock:
            return self._current_project_id
    
    def get_messages_for_agent(self, agent_id: str) -> List[AgentMessage]:
        """Get unread messages for an agent (alias for get_messages)."""
        return self.get_messages(agent_id, mark_read=False, limit=50)
    
    def get_collaboration_opportunities(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get collaboration opportunities relevant to an agent."""
        with self._lock:
            agent_capabilities = self._agents.get(agent_id, AgentState("", AgentStatus.IDLE, "", 0.0, datetime.now(), [], {})).capabilities
            
            relevant_opportunities = []
            for opportunity in self._awareness_state.proactive_opportunities:
                target_agents = opportunity.get("details", {}).get("target_agents", [])
                
                # Include if agent is directly targeted or has relevant capabilities
                if agent_id in target_agents or any(capability in str(opportunity) for capability in agent_capabilities):
                    relevant_opportunities.append(opportunity)
            
            return relevant_opportunities
    
    def accept_collaboration_opportunity(self, agent_id: str, opportunity_id: str) -> bool:
        """Mark a collaboration opportunity as accepted by an agent."""
        with self._lock:
            for opportunity in self._awareness_state.proactive_opportunities:
                if opportunity.get("id") == opportunity_id:
                    if "accepted_by" not in opportunity:
                        opportunity["accepted_by"] = []
                    opportunity["accepted_by"].append({
                        "agent_id": agent_id,
                        "accepted_at": datetime.now().isoformat()
                    })
                    return True
            return False
    
    def get_agent_activity_stream(self, agent_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activity stream for an agent."""
        with self._lock:
            activities = self._awareness_state.agent_activity_streams.get(agent_id, [])
            return activities[-limit:] if limit else activities

    # Predictive assistance capabilities
    def generate_predictive_insights(self, agent_id: str) -> List[Dict[str, Any]]:
        """Generate predictive insights for an agent based on current state and patterns."""
        # Add busy check to prevent spam
        agent_state = self.get_agent_state(agent_id)
        if agent_state and agent_state.status != AgentStatus.IDLE:
            return []  # Don't predict if agent is busy
        
        with self._lock:
            insights = []
            
            try:
                # Analyze current project state
                if self._current_project_id and self._current_project_id in self._projects:
                    project = self._projects[self._current_project_id]
                    
                    # Predict next likely actions based on current phase
                    phase_insights = self._predict_from_project_phase(project, agent_id)
                    insights.extend(phase_insights)
                    
                    # Analyze peer agent patterns
                    peer_insights = self._predict_from_peer_patterns(agent_id)
                    insights.extend(peer_insights)
                    
                    # Check for recurring collaboration patterns
                    collaboration_insights = self._predict_collaboration_needs(agent_id)
                    insights.extend(collaboration_insights)
                    
                    # Update stored insights
                    if agent_id not in self._awareness_state.predictive_insights:
                        self._awareness_state.predictive_insights[agent_id] = []
                    
                    # Add new insights with timestamp
                    for insight in insights:
                        insight["generated_at"] = datetime.now().isoformat()
                        insight["confidence"] = self._calculate_insight_confidence(insight)
                    
                    self._awareness_state.predictive_insights[agent_id] = insights[-10:]  # Keep last 10
                    
            except Exception as e:
                print(f"Error generating predictive insights: {e}")
                
            return insights

    def _predict_from_project_phase(self, project: ProjectState, agent_id: str) -> List[Dict[str, Any]]:
        """Predict next actions based on current project phase."""
        insights = []
        current_phase = project.current_phase
        
        if current_phase == "planning" and agent_id == "architecture":
            insights.append({
                "type": "phase_transition",
                "prediction": "architecture_design_needed",
                "description": "Project in planning phase, architecture design likely needed soon",
                "suggested_action": "prepare_architecture_analysis",
                "priority": "high"
            })
        
        elif current_phase == "architecture" and agent_id == "implementation":
            insights.append({
                "type": "phase_transition", 
                "prediction": "implementation_start_upcoming",
                "description": "Architecture phase active, implementation phase likely next",
                "suggested_action": "prepare_implementation_structure",
                "priority": "medium"
            })
        
        elif current_phase == "implementation" and agent_id == "testing":
            insights.append({
                "type": "phase_transition",
                "prediction": "testing_phase_approaching",
                "description": "Implementation in progress, testing will be needed",
                "suggested_action": "prepare_test_infrastructure",
                "priority": "medium"
            })
        
        return insights

    def _predict_from_peer_patterns(self, agent_id: str) -> List[Dict[str, Any]]:
        """Predict actions based on peer agent activity patterns."""
        insights = []
        
        try:
            # Analyze recent activities from all agents
            recent_activities = []
            for peer_id, activities in self._awareness_state.agent_activity_streams.items():
                if peer_id != agent_id:
                    recent_activities.extend(activities[-5:])  # Last 5 activities per peer
            
            # Sort by timestamp
            recent_activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            # Look for patterns that suggest upcoming work
            for activity in recent_activities[:10]:  # Check last 10 activities
                activity_type = activity.get("activity_type", "")
                source_agent = activity.get("agent_id", "")
                
                # Architecture decisions → Implementation preparation  
                if source_agent == "architecture" and "decision" in activity_type and agent_id == "implementation":
                    insights.append({
                        "type": "peer_pattern",
                        "prediction": "implementation_work_incoming",
                        "description": f"Architecture decisions made, implementation work likely needed",
                        "trigger_activity": activity_type,
                        "suggested_action": "review_architecture_decisions",
                        "priority": "medium"
                    })
                
                # Code generation → Testing needed
                elif source_agent == "implementation" and "code" in activity_type and agent_id == "testing":
                    insights.append({
                        "type": "peer_pattern",
                        "prediction": "testing_work_needed",
                        "description": f"Code generated, testing work will be needed",
                        "trigger_activity": activity_type,
                        "suggested_action": "prepare_test_cases",
                        "priority": "medium"
                    })
                
                # Security issues → Multiple agent response
                elif source_agent == "security" and "issue" in activity_type and agent_id in ["implementation", "testing"]:
                    insights.append({
                        "type": "peer_pattern",
                        "prediction": "security_response_needed",
                        "description": f"Security issue detected, response likely needed",
                        "trigger_activity": activity_type,
                        "suggested_action": "review_security_findings",
                        "priority": "high"
                    })
                
        except Exception as e:
            print(f"Error predicting from peer patterns: {e}")
            
        return insights

    def _predict_collaboration_needs(self, agent_id: str) -> List[Dict[str, Any]]:
        """Predict collaboration needs based on historical patterns."""
        insights = []
        
        try:
            # Check for common collaboration patterns
            agent_capabilities = self._agents.get(agent_id, AgentState("", AgentStatus.IDLE, "", 0.0, datetime.now(), [], {})).capabilities
            
            # Look at recent collaboration opportunities
            recent_opportunities = self._awareness_state.proactive_opportunities[-5:]
            
            collaboration_frequency = {}
            for opportunity in recent_opportunities:
                target_agents = opportunity.get("details", {}).get("target_agents", [])
                for target in target_agents:
                    if target != agent_id:
                        collaboration_frequency[target] = collaboration_frequency.get(target, 0) + 1
            
            # Predict high-frequency collaborations
            for collaborator, frequency in collaboration_frequency.items():
                if frequency >= 2:  # If collaborated 2+ times recently
                    insights.append({
                        "type": "collaboration_pattern",
                        "prediction": "frequent_collaboration_likely",
                        "description": f"High collaboration frequency with {collaborator}",
                        "collaborator": collaborator,
                        "frequency": frequency,
                        "suggested_action": "monitor_collaborator_activities",
                        "priority": "low"
                    })
            
        except Exception as e:
            print(f"Error predicting collaboration needs: {e}")
            
        return insights

    def _calculate_insight_confidence(self, insight: Dict[str, Any]) -> float:
        """Calculate confidence score for a predictive insight."""
        insight_type = insight.get("type", "")
        priority = insight.get("priority", "low")
        
        base_confidence = 0.5
        
        # Adjust based on insight type
        if insight_type == "phase_transition":
            base_confidence = 0.8  # Phase transitions are highly predictable
        elif insight_type == "peer_pattern":
            base_confidence = 0.7  # Peer patterns are fairly predictable
        elif insight_type == "collaboration_pattern":
            base_confidence = 0.6  # Collaboration patterns are moderately predictable
        
        # Adjust based on priority
        if priority == "high":
            base_confidence += 0.1
        elif priority == "low":
            base_confidence -= 0.1
        
        return min(1.0, max(0.0, base_confidence))

    def get_predictive_insights(self, agent_id: str) -> List[Dict[str, Any]]:
        """Get stored predictive insights for an agent."""
        with self._lock:
            return self._awareness_state.predictive_insights.get(agent_id, [])

    def update_real_time_metrics(self, metric_name: str, value: Any) -> None:
        """Update real-time awareness metrics."""
        with self._lock:
            self._awareness_state.real_time_metrics[metric_name] = {
                "value": value,
                "updated_at": datetime.now().isoformat()
            }

    def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get all real-time awareness metrics."""
        with self._lock:
            return self._awareness_state.real_time_metrics.copy()

    def create_proactive_assistance_offer(self, offering_agent: str, target_agent: str, 
                                        assistance_type: str, details: Dict[str, Any]) -> str:
        """Create a proactive assistance offer."""
        with self._lock:
            offer_id = str(uuid.uuid4())
            
            offer = {
                "id": offer_id,
                "offering_agent": offering_agent,
                "target_agent": target_agent,
                "assistance_type": assistance_type,
                "details": details,
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            }
            
            # Send proactive assistance message
            self.send_message(
                from_agent=offering_agent,
                to_agent=target_agent,
                message_type=MessageType.PROACTIVE_ASSISTANCE_OFFER,
                content=offer
            )
            
            return offer_id
    
    def _broadcast_real_time_update(self, event: AgentActivityEvent) -> None:
        """Broadcast real-time update to all relevant agents with rate limiting."""
        try:
            # Rate limiting: track broadcast frequency
            current_time = time.time()
            broadcast_key = f"{event.agent_id}_{event.activity_type}"
            
            if not hasattr(self, '_broadcast_timestamps'):
                self._broadcast_timestamps = {}
            
            last_broadcast = self._broadcast_timestamps.get(broadcast_key, 0)
            
            # Apply rate limiting based on activity type
            if event.activity_type in ["status_change", "predictive_preparation", "monitoring"]:
                min_interval = 15.0  # 15 seconds for frequent activities
            else:
                min_interval = 5.0   # 5 seconds for important activities
            
            if current_time - last_broadcast < min_interval:
                # Skip broadcast to prevent spam
                return
            
            # Only broadcast truly important activities
            important_activities = {
                "file_created", "task_completed", "error_detected", 
                "architecture_decision", "feature_completed", "test_passed",
                "project_structure_created"
            }
            
            if event.activity_type not in important_activities:
                # Skip non-critical activities to reduce noise
                return
            
            # Find agents interested in this type of activity
            interested_agents = set()
            
            # All agents get critical events
            if event.impact_level == "critical":
                interested_agents.update(self._agents.keys())
            else:
                # Find agents subscribed to this agent or interested in this activity type
                for agent_id, subscriptions in self._awareness_state.agent_subscriptions.items():
                    if event.agent_id in subscriptions:
                        interested_agents.add(agent_id)
                    
                    # Check if agent type is relevant
                    if agent_id in self._agents:
                        agent_capabilities = self._agents[agent_id].capabilities
                        if any(capability in event.collaboration_relevance for capability in agent_capabilities):
                            interested_agents.add(agent_id)
            
            # Remove the source agent
            interested_agents.discard(event.agent_id)
            
            # Limit to maximum 3 agents to prevent broadcast storms
            if len(interested_agents) > 3:
                interested_agents = set(list(interested_agents)[:3])
            
            # Send real-time updates
            for agent_id in interested_agents:
                self.send_message(
                    from_agent="shared_consciousness",
                    to_agent=agent_id,
                    message_type=MessageType.REAL_TIME_STATUS_BROADCAST,
                    content={
                        "event": asdict(event),
                        "consciousness_update": self._get_relevant_consciousness_for_agent(agent_id),
                        "timestamp": datetime.now().isoformat()
                    }
                )
            
            # Update broadcast timestamp
            self._broadcast_timestamps[broadcast_key] = current_time
            
        except Exception as e:
            print(f"Error in broadcast_real_time_update: {e}")
    
    def broadcast_project_status(self, project_id: str) -> None:
        """Broadcast project status to all agents."""
        try:
            project = self.get_project_state(project_id)
            if not project:
                print(f"Warning: Project {project_id} not found for status broadcast")
                return
                
            self._broadcast_message(
                from_agent="system",
                message_type=MessageType.STATE_SYNC,
                content={
                    "event": "project_status_broadcast",
                    "project_id": project_id,
                    "project": asdict(project),
                    "timestamp": datetime.now().isoformat()
                }
            )
        except Exception as e:
            print(f"Error broadcasting project status: {e}")

    async def async_send_message(self, from_agent: str, to_agent: Optional[str], 
                                message_type: MessageType, content: Dict[str, Any],
                                priority: int = 1) -> str:
        """Async version of send_message for use in async contexts."""
        # For async safety, we can use the regular send_message since it's thread-safe
        # but we provide this method for consistency in async codebases
        return self.send_message(from_agent, to_agent, message_type, content, priority)
    
    async def async_update_agent_status(self, agent_id: str, status: AgentStatus, 
                                       current_task: Optional[str] = None, 
                                       progress: float = None,
                                       metadata: Dict[str, Any] = None) -> None:
        """Async version of update_agent_status."""
        self.update_agent_status(agent_id, status, current_task, progress, metadata)
    
    async def async_broadcast_agent_activity(self, event: AgentActivityEvent) -> None:
        """Async version of broadcast_agent_activity."""
        # Get the async lock for thread safety in async contexts
        async_lock = await self._get_async_lock()
        async with async_lock:
            # Call the synchronous version which has all the logic
            self.broadcast_agent_activity(event)

    async def update_project_async(self, project_id: str, **kwargs) -> None:
        """Thread-safe async version of update_project."""
        lock = await self._get_async_lock(f"project_{project_id}")
        async with lock:
            # Store the previous state for versioning
            current_state = self.get_project_state(project_id)
            if current_state:
                if project_id not in self._state_versions:
                    self._state_versions[project_id] = []
                self._state_versions[project_id].append(copy.deepcopy(current_state))
                if len(self._state_versions[project_id]) > 10:  # Keep last 10 versions
                    self._state_versions[project_id].pop(0)
            
            # Update the project state
            self.update_project(project_id, **kwargs)
            self._version_counter += 1
    
    def rollback_state(self, project_id: str, version_index: int = -1) -> bool:
        """Rollback to a previous state version."""
        if project_id in self._state_versions and self._state_versions[project_id]:
            try:
                previous_state = self._state_versions[project_id][version_index]
                # Replace current state with previous state
                self.update_project(project_id, **previous_state)
                return True
            except IndexError:
                return False
        return False
    
    def validate_state_update(self, update_data: Dict[str, Any]) -> bool:
        """Validate state update data before applying."""
        # Basic validation - could be expanded based on specific requirements
        if not isinstance(update_data, dict):
            return False
            
        # Check for required fields or other validation logic
        required_fields = ["project_id"]
        for field in required_fields:
            if field not in update_data:
                return False
                
        return True
    
    async def persist_state(self, filepath: str = "state_backup.json") -> bool:
        """Persist current state to a file."""
        import json
        try:
            lock = await self._get_async_lock("persist_state")
            async with lock:
                # Get all the data to persist
                data = {
                    "projects": self._projects,
                    "agents": self._agents,
                    "version": self._version_counter,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Write to file
                with open(filepath, 'w') as f:
                    json.dump(data, f)
                return True
        except Exception as e:
            print(f"Error persisting state: {e}")
            return False
    
    async def load_state(self, filepath: str = "state_backup.json") -> bool:
        """Load state from a file."""
        import json
        import os
        
        if not os.path.exists(filepath):
            return False
            
        try:
            lock = await self._get_async_lock("load_state")
            async with lock:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Restore state
                self._projects = data.get("projects", {})
                self._agents = data.get("agents", {})
                self._version_counter = data.get("version", 0)
                return True
        except Exception as e:
            print(f"Error loading state: {e}")
            return False

# Global shared state instance
shared_state = SharedState()
