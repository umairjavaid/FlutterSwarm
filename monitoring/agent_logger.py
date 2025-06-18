"""
Agent Logger for FlutterSwarm
Comprehensive logging system for tracking agent actions, tool usage, and system events.
"""

import logging
import json
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

from shared.state import shared_state, AgentStatus, MessageType


@dataclass
class LogEntry:
    """Represents a single log entry."""
    timestamp: datetime
    level: str
    agent_id: str
    event_type: str
    message: str
    data: Optional[Dict[str, Any]] = None
    tool_name: Optional[str] = None
    operation: Optional[str] = None
    execution_time: Optional[float] = None
    status: Optional[str] = None


class AgentLogger:
    """
    Comprehensive logging system for FlutterSwarm agents.
    Logs agent activities, tool usage, and system events with structured data.
    """
    
    def __init__(self, log_dir: str = "logs", enable_file_logging: bool = True):
        self.log_dir = Path(log_dir)
        self.enable_file_logging = enable_file_logging
        self.log_entries: List[LogEntry] = []
        
        # Session tracking
        self.session_start = datetime.now()
        self.session_id = self.session_start.strftime("%Y%m%d_%H%M%S")
        
        # Create log directory
        if self.enable_file_logging:
            self.log_dir.mkdir(exist_ok=True)
        
        # Setup logging
        self._setup_logging()
        
        self.logger.info(f"🐝 AgentLogger initialized - Session: {self.session_id}")
    
    def _setup_logging(self):
        """Setup the logging configuration."""
        # Create logger
        self.logger = logging.getLogger('FlutterSwarm')
        self.logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Console handler with colored output
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # File handler for detailed logs
        if self.enable_file_logging:
            log_file = self.log_dir / f"flutter_swarm_{self.session_id}.log"
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(logging.DEBUG)
            
            # Detailed file formatter
            file_formatter = logging.Formatter(
                '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        # Simple console formatter
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
    
    def log_agent_status_change(self, agent_id: str, old_status: AgentStatus, 
                               new_status: AgentStatus, task: Optional[str] = None,
                               metadata: Optional[Dict[str, Any]] = None):
        """Log agent status change."""
        message = f"Agent {agent_id} status: {old_status.value} → {new_status.value}"
        if task:
            message += f" (Task: {task})"
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level="INFO",
            agent_id=agent_id,
            event_type="status_change",
            message=message,
            data={
                "old_status": old_status.value,
                "new_status": new_status.value,
                "task": task,
                "metadata": metadata or {}
            }
        )
        
        self._add_log_entry(entry)
        self.logger.info(f"🔄 {message}")
    
    def log_tool_usage(self, agent_id: str, tool_name: str, operation: str,
                      status: str, execution_time: Optional[float] = None,
                      input_data: Optional[Dict[str, Any]] = None,
                      output_data: Optional[Dict[str, Any]] = None,
                      error: Optional[str] = None):
        """Log tool usage by an agent."""
        message = f"Agent {agent_id} used {tool_name}.{operation} - Status: {status}"
        if execution_time:
            message += f" ({execution_time:.2f}s)"
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level="DEBUG" if status == "success" else "WARNING",
            agent_id=agent_id,
            event_type="tool_usage",
            message=message,
            tool_name=tool_name,
            operation=operation,
            execution_time=execution_time,
            status=status,
            data={
                "input_data": input_data,
                "output_data": output_data,
                "error": error
            }
        )
        
        self._add_log_entry(entry)
        
        # Log to console with appropriate level
        if status == "success":
            self.logger.debug(f"🔧 {message}")
        else:
            self.logger.warning(f"⚠️ {message}")
            if error:
                self.logger.warning(f"   Error: {error}")
    
    def log_agent_collaboration(self, from_agent: str, to_agent: str,
                               collaboration_type: str, data: Dict[str, Any],
                               result: Optional[Dict[str, Any]] = None):
        """Log agent collaboration."""
        message = f"Collaboration: {from_agent} → {to_agent} ({collaboration_type})"
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level="INFO",
            agent_id=from_agent,
            event_type="collaboration",
            message=message,
            data={
                "to_agent": to_agent,
                "collaboration_type": collaboration_type,
                "request_data": data,
                "result": result
            }
        )
        
        self._add_log_entry(entry)
        self.logger.info(f"🤝 {message}")
    
    def log_project_event(self, project_id: str, event_type: str, 
                         description: str, data: Optional[Dict[str, Any]] = None):
        """Log project-level events."""
        message = f"Project {project_id}: {description}"
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level="INFO",
            agent_id="system",
            event_type=f"project_{event_type}",
            message=message,
            data={
                "project_id": project_id,
                "event_type": event_type,
                "data": data or {}
            }
        )
        
        self._add_log_entry(entry)
        self.logger.info(f"📁 {message}")
    
    def log_build_phase_change(self, project_id: str, old_phase: str, 
                              new_phase: str, progress: float):
        """Log build phase changes."""
        message = f"Build phase: {old_phase} → {new_phase} ({progress:.1%} complete)"
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level="INFO",
            agent_id="orchestrator",
            event_type="phase_change",
            message=message,
            data={
                "project_id": project_id,
                "old_phase": old_phase,
                "new_phase": new_phase,
                "progress": progress
            }
        )
        
        self._add_log_entry(entry)
        self.logger.info(f"🏗️ {message}")
    
    def log_error(self, agent_id: str, error_type: str, error_message: str,
                  context: Optional[Dict[str, Any]] = None, exception: Optional[Exception] = None):
        """Log errors and exceptions."""
        message = f"Error in {agent_id}: {error_type} - {error_message}"
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level="ERROR",
            agent_id=agent_id,
            event_type="error",
            message=message,
            data={
                "error_type": error_type,
                "error_message": error_message,
                "context": context or {},
                "exception": str(exception) if exception else None
            }
        )
        
        self._add_log_entry(entry)
        self.logger.error(f"❌ {message}")
        
        if exception and self.logger.isEnabledFor(logging.DEBUG):
            self.logger.exception(f"Exception details for {agent_id}")
    
    def log_message(self, from_agent: str, to_agent: str, message_type: MessageType,
                   content: Any, priority: int = 1):
        """Log inter-agent messages."""
        message = f"Message: {from_agent} → {to_agent} [{message_type.value}] (priority: {priority})"
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level="DEBUG",
            agent_id=from_agent,
            event_type="message",
            message=message,
            data={
                "to_agent": to_agent,
                "message_type": message_type.value,
                "content": content,
                "priority": priority
            }
        )
        
        self._add_log_entry(entry)
        self.logger.debug(f"💬 {message}")
    
    def log_performance_metric(self, agent_id: str, metric_name: str, 
                              value: float, unit: str = "",
                              context: Optional[Dict[str, Any]] = None):
        """Log performance metrics."""
        message = f"Performance: {agent_id}.{metric_name} = {value}{unit}"
        
        entry = LogEntry(
            timestamp=datetime.now(),
            level="DEBUG",
            agent_id=agent_id,
            event_type="performance",
            message=message,
            data={
                "metric_name": metric_name,
                "value": value,
                "unit": unit,
                "context": context or {}
            }
        )
        
        self._add_log_entry(entry)
        self.logger.debug(f"📊 {message}")
    
    def _add_log_entry(self, entry: LogEntry):
        """Add a log entry to the internal list."""
        self.log_entries.append(entry)
        
        # Keep only recent entries in memory (last 1000)
        if len(self.log_entries) > 1000:
            self.log_entries = self.log_entries[-1000:]
    
    def get_logs_for_agent(self, agent_id: str, limit: int = 100) -> List[LogEntry]:
        """Get recent logs for a specific agent."""
        agent_logs = [entry for entry in self.log_entries if entry.agent_id == agent_id]
        return agent_logs[-limit:]
    
    def get_logs_by_type(self, event_type: str, limit: int = 100) -> List[LogEntry]:
        """Get recent logs by event type."""
        type_logs = [entry for entry in self.log_entries if entry.event_type == event_type]
        return type_logs[-limit:]
    
    def get_recent_logs(self, limit: int = 100) -> List[LogEntry]:
        """Get recent logs."""
        return self.log_entries[-limit:]
    
    def export_logs_to_json(self, filename: Optional[str] = None) -> str:
        """Export logs to JSON file."""
        if not filename:
            filename = f"flutter_swarm_logs_{self.session_id}.json"
        
        filepath = self.log_dir / filename
        
        # Convert log entries to dictionaries
        logs_data = {
            "session_id": self.session_id,
            "session_start": self.session_start.isoformat(),
            "export_time": datetime.now().isoformat(),
            "total_entries": len(self.log_entries),
            "logs": [
                {
                    **asdict(entry),
                    "timestamp": entry.timestamp.isoformat()
                }
                for entry in self.log_entries
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(logs_data, f, indent=2, default=str)
        
        self.logger.info(f"📄 Logs exported to {filepath}")
        return str(filepath)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current session."""
        if not self.log_entries:
            return {"message": "No log entries found"}
        
        # Count entries by type
        event_counts = {}
        agent_counts = {}
        error_count = 0
        
        for entry in self.log_entries:
            event_counts[entry.event_type] = event_counts.get(entry.event_type, 0) + 1
            agent_counts[entry.agent_id] = agent_counts.get(entry.agent_id, 0) + 1
            if entry.level == "ERROR":
                error_count += 1
        
        return {
            "session_id": self.session_id,
            "session_duration": str(datetime.now() - self.session_start),
            "total_entries": len(self.log_entries),
            "error_count": error_count,
            "events_by_type": event_counts,
            "entries_by_agent": agent_counts,
            "session_start": self.session_start.isoformat(),
            "last_entry": self.log_entries[-1].timestamp.isoformat() if self.log_entries else None
        }


# Global logger instance
agent_logger = AgentLogger()
