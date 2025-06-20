"""
Build Monitor for FlutterSwarm
Monitors the entire Flutter app build process and coordinates logging and live display.
"""

import asyncio
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass

from shared.state import shared_state, AgentStatus, MessageType
from .agent_logger import agent_logger
from .live_display import live_display
from .progress_tracker import ProgressTracker


@dataclass
class BuildEvent:
    """Represents a build event."""
    timestamp: datetime
    project_id: str
    agent_id: str
    event_type: str
    description: str
    data: Optional[Dict[str, Any]] = None


class BuildMonitor:
    """
    Comprehensive build monitoring system that coordinates agent logging,
    live display, and progress tracking during Flutter app development.
    """
    
    def __init__(self, enable_live_display: bool = True, enable_logging: bool = True):
        self.enable_live_display = enable_live_display
        self.enable_logging = enable_logging
        
        # Components
        self.progress_tracker = ProgressTracker()
        
        # State
        self.is_monitoring = False
        self.current_project_id: Optional[str] = None
        self.monitoring_task: Optional[asyncio.Task] = None
        self.build_events: List[BuildEvent] = []
        
        # Callbacks
        self.event_callbacks: List[Callable[[BuildEvent], None]] = []
        
        # Statistics
        self.build_start_time: Optional[datetime] = None
        self.total_tool_calls = 0
        self.active_agents = set()
        
    def initialize_monitoring(self) -> None:
        """Initialize the monitoring system."""
        # Initialize components if needed
        self.build_events.clear()
        self.total_tool_calls = 0
        self.active_agents.clear()
        print("🔍 Build monitoring system initialized")
        
    def start_monitoring(self, project_id: str) -> None:
        """Start monitoring a Flutter build process."""
        if self.is_monitoring:
            self.stop_monitoring()
        
        self.current_project_id = project_id
        self.is_monitoring = True
        self.build_start_time = datetime.now()
        self.build_events.clear()
        self.total_tool_calls = 0
        self.active_agents.clear()
        
        # Start live display
        if self.enable_live_display:
            live_display.start()
        
        # Log build start
        if self.enable_logging:
            agent_logger.log_project_event(
                project_id, "build_start",
                f"Starting Flutter build monitoring for project {project_id}"
            )
        
        # Start monitoring task
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        self._emit_event("build_start", "Build monitoring started", {
            "project_id": project_id,
            "start_time": self.build_start_time.isoformat()
        })
        
        print(f"🔍 Build monitoring started for project: {project_id}")
    
    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return summary."""
        if not self.is_monitoring:
            return {}
        
        self.is_monitoring = False
        
        # Stop monitoring task
        if self.monitoring_task and not self.monitoring_task.done():
            self.monitoring_task.cancel()
        
        # Stop live display
        if self.enable_live_display:
            live_display.stop()
        
        # Calculate build summary
        build_duration = datetime.now() - self.build_start_time if self.build_start_time else None
        
        summary = {
            "project_id": self.current_project_id,
            "build_duration": str(build_duration) if build_duration else "Unknown",
            "total_events": len(self.build_events),
            "total_tool_calls": self.total_tool_calls,
            "active_agents": list(self.active_agents),
            "build_phases": self.progress_tracker.get_phase_summary(),
            "final_progress": self.progress_tracker.get_overall_progress()
        }
        
        # Log build completion
        if self.enable_logging:
            agent_logger.log_project_event(
                self.current_project_id or "unknown", "build_complete",
                f"Build monitoring completed", summary
            )
        
        self._emit_event("build_complete", "Build monitoring completed", summary)
        
        print(f"✅ Build monitoring completed. Duration: {build_duration}")
        
        return summary
    
    async def _monitoring_loop(self):
        """Main monitoring loop."""
        try:
            while self.is_monitoring:
                await self._update_monitoring_data()
                await asyncio.sleep(0.5)  # Update every 500ms
        except asyncio.CancelledError:
            pass
        except Exception as e:
            print(f"❌ Monitoring loop error: {e}")
            if self.enable_logging:
                agent_logger.log_error("build_monitor", "monitoring_loop_error", str(e))
    
    async def _update_monitoring_data(self):
        """Update monitoring data from shared state."""
        if not self.current_project_id:
            return
        
        # Get current project state
        project = shared_state.get_project_state(self.current_project_id)
        if not project:
            return
        
        # Get agent states
        agent_states = shared_state.get_agent_states()
        
        # Update progress tracker
        self.progress_tracker.update_project_progress(
            self.current_project_id,
            project.current_phase,
            project.progress
        )
        
        # Track active agents
        currently_active = set()
        for agent_id, state in agent_states.items():
            if state.status == AgentStatus.WORKING:
                currently_active.add(agent_id)
                
                # Log agent activity to live display
                if self.enable_live_display:
                    live_display.log_agent_activity(agent_id, state.current_task or "Working")
        
        # Update active agents set
        self.active_agents.update(currently_active)
        
        # Check for phase changes
        if hasattr(project, '_last_monitored_phase'):
            if project._last_monitored_phase != project.current_phase:
                self._on_phase_change(
                    project._last_monitored_phase,
                    project.current_phase,
                    project.progress
                )
        project._last_monitored_phase = project.current_phase
    
    def _on_phase_change(self, old_phase: str, new_phase: str, progress: float):
        """Handle build phase changes."""
        if self.enable_logging:
            agent_logger.log_build_phase_change(
                self.current_project_id or "unknown",
                old_phase, new_phase, progress
            )
        
        self._emit_event("phase_change", f"Phase changed: {old_phase} → {new_phase}", {
            "old_phase": old_phase,
            "new_phase": new_phase,
            "progress": progress
        })
        
        print(f"🏗️ Build phase: {old_phase} → {new_phase} ({progress:.1%})")
    
    def log_agent_status_change(self, agent_id: str, old_status: AgentStatus, 
                               new_status: AgentStatus, task: Optional[str] = None):
        """Log agent status change."""
        if self.enable_logging:
            agent_logger.log_agent_status_change(agent_id, old_status, new_status, task)
        
        if self.enable_live_display:
            live_display.log_agent_activity(
                agent_id, 
                f"Status: {old_status.value} → {new_status.value}"
            )
        
        self._emit_event("agent_status_change", f"Agent {agent_id} status changed", {
            "agent_id": agent_id,
            "old_status": old_status.value,
            "new_status": new_status.value,
            "task": task
        })
    
    def log_tool_usage(self, agent_id: str, tool_name: str, operation: str,
                      status: str, execution_time: Optional[float] = None,
                      input_data: Optional[Dict[str, Any]] = None,
                      output_data: Optional[Dict[str, Any]] = None,
                      error: Optional[str] = None):
        """Log tool usage by an agent."""
        self.total_tool_calls += 1
        
        if self.enable_logging:
            agent_logger.log_tool_usage(
                agent_id, tool_name, operation, status,
                execution_time, input_data, output_data, error
            )
        
        if self.enable_live_display:
            live_display.log_tool_usage(agent_id, tool_name, operation, status)
            live_display.log_agent_activity(
                agent_id,
                f"Used {tool_name}.{operation} - {status}"
            )
        
        self._emit_event("tool_usage", f"Tool used: {tool_name}.{operation}", {
            "agent_id": agent_id,
            "tool_name": tool_name,
            "operation": operation,
            "status": status,
            "execution_time": execution_time,
            "error": error
        })
    
    def log_agent_collaboration(self, from_agent: str, to_agent: str,
                               collaboration_type: str, data: Dict[str, Any]):
        """Log agent collaboration."""
        if self.enable_logging:
            agent_logger.log_agent_collaboration(from_agent, to_agent, collaboration_type, data)
        
        if self.enable_live_display:
            live_display.log_message(from_agent, to_agent, collaboration_type, data)
            live_display.log_agent_activity(
                from_agent,
                f"Collaborating with {to_agent}: {collaboration_type}"
            )
        
        self._emit_event("collaboration", f"Collaboration: {from_agent} → {to_agent}", {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "type": collaboration_type,
            "data": data
        })
    
    def log_message(self, from_agent: str, to_agent: str, message_type: MessageType,
                   content: Any, priority: int = 1):
        """Log inter-agent messages."""
        if self.enable_logging:
            agent_logger.log_message(from_agent, to_agent, message_type, content, priority)
        
        if self.enable_live_display:
            live_display.log_message(from_agent, to_agent, message_type.value, content)
        
        self._emit_event("message", f"Message: {from_agent} → {to_agent}", {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "message_type": message_type.value,
            "content": content,
            "priority": priority
        })
    
    def add_event_callback(self, callback: Callable[[BuildEvent], None]):
        """Add a callback for build events."""
        self.event_callbacks.append(callback)
    
    def _emit_event(self, event_type: str, description: str, data: Optional[Dict[str, Any]] = None):
        """Emit a build event."""
        event = BuildEvent(
            timestamp=datetime.now(),
            project_id=self.current_project_id or "unknown",
            agent_id="build_monitor",
            event_type=event_type,
            description=description,
            data=data
        )
        
        self.build_events.append(event)
        
        # Call event callbacks
        for callback in self.event_callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"Event callback error: {e}")
    
    def get_build_summary(self) -> Dict[str, Any]:
        """Get a summary of the current build."""
        if not self.is_monitoring:
            return {"status": "not_monitoring"}
        
        build_duration = datetime.now() - self.build_start_time if self.build_start_time else None
        
        # Get LLM usage summary
        llm_metrics = {}
        try:
            from utils.llm_logger import llm_logger
            llm_summary = llm_logger.get_session_summary()
            llm_metrics = {
                "total_llm_requests": llm_summary.get("total_requests", 0),
                "total_tokens_used": llm_summary.get("total_tokens", 0),
                "llm_success_rate": llm_summary.get("success_rate", 0),
                "average_llm_duration": llm_summary.get("average_duration", 0),
                "llm_error_count": llm_summary.get("error_count", 0)
            }
        except ImportError:
            pass
        except Exception as e:
            self.logger.debug(f"Could not get LLM metrics: {e}")
        
        return {
            "project_id": self.current_project_id,
            "is_monitoring": self.is_monitoring,
            "build_duration": str(build_duration) if build_duration else "Unknown",
            "total_events": len(self.build_events),
            "total_tool_calls": self.total_tool_calls,
            "active_agents": list(self.active_agents),
            "current_phase": self.progress_tracker.get_current_phase(self.current_project_id or ""),
            "overall_progress": self.progress_tracker.get_overall_progress(),
            "llm_metrics": llm_metrics,
            "recent_events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "event_type": event.event_type,
                    "description": event.description
                }
                for event in self.build_events[-10:]  # Last 10 events
            ]
        }
    
    def export_build_report(self, filename: Optional[str] = None) -> str:
        """Export a detailed build report."""
        import json
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"build_report_{self.current_project_id}_{timestamp}.json"
        
        report = {
            "build_summary": self.get_build_summary(),
            "progress_data": self.progress_tracker.get_detailed_progress(self.current_project_id or ""),
            "all_events": [
                {
                    "timestamp": event.timestamp.isoformat(),
                    "agent_id": event.agent_id,
                    "event_type": event.event_type,
                    "description": event.description,
                    "data": event.data
                }
                for event in self.build_events
            ],
            "agent_statistics": self._calculate_agent_statistics()
        }
        
        # Save to file
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📊 Build report exported to: {filename}")
        return filename
    
    def _calculate_agent_statistics(self) -> Dict[str, Any]:
        """Calculate statistics about agent activities."""
        stats = {}
        
        for event in self.build_events:
            agent_id = event.agent_id
            if agent_id not in stats:
                stats[agent_id] = {
                    "total_events": 0,
                    "event_types": {},
                    "tool_calls": 0,
                    "collaborations": 0
                }
            
            stats[agent_id]["total_events"] += 1
            
            event_type = event.event_type
            if event_type not in stats[agent_id]["event_types"]:
                stats[agent_id]["event_types"][event_type] = 0
            stats[agent_id]["event_types"][event_type] += 1
            
            if event_type == "tool_usage":
                stats[agent_id]["tool_calls"] += 1
            elif event_type == "collaboration":
                stats[agent_id]["collaborations"] += 1
        
        return stats


# Global build monitor instance
build_monitor = BuildMonitor()
