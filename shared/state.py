"""
Shared state management for FlutterSwarm agents.
Provides real-time synchronization and communication between all agents.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum
import threading
from pydantic import BaseModel

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

class SharedState:
    """
    Central shared state manager for all agents.
    Provides real-time synchronization and communication.
    """
    
    def __init__(self):
        self._lock = threading.RLock()
        self._agents: Dict[str, AgentState] = {}
        self._projects: Dict[str, ProjectState] = {}
        self._messages: List[AgentMessage] = []
        self._message_queue: Dict[str, List[AgentMessage]] = {}
        self._subscribers: Dict[str, List[Callable]] = {}
        self._current_project_id: Optional[str] = None
        
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
            
            if to_agent:
                # Direct message
                if to_agent in self._message_queue:
                    self._message_queue[to_agent].append(message)
            else:
                # Broadcast to all agents except sender
                for agent_id in self._message_queue:
                    if agent_id != from_agent:
                        self._message_queue[agent_id].append(message)
        
        return message.id
    
    def get_messages(self, agent_id: str, mark_read: bool = True) -> List[AgentMessage]:
        """Get messages for a specific agent."""
        with self._lock:
            if agent_id not in self._message_queue:
                return []
            
            messages = self._message_queue[agent_id].copy()
            if mark_read:
                self._message_queue[agent_id].clear()
            
            return sorted(messages, key=lambda m: (m.priority, m.timestamp), reverse=True)
    
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
    
    def get_collaboration_context(self, requesting_agent: str) -> Dict[str, Any]:
        """Get full context for agent collaboration."""
        with self._lock:
            return {
                "agents": {aid: asdict(state) for aid, state in self._agents.items()},
                "current_project": asdict(self.get_project_state()) if self.get_project_state() else None,
                "recent_messages": [asdict(msg) for msg in self._messages[-10:]],
                "requesting_agent": requesting_agent,
                "timestamp": datetime.now().isoformat()
            }

# Global shared state instance
shared_state = SharedState()
