"""
Process Supervision Agent - Monitors all development processes, handles failures, and ensures quality.
"""

import asyncio
import uuid
import time
import psutil
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from .base_agent import BaseAgent
from shared.state import shared_state, AgentStatus, MessageType, ProcessSupervisionState


class ProcessSupervisionAgent(BaseAgent):
    """
    The Process Supervision Agent monitors all development processes and intervenes when necessary.
    It tracks execution times, resource usage, and implements recovery mechanisms.
    """
    
    def __init__(self):
        super().__init__("supervision")
        
        # Configuration from config manager
        supervision_config = self.agent_config.get('supervision', {})
        self.timeouts = supervision_config.get('process_timeouts', {
            'build': 600,
            'test': 300,
            'analysis': 180,
            'code_generation': 240
        })
        self.health_check_interval = supervision_config.get('health_check_interval', 15)
        self.stuck_threshold = supervision_config.get('stuck_threshold', 120)
        self.max_retries = supervision_config.get('max_retries', 3)
        
        # Recovery agent mapping
        self.recovery_mapping = {
            'build_failure': 'implementation',
            'test_failure': 'testing',
            'security_issue': 'security',
            'performance_issue': 'performance',
            'code_generation_failure': 'implementation',
            'analysis_failure': 'architecture'
        }
        
        # Internal state
        self.is_monitoring = False
        self.monitoring_task = None
        
        self.logger.info("🔍 Process Supervision Agent initialized")
    
    async def execute_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute supervision tasks."""
        try:
            # Analyze task using LLM to understand supervision requirements
            analysis = await self.think(f"Analyze this supervision task: {task_description}", {
                "task_data": task_data,
                "task_description": task_description,
                "agent_id": self.agent_id
            })
            
            self.logger.info(f"👁️ Supervision Agent executing task: {task_description}")
            
            # Execute appropriate task with retry mechanism
            result = None
            if "start_monitoring" in task_description:
                result = await self.safe_execute_with_retry(
                    lambda: self._start_monitoring(task_data)
                )
            elif "stop_monitoring" in task_description:
                result = await self.safe_execute_with_retry(
                    lambda: self._stop_monitoring(task_data)
                )
            elif "check_process_health" in task_description:
                result = await self.safe_execute_with_retry(
                    lambda: self._check_process_health(task_data)
                )
            elif "intervene_process" in task_description:
                result = await self.safe_execute_with_retry(
                    lambda: self._intervene_process(task_data)
                )
            elif "recover_from_failure" in task_description:
                result = await self.safe_execute_with_retry(
                    lambda: self._recover_from_failure(task_data)
                )
            else:
                result = await self.safe_execute_with_retry(
                    lambda: self._handle_general_supervision_task(task_description, task_data)
                )
            
            # Add execution metadata
            result.update({
                "task_type": task_description,
                "execution_time": datetime.now().isoformat(),
                "agent": self.agent_id,
                "task_analysis": analysis[:200] + "..." if len(analysis) > 200 else analysis
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error executing supervision task: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "task_type": task_description,
                "execution_time": datetime.now().isoformat(),
                "agent": self.agent_id
            }
    
    async def collaborate(self, collaboration_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collaboration requests."""
        if collaboration_type == "supervision_status":
            return await self._provide_supervision_status(data)
        elif collaboration_type == "register_process":
            return await self._register_process_for_supervision(data)
        elif collaboration_type == "report_failure":
            return await self._handle_failure_report(data)
        else:
            return {"status": "unknown_collaboration_type", "type": collaboration_type}
    
    async def on_state_change(self, change_data: Dict[str, Any]) -> None:
        """React to state changes."""
        event = change_data.get("event")
        
        if event == "project_created":
            await self._start_project_supervision(change_data["project_id"])
        elif event == "agent_task_started":
            await self._register_agent_task(change_data)
        elif event == "agent_task_completed":
            await self._mark_task_completed(change_data)
    
    # Core supervision methods
    async def _start_monitoring(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Start the supervision monitoring loop."""
        if self.is_monitoring:
            return {"status": "already_monitoring"}
        
        self.is_monitoring = True
        self.monitoring_task = asyncio.create_task(self._monitoring_loop())
        
        self.logger.info("🔍 Started process supervision monitoring")
        
        return {
            "status": "monitoring_started",
            "health_check_interval": self.health_check_interval,
            "timeouts": self.timeouts
        }
    
    async def _stop_monitoring(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Stop the supervision monitoring loop."""
        self.is_monitoring = False
        
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
        
        self.logger.info("🔍 Stopped process supervision monitoring")
        
        return {"status": "monitoring_stopped"}
    
    async def _monitoring_loop(self):
        """Main monitoring loop that checks process health."""
        while self.is_monitoring:
            try:
                await self._perform_health_checks()
                await asyncio.sleep(self.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(5)  # Brief pause on error
    
    async def _perform_health_checks(self):
        """Perform comprehensive health checks on all supervised processes."""
        # Check for stuck processes
        stuck_processes = shared_state.get_stuck_processes(self.stuck_threshold)
        for process in stuck_processes:
            await self._handle_stuck_process(process)
        
        # Check for timeout processes
        timeout_processes = shared_state.get_timeout_processes()
        for process in timeout_processes:
            await self._handle_timeout_process(process)
        
        # Update resource usage for all running processes
        await self._update_resource_usage()
        
        # Check system health
        await self._check_system_health()
    
    async def _handle_stuck_process(self, process: ProcessSupervisionState):
        """Handle a process that appears stuck."""
        self.logger.warning(f"⚠️ Process {process.process_id} appears stuck (no activity for {self.stuck_threshold}s)")
        
        # Send health check request to the agent
        self.send_message_to_agent(
            to_agent=process.agent_id,
            message_type=MessageType.HEALTH_CHECK,
            content={
                "process_id": process.process_id,
                "check_type": "stuck_process",
                "last_heartbeat": process.last_heartbeat.isoformat(),
                "requested_by": self.agent_id
            },
            priority=4
        )
        
        shared_state.increment_process_intervention(process.process_id)
        
        # Log supervision event
        self.logger.warning(f"🔍 Sent health check request to {process.agent_id} for stuck process {process.process_id}")
    
    async def _handle_timeout_process(self, process: ProcessSupervisionState):
        """Handle a process that has exceeded its timeout threshold."""
        elapsed = (datetime.now() - process.start_time).total_seconds()
        self.logger.error(f"❌ Process {process.process_id} timed out (running for {elapsed:.1f}s, limit: {process.timeout_threshold}s)")
        
        # Send halt message to the agent
        self.send_message_to_agent(
            to_agent=process.agent_id,
            message_type=MessageType.PROCESS_HALT,
            content={
                "process_id": process.process_id,
                "reason": "timeout",
                "elapsed_time": elapsed,
                "timeout_threshold": process.timeout_threshold,
                "requested_by": self.agent_id
            },
            priority=5  # High priority
        )
        
        # Mark process as failed
        shared_state.mark_process_failed(process.process_id, f"Timeout after {elapsed:.1f}s")
        shared_state.increment_process_intervention(process.process_id)
        
        # Trigger recovery if needed
        await self._trigger_recovery(process, "timeout")
        
        self.logger.error(f"🔍 Halted timed-out process {process.process_id} and triggered recovery")
    
    async def _update_resource_usage(self):
        """Update CPU and memory usage for all supervised processes."""
        current_process = psutil.Process()
        
        try:
            # Get system-wide resource usage
            cpu_percent = psutil.cpu_percent(interval=None)
            memory = psutil.virtual_memory()
            
            # Update process resource usage
            processes = shared_state.get_supervised_processes()
            for process_id, process in processes.items():
                if process.status == "running":
                    # For now, use system-wide metrics
                    # In a more sophisticated implementation, we could track per-process usage
                    shared_state.update_process_heartbeat(
                        process_id, 
                        cpu_usage=cpu_percent,
                        memory_usage=memory.percent
                    )
        
        except Exception as e:
            self.logger.debug(f"⚠️ Could not update resource usage: {e}")
    
    async def _check_system_health(self):
        """Check overall system health and resource availability."""
        try:
            # Check CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            if cpu_percent > 90:
                self.logger.warning(f"⚠️ High CPU usage detected: {cpu_percent:.1f}%")
                await self._send_supervision_alert("high_cpu_usage", {"cpu_percent": cpu_percent})
            
            # Check memory usage
            memory = psutil.virtual_memory()
            if memory.percent > 85:
                self.logger.warning(f"⚠️ High memory usage detected: {memory.percent:.1f}%")
                await self._send_supervision_alert("high_memory_usage", {"memory_percent": memory.percent})
            
            # Check disk space
            disk = psutil.disk_usage('/')
            if disk.percent > 90:
                self.logger.warning(f"⚠️ Low disk space detected: {disk.percent:.1f}% used")
                await self._send_supervision_alert("low_disk_space", {"disk_percent": disk.percent})
        
        except Exception as e:
            self.logger.debug(f"⚠️ Could not check system health: {e}")
    
    async def _trigger_recovery(self, process: ProcessSupervisionState, failure_type: str):
        """Trigger recovery mechanism for a failed process."""
        # Determine recovery agent based on task type and failure
        recovery_key = f"{process.task_type}_{failure_type}"
        recovery_agent = self.recovery_mapping.get(recovery_key, 
                                                 self.recovery_mapping.get(process.task_type, 
                                                                         'implementation'))
        
        # Create recovery task
        recovery_task = {
            "task_description": f"recover_from_{failure_type}",
            "task_data": {
                "failed_process_id": process.process_id,
                "failure_type": failure_type,
                "original_task_type": process.task_type,
                "failure_context": {
                    "agent_id": process.agent_id,
                    "start_time": process.start_time.isoformat(),
                    "elapsed_time": (datetime.now() - process.start_time).total_seconds(),
                    "intervention_count": process.intervention_count
                }
            }
        }
        
        # Send recovery task to appropriate agent
        self.send_message_to_agent(
            to_agent=recovery_agent,
            message_type=MessageType.TASK_REQUEST,
            content=recovery_task,
            priority=4
        )
        
        self.logger.info(f"🔄 Triggered recovery with {recovery_agent} for failed process {process.process_id}")
    
    async def _send_supervision_alert(self, alert_type: str, data: Dict[str, Any]):
        """Send supervision alert to all agents."""
        alert_content = {
            "alert_type": alert_type,
            "timestamp": datetime.now().isoformat(),
            "data": data,
            "supervisor": self.agent_id
        }
        
        # Broadcast supervision alert
        self.send_message_to_agent(
            to_agent=None,  # Broadcast
            message_type=MessageType.SUPERVISION_ALERT,
            content=alert_content,
            priority=4
        )
    
    # Task execution methods
    async def _check_process_health(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check health of specific processes."""
        processes = shared_state.get_supervised_processes()
        
        health_report = {
            "total_processes": len(processes),
            "running_processes": len([p for p in processes.values() if p.status == "running"]),
            "stuck_processes": len(shared_state.get_stuck_processes(self.stuck_threshold)),
            "timeout_processes": len(shared_state.get_timeout_processes()),
            "process_details": {}
        }
        
        for process_id, process in processes.items():
            health_report["process_details"][process_id] = {
                "agent_id": process.agent_id,
                "task_type": process.task_type,
                "status": process.status,
                "running_time": (datetime.now() - process.start_time).total_seconds(),
                "last_heartbeat": (datetime.now() - process.last_heartbeat).total_seconds(),
                "cpu_usage": process.cpu_usage,
                "memory_usage": process.memory_usage,
                "intervention_count": process.intervention_count
            }
        
        return {
            "status": "health_check_completed",
            "health_report": health_report
        }
    
    async def _intervene_process(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Manually intervene in a specific process."""
        process_id = task_data.get("process_id")
        intervention_type = task_data.get("intervention_type", "halt")
        
        processes = shared_state.get_supervised_processes()
        if process_id not in processes:
            return {"status": "process_not_found", "process_id": process_id}
        
        process = processes[process_id]
        
        if intervention_type == "halt":
            await self._handle_timeout_process(process)
        elif intervention_type == "health_check":
            await self._handle_stuck_process(process)
        elif intervention_type == "recover":
            await self._trigger_recovery(process, "manual_intervention")
        
        return {
            "status": "intervention_completed",
            "process_id": process_id,
            "intervention_type": intervention_type
        }
    
    async def _recover_from_failure(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate recovery from failures."""
        failure_type = task_data.get("failure_type")
        failed_process_id = task_data.get("failed_process_id")
        
        # Log recovery attempt
        self.logger.info(f"🔄 Starting recovery for {failure_type} (process: {failed_process_id})")
        
        # Update project state with recovery attempt
        if shared_state._current_project_id:
            project = shared_state.get_project_state(shared_state._current_project_id)
            if project:
                project.recovered_processes.append(f"{failed_process_id}: {failure_type}")
        
        return {
            "status": "recovery_initiated",
            "failure_type": failure_type,
            "failed_process_id": failed_process_id
        }
    
    async def _handle_general_supervision_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general supervision tasks."""
        self.logger.info(f"🔍 Handling general supervision task: {task_description}")
        
        # Default supervision response
        return {
            "status": "supervision_task_completed",
            "task_description": task_description,
            "supervisor": self.agent_id,
            "timestamp": datetime.now().isoformat()
        }
    
    # Collaboration methods
    async def _provide_supervision_status(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide current supervision status."""
        processes = shared_state.get_supervised_processes()
        
        status = {
            "is_monitoring": self.is_monitoring,
            "total_supervised_processes": len(processes),
            "running_processes": len([p for p in processes.values() if p.status == "running"]),
            "failed_processes": len([p for p in processes.values() if p.status == "failed"]),
            "completed_processes": len([p for p in processes.values() if p.status == "completed"]),
            "stuck_count": len(shared_state.get_stuck_processes(self.stuck_threshold)),
            "timeout_count": len(shared_state.get_timeout_processes()),
            "health_check_interval": self.health_check_interval,
            "configuration": {
                "timeouts": self.timeouts,
                "stuck_threshold": self.stuck_threshold,
                "max_retries": self.max_retries
            }
        }
        
        return {
            "status": "supervision_status_provided",
            "supervision_status": status
        }
    
    async def _register_process_for_supervision(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Register a new process for supervision."""
        agent_id = data.get("agent_id")
        task_type = data.get("task_type", "unknown")
        timeout_threshold = data.get("timeout_threshold", self.timeouts.get(task_type, 300))
        
        # Generate unique process ID
        process_id = f"{agent_id}_{task_type}_{uuid.uuid4().hex[:8]}"
        
        # Register with shared state
        shared_state.register_supervised_process(
            process_id=process_id,
            agent_id=agent_id,
            task_type=task_type,
            timeout_threshold=timeout_threshold
        )
        
        self.logger.info(f"🔍 Registered process {process_id} for supervision (agent: {agent_id}, type: {task_type})")
        
        return {
            "status": "process_registered",
            "process_id": process_id,
            "timeout_threshold": timeout_threshold
        }
    
    async def _handle_failure_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle failure reports from other agents."""
        failure_type = data.get("failure_type")
        agent_id = data.get("agent_id")
        details = data.get("details", {})
        
        self.logger.error(f"❌ Failure reported by {agent_id}: {failure_type}")
        
        # Create supervision alert
        await self._send_supervision_alert("agent_failure_reported", {
            "failure_type": failure_type,
            "reporting_agent": agent_id,
            "details": details
        })
        
        # Trigger appropriate recovery
        recovery_agent = self.recovery_mapping.get(failure_type, 'implementation')
        
        recovery_task = {
            "task_description": f"handle_{failure_type}",
            "task_data": {
                "failure_type": failure_type,
                "reporting_agent": agent_id,
                "failure_details": details,
                "recovery_requested_by": self.agent_id
            }
        }
        
        self.send_message_to_agent(
            to_agent=recovery_agent,
            message_type=MessageType.TASK_REQUEST,
            content=recovery_task,
            priority=4
        )
        
        return {
            "status": "failure_handled",
            "failure_type": failure_type,
            "recovery_agent": recovery_agent
        }
    
    # Utility methods
    async def _start_project_supervision(self, project_id: str):
        """Start supervision for a new project."""
        self.logger.info(f"🔍 Starting supervision for project: {project_id}")
        
        # Update project with supervision status
        project = shared_state.get_project_state(project_id)
        if project:
            project.supervision_status = "active"
            project.process_health_metrics = {
                "supervision_started": datetime.now().isoformat(),
                "supervisor_agent": self.agent_id
            }
    
    async def _register_agent_task(self, change_data: Dict[str, Any]):
        """Register a new agent task for supervision."""
        agent_id = change_data.get("agent_id")
        task_type = change_data.get("task_type", "unknown")
        
        if agent_id and agent_id != self.agent_id:  # Don't supervise ourselves
            await self._register_process_for_supervision({
                "agent_id": agent_id,
                "task_type": task_type
            })
    
    async def _mark_task_completed(self, change_data: Dict[str, Any]):
        """Mark an agent task as completed."""
        process_id = change_data.get("process_id")
        if process_id:
            shared_state.mark_process_completed(process_id)
            self.logger.debug(f"✅ Marked process {process_id} as completed")