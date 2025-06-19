"""
Shared state management for FlutterSwarm agents.
Provides real-time synchronization and communication between all agents.
"""

import asyncio
import json
import uuid
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pydantic import BaseModel
from config.config_manager import get_config

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

class SharedState:
    """
    Central shared state manager for all agents.
    Provides real-time synchronization and communication.
    """
    
    def __init__(self):
        self._config = get_config()
        self._lock = threading.RLock()
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
        
        # Configure limits from config
        self._max_messages = self._config.get('communication.messaging.queue_size', 500)
        self._message_ttl = self._config.get('communication.messaging.message_ttl', 3600)
        self._max_collaborations = self._config.get('communication.collaboration.max_concurrent_collaborations', 5)
        
    def register_agent(self, agent_id: str, capabilities: List[str]) -> None:
        """Register a new agent with the shared state."""
        with self._lock:
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
        with self._lock:
            project_id = str(uuid.uuid4())
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
                deployment_config={}
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
            
            return project_id
    
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
                deployment_config={}
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
            self._messages.append(message)
            
            # Clean up old messages if we exceed the limit
            if len(self._messages) > self._max_messages:
                self._messages = self._messages[-self._max_messages:]
            
            if to_agent:
                # Direct message
                if to_agent in self._message_queue:
                    self._message_queue[to_agent].append(message)
                    # Clean up agent-specific queue
                    if len(self._message_queue[to_agent]) > self._max_messages:
                        self._message_queue[to_agent] = self._message_queue[to_agent][-self._max_messages:]
            else:
                # Broadcast to all agents except sender
                for agent_id in self._message_queue:
                    if agent_id != from_agent:
                        self._message_queue[agent_id].append(message)
                        # Clean up agent-specific queue
                        if len(self._message_queue[agent_id]) > self._max_messages:
                            self._message_queue[agent_id] = self._message_queue[agent_id][-self._max_messages:]
        
        return message.id
    
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

# Global shared state instance
shared_state = SharedState()
