"""
Orchestrator Agent - Master coordinator for FlutterSwarm.
Manages workflow, coordinates other agents, and makes high-level decisions.
"""

import asyncio
import uuid
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from shared.state import shared_state, AgentStatus, MessageType
from datetime import datetime

class OrchestratorAgent(BaseAgent):
    """
    The Orchestrator Agent serves as the master coordinator.
    It manages the overall workflow and coordinates all other agents.
    """
    
    def __init__(self):
        super().__init__("orchestrator")
        # Get workflow phases from config manager
        workflow_config = self._config_manager.get('workflow', {})
        self.workflow_phases = workflow_config.get('phases', [
            'planning', 'architecture', 'implementation', 'testing', 
            'security_review', 'performance_optimization', 'documentation', 'deployment'
        ])
        self.active_tasks = {}
        self.project_timeline = []
        
    async def execute_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute orchestration tasks."""
        try:
            # Analyze task using LLM to understand orchestration requirements
            analysis = await self.think(f"Analyze this orchestration task: {task_description}", {
                "task_data": task_data,
                "workflow_phases": self.workflow_phases,
                "active_tasks": self.active_tasks,
                "project_timeline": self.project_timeline
            })
            
            self.logger.info(f"🎯 Orchestrator Agent executing task: {task_description}")
            
            # Execute appropriate task with retry mechanism
            result = None
            # Removed create_project handling; only use build_project in workflow
            if "initiate_project_workflow" in task_description.lower():
                result = await self.safe_execute_with_retry(
                    lambda: self._initiate_project_workflow_task(task_data)
                )
            elif "coordinate_phase" in task_description.lower():
                result = await self.safe_execute_with_retry(
                    lambda: self._coordinate_phase(task_data)
                )
            elif "assign_task" in task_description.lower():
                result = await self.safe_execute_with_retry(
                    lambda: self._assign_task_to_agent(task_data)
                )
            else:
                result = await self.safe_execute_with_retry(
                    lambda: self._handle_general_coordination(task_description, task_data)
                )
            
            # Add execution metadata
            result.update({
                "task_type": task_description,
                "execution_time": datetime.now().isoformat(),
                "agent": self.agent_id,
                "current_phase": shared_state.get_project_state().current_phase if shared_state.get_project_state() else "unknown",
                "task_analysis": analysis[:200] + "..." if len(analysis) > 200 else analysis
            })
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ Error executing orchestration task: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "task_type": task_description,
                "execution_time": datetime.now().isoformat(),
                "agent": self.agent_id
            }
    
    async def collaborate(self, collaboration_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collaboration requests."""
        if collaboration_type == "request_decision":
            return await self._make_decision(data)
        elif collaboration_type == "report_completion":
            return await self._handle_task_completion(data)
        elif collaboration_type == "request_priority":
            return await self._prioritize_tasks(data)
        else:
            return {"status": "unknown_collaboration_type", "type": collaboration_type}
    
    async def on_state_change(self, change_data: Dict[str, Any]) -> None:
        """React to state changes and coordinate accordingly."""
        event = change_data.get("event")
        if event == "project_created":
            await self._initiate_project_workflow(change_data["project_id"])
        elif event == "agent_status_changed":
            # FIX: Add missing handler for agent status changes
            await self._handle_agent_status_change(change_data)
        elif event == "phase_completed":
            await self._advance_to_next_phase(change_data)

    async def _handle_agent_status_change(self, change_data: Dict[str, Any]) -> None:
        """Handle agent status changes (e.g., for stuck/idle agents)."""
        # Placeholder: implement logic as needed
        agent_id = change_data.get("agent_id")
        new_status = change_data.get("new_status")
        # Example: log or trigger recovery if agent is stuck
        self.logger.info(f"Agent {agent_id} changed status to {new_status}")

    async def _advance_to_next_phase(self, change_data: Dict[str, Any]) -> None:
        """Advance project to the next workflow phase after completion."""
        project_id = change_data.get("project_id")
        project = shared_state.get_project_state(project_id)
        if not project:
            return
        current_phase = getattr(project, 'current_phase', 'planning')
        try:
            current_phase_index = self.workflow_phases.index(current_phase)
        except ValueError:
            self.logger.error(f"Unknown phase: {current_phase}")
            return
        if current_phase_index < len(self.workflow_phases) - 1:
            next_phase = self.workflow_phases[current_phase_index + 1]
            shared_state.update_project(project_id, current_phase=next_phase)
            await self._coordinate_phase({
                "phase": next_phase,
                "project_id": project_id
            })
        else:
            self.logger.info(f"Project {project_id} completed all phases.")

    async def _create_flutter_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initiate the workflow for an existing Flutter project."""
        name = project_data["name"]
        
        # Find existing project by name
        project_id = None
        for pid, project in shared_state._projects.items():
            project_name = getattr(project, 'name', '')
            if project_name == name:
                project_id = pid
                break
        
        if not project_id:
            # Project doesn't exist, create it
            import uuid
            description = project_data["description"]
            requirements = project_data.get("requirements", [])
            project_id = str(uuid.uuid4())
            shared_state.create_project_with_id(project_id, name, description, requirements)
        
        # Start the workflow
        await self._initiate_project_workflow(project_id)
        
        return {
            "project_id": project_id,
            "status": "workflow_initiated",
            "next_phase": "planning"
        }
    
    async def _initiate_project_workflow_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Initiate workflow for an existing project."""
        project_id = task_data["project_id"]
        
        # Initiate the workflow for the existing project
        await self._initiate_project_workflow(project_id)
        
        return {
            "project_id": project_id,
            "status": "workflow_initiated",
            "next_phase": "planning"
        }

    async def _initiate_project_workflow(self, project_id: str) -> None:
        """Initiate the Flutter project development workflow."""
        project = shared_state.get_project_state(project_id)
        if not project:
            return
        
        # Defensively access project attributes
        project_name = getattr(project, 'name', 'Unknown Project')
        project_description = getattr(project, 'description', 'No description available')
        project_requirements = getattr(project, 'requirements', [])
        
        # Start with planning phase
        planning_prompt = f"""
        Analyze the project requirements and create a comprehensive plan:
        
        Project: {project_name}
        Description: {project_description}
        Requirements: {project_requirements}
        
        Create a detailed project plan including:
        1. Architecture decisions needed
        2. Key features to implement
        3. Technical stack recommendations
        4. Development phases and milestones
        5. Risk assessment
        6. Resource allocation
        
        Consider Flutter best practices and modern app development patterns.
        """
        
        plan = await self.think(planning_prompt, {
            "project": project,
            "available_agents": self.get_other_agents()
        })
        
        # Update project with planning results
        shared_state.update_project(project_id, current_phase="architecture")
        
        # FIRST: Create the actual Flutter project structure using detailed setup task
        structure_task_id = await self._assign_project_setup_task(project_id, plan)
        
        # WAIT for project structure to be created before proceeding
        self.logger.info(f"⏳ Waiting for project structure setup to complete...")
        structure_success = await self._wait_for_task_completion(structure_task_id, timeout=300)
        
        if structure_success:
            self.logger.info(f"✅ Project structure created successfully, proceeding with architecture design")
            
            # THEN: Assign architecture task to Architecture Agent
            architecture_task_id = str(uuid.uuid4())
            self.send_message_to_agent(
                to_agent="architecture",
                message_type=MessageType.TASK_REQUEST,
                content={
                    "task_id": architecture_task_id,
                    "task_description": "design_flutter_architecture",
                    "task_data": {
                        "project_id": project_id,
                        "requirements": getattr(project, 'requirements', []),
                        "planning_output": plan
                    }
                },
                priority=5
            )
        else:
            self.logger.error(f"❌ Project structure setup failed or timed out. Skipping architecture design.")
        
        print(f"🎯 Orchestrator: Initiated workflow for project {getattr(project, 'name', 'Unknown Project')}")
    
    
    async def _coordinate_phase(self, phase_data: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate a specific development phase."""
        phase = phase_data["phase"]
        project_id = phase_data["project_id"]
        
        coordination_prompt = f"""
        Coordinate the {phase} phase for the Flutter project.
        
        Based on the current project state and agent capabilities,
        determine:
        1. Which agents need to be involved
        2. What tasks need to be assigned
        3. Dependencies between tasks
        4. Expected deliverables
        5. Success criteria
        
        Available agents and their current status:
        {self.get_other_agents()}
        """
        
        coordination_plan = await self.think(coordination_prompt, {
            "phase": phase,
            "project": shared_state.get_project_state(project_id)
        })
        
        # Execute the coordination plan
        await self._execute_coordination_plan(coordination_plan, project_id, phase)
        
        return {
            "phase": phase,
            "status": "coordinated",
            "plan": coordination_plan
        }
    
    async def _assign_task_to_agent(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assign a specific task to the most appropriate agent."""
        import uuid
        task_description = task_data["task_description"]
        required_capabilities = task_data.get("required_capabilities", [])
        
        # Find the best agent for the task
        best_agent = await self._find_best_agent_for_task(required_capabilities)
        
        if best_agent:
            task_id = str(uuid.uuid4())
            content = dict(task_data)
            content["task_id"] = task_id
            self.send_message_to_agent(
                to_agent=best_agent,
                message_type=MessageType.TASK_REQUEST,
                content=content,
                priority=task_data.get("priority", 3)
            )
            
            return {
                "assigned_to": best_agent,
                "task": task_description,
                "task_id": task_id,
                "status": "assigned"
            }
        else:
            return {
                "status": "no_suitable_agent",
                "task": task_description
            }
    
    async def _find_best_agent_for_task(self, required_capabilities: List[str]) -> Optional[str]:
        """Find the best agent for a task based on capabilities and availability."""
        agents = self.get_other_agents()
        best_agent = None
        best_score = 0
        
        for agent_id, agent_state in agents.items():
            if agent_state.status == AgentStatus.IDLE:
                # Calculate capability match score
                agent_capabilities = set(agent_state.capabilities)
                required_capabilities_set = set(required_capabilities)
                match_score = len(agent_capabilities.intersection(required_capabilities_set))
                
                if match_score > best_score:
                    best_score = match_score
                    best_agent = agent_id
        
        return best_agent
    
    async def _execute_coordination_plan(self, plan: str, project_id: str, phase: str) -> None:
        """Execute a coordination plan by assigning tasks to agents."""
        # This is a simplified implementation
        # In a real scenario, you'd parse the plan and extract specific tasks
        if "architecture" in phase.lower():
            # Assign detailed architecture task with full context
            task_id = str(uuid.uuid4())
            project = shared_state.get_project_state(project_id)
            
            self.send_message_to_agent(
                to_agent="architecture",
                message_type=MessageType.TASK_REQUEST,
                content={
                    "task_id": task_id,
                    "task_description": "design_flutter_architecture_with_context",
                    "task_data": {
                        "project_id": project_id,
                        "project_name": getattr(project, 'name', 'Unknown Project') if project else 'Unknown Project',
                        "description": getattr(project, 'description', 'No description available') if project else 'No description available',
                        "requirements": getattr(project, 'requirements', []) if project else [],
                        "planning_output": plan,
                        "architecture_goals": [
                            "scalable_architecture",
                            "maintainable_code_structure", 
                            "flutter_best_practices",
                            "clean_architecture_principles"
                        ]
                    }
                },
                priority=5
            )
        elif "implementation" in phase.lower():
            # Use the new detailed implementation task assignment
            await self._assign_implementation_task(project_id, {"phase": phase, "plan": plan})
        elif "testing" in phase.lower():
            # Assign detailed testing task
            await self._assign_testing_task(project_id, {"phase": phase, "plan": plan})
        elif "security" in phase.lower():
            # Assign detailed security review task
            await self._assign_security_task(project_id, {"phase": phase, "plan": plan})
        elif "performance" in phase.lower():
            # Assign detailed performance optimization task
            await self._assign_performance_task(project_id, {"phase": phase, "plan": plan})
        # Add more phase-specific logic as needed
    
    async def _make_decision(self, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Make high-level decisions when agents need guidance."""
        question = decision_data.get("question", "")
        options = decision_data.get("options", [])
        context = decision_data.get("context", {})
        
        decision_prompt = f"""
        As the Orchestrator Agent, make a decision on the following:
        
        Question: {question}
        Options: {options}
        Context: {context}
        
        Consider:
        1. Project goals and requirements
        2. Technical best practices
        3. Resource constraints
        4. Timeline implications
        5. Risk factors
        
        Provide a clear decision with reasoning.
        """
        
        decision = await self.think(decision_prompt, {
            "current_project": self.get_project_state(),
            "agent_states": self.get_other_agents()
        })
        
        return {
            "decision": decision,
            "timestamp": shared_state._current_project_id,  # placeholder
            "reasoning": "Based on project requirements and best practices"
        }
    
    async def _handle_task_completion(self, completion_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle task completion reports from agents."""
        task_id = completion_data.get("task_id")
        agent_id = completion_data.get("agent_id")
        result = completion_data.get("result")
        
        # Log completion
        print(f"✅ Task {task_id} completed by {agent_id}")
        
        # Determine next steps based on completion
        await self._plan_next_steps(completion_data)
        
        return {"status": "acknowledged", "next_steps_planned": True}
    
    async def _plan_next_steps(self, completion_data: Dict[str, Any]) -> None:
        """Plan next steps after task completion."""
        # Simplified next step planning
        # In a real implementation, this would be more sophisticated
        
        project = self.get_project_state()
        if project:
            current_phase = getattr(project, 'current_phase', 'planning')
            current_phase_index = self.workflow_phases.index(current_phase)
            if current_phase_index < len(self.workflow_phases) - 1:
                next_phase = self.workflow_phases[current_phase_index + 1]
                project_id = getattr(project, 'project_id', 'unknown')
                shared_state.update_project(project_id, current_phase=next_phase)
                
                # Coordinate the next phase
                await self._coordinate_phase({
                    "phase": next_phase,
                    "project_id": project_id
                })
    
    async def _prioritize_tasks(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prioritize tasks based on project needs."""
        tasks = task_data.get("tasks", [])
        
        prioritization_prompt = f"""
        Prioritize the following tasks for the Flutter project:
        {tasks}
        
        Consider:
        1. Dependencies between tasks
        2. Critical path items
        3. Resource availability
        4. Risk factors
        5. Business value
        
        Return a prioritized list with reasoning.
        """
        
        prioritized_tasks = await self.think(prioritization_prompt, {
            "project": self.get_project_state(),
            "agents": self.get_other_agents()
        })
        
        return {
            "prioritized_tasks": prioritized_tasks,
            "methodology": "dependency_and_value_based"
        }
    
    async def _handle_general_coordination(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general coordination tasks."""
        coordination_prompt = f"""
        Handle the following coordination task:
        {task_description}
        
        Task data: {task_data}
        
        As the Orchestrator, determine the best approach and actions to take.
        """
        
        response = await self.think(coordination_prompt, {
            "project": self.get_project_state(),
            "agents": self.get_other_agents()
        })
        
        return {
            "response": response,
            "task_handled": task_description
        }
    
    async def _periodic_task(self) -> None:
        """Periodic orchestration tasks."""
        # Check for stuck agents
        agents = self.get_other_agents()
        for agent_id, agent_state in agents.items():
            if agent_state.status == AgentStatus.WORKING:
                # Check if agent has been working too long without updates
                # Implement timeout logic here
                pass
        
        # Monitor project progress
        project = self.get_project_state()
        if project:
            # Calculate overall progress
            total_phases = len(self.workflow_phases)
            current_phase = getattr(project, 'current_phase', 'planning')
            current_phase_index = self.workflow_phases.index(current_phase)
            progress = (current_phase_index + 1) / total_phases
            
            project_id = getattr(project, 'project_id', 'unknown')
            shared_state.update_project(project_id, progress=progress)
    
    async def _wait_for_task_completion(self, task_id: str, timeout: int = 300) -> bool:
        """
        Wait for a specific task to complete by monitoring the message queue.
        
        Args:
            task_id: The unique task ID to wait for
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if task completed successfully, False if timed out or failed
        """
        start_time = asyncio.get_event_loop().time()
        
        # Add circuit breaker to prevent infinite waiting
        from shared.state import CircuitBreaker
        circuit_breaker = CircuitBreaker(
            max_iterations=int(timeout * 2),   # 2 checks per second max  
            max_time=timeout + 5,              # Slightly longer than timeout
            name=f"orchestrator_wait_task_{task_id}"
        )
        
        self.logger.info(f"⏳ Waiting for task {task_id} to complete (timeout: {timeout}s)")
        
        check_count = 0
        while circuit_breaker.check():
            # Check if we've exceeded the timeout
            current_time = asyncio.get_event_loop().time()
            if current_time - start_time > timeout:
                self.logger.error(f"⏰ Task {task_id} timed out after {timeout} seconds")
                return False
            
            # Get recent messages with priority for task completion
            messages = shared_state.get_messages(self.agent_id, mark_read=True, limit=100)
            
            # Look for task completion message
            for message in messages:
                if (message.message_type == MessageType.TASK_COMPLETED and 
                    message.content.get("task_id") == task_id):
                    
                    result = message.content.get("result", {})
                    status = result.get("status", "unknown")
                    
                    elapsed_time = current_time - start_time
                    
                    if status in ["completed", "success", "project_structure_created", "architecture_completed"]:
                        self.logger.info(f"✅ Task {task_id} completed successfully in {elapsed_time:.2f}s")
                        return True
                    else:
                        self.logger.error(f"❌ Task {task_id} failed with status: {status} after {elapsed_time:.2f}s")
                        return False
                        
                # Also check for error reports
                elif (message.message_type == MessageType.ERROR_REPORT and 
                      message.content.get("task_id") == task_id):
                    
                    error = message.content.get("error", "Unknown error")
                    elapsed_time = current_time - start_time
                    self.logger.error(f"❌ Task {task_id} failed with error: {error} after {elapsed_time:.2f}s")
                    return False
            
            check_count += 1
            if check_count % 10 == 0:  # Log every 5 seconds
                elapsed = current_time - start_time
                self.logger.info(f"⏳ Still waiting for task {task_id} ({elapsed:.1f}s elapsed)")
            
            # Wait a short time before checking again
            await asyncio.sleep(0.5)  # Check every 500ms
        
        # Circuit breaker triggered
        self.logger.error(f"🚨 Task waiting stopped by circuit breaker for {task_id}")
        return False
    
    async def _assign_implementation_task(self, project_id: str, phase_data: Dict[str, Any]) -> None:
        """Assign specific implementation task with full context."""
        project = shared_state.get_project_state(project_id)
        
        # Get architecture decisions from architecture agent using defensive access
        architecture_decisions = getattr(project, 'architecture_decisions', []) if project else []
        
        # Create specific implementation task
        implementation_task = {
            "task_type": "implement_features",
            "project_id": project_id,
            "project_name": getattr(project, 'name', 'Unknown Project') if project else 'Unknown Project',
            "description": getattr(project, 'description', 'No description available') if project else 'No description available',
            "requirements": getattr(project, 'requirements', []) if project else [],
            "architecture_decisions": architecture_decisions,
            "specific_features": [
                {
                    "name": "project_setup",
                    "description": "Initialize Flutter project with proper structure",
                    "files_to_create": ["lib/main.dart", "pubspec.yaml"]
                },
                {
                    "name": "core_models",
                    "description": "Create data models based on requirements",
                    "files_to_create": ["lib/models/", "lib/data/"]
                },
                {
                    "name": "ui_screens",
                    "description": "Implement UI screens for each requirement",
                    "files_to_create": ["lib/screens/", "lib/widgets/"]
                }
            ]
        }
        
        # Send to implementation agent
        await shared_state.send_message(
            sender_id=self.agent_id,
            receiver_id="implementation",
            message_type=MessageType.TASK_ASSIGNMENT,
            content={
                "task": "implement_features_with_context",
                "data": implementation_task
            }
        )
    
    async def _assign_project_setup_task(self, project_id: str, plan: str) -> str:
        """Assign project setup task with detailed context."""
        project = shared_state.get_project_state(project_id)
        
        # Create detailed project setup task
        setup_task = {
            "task_type": "setup_project_structure",
            "project_id": project_id,
            "project_name": getattr(project, 'name', 'Unknown Project') if project else 'Unknown Project',
            "description": getattr(project, 'description', 'No description available') if project else 'No description available',
            "requirements": getattr(project, 'requirements', []) if project else [],
            "architecture_style": "clean_architecture",
            "planning_output": plan,
            "specific_setup_actions": [
                {
                    "name": "flutter_init",
                    "description": "Initialize Flutter project with proper configuration",
                    "files_to_create": ["pubspec.yaml", "analysis_options.yaml"]
                },
                {
                    "name": "folder_structure",
                    "description": "Create clean architecture folder structure",
                    "files_to_create": [
                        "lib/core/",
                        "lib/features/",
                        "lib/shared/",
                        "test/"
                    ]
                },
                {
                    "name": "basic_files",
                    "description": "Create essential Flutter files",
                    "files_to_create": [
                        "lib/main.dart",
                        "lib/app.dart",
                        "lib/core/themes/app_theme.dart",
                        "lib/core/constants/app_constants.dart"
                    ]
                }
            ]
        }
        
        task_id = str(uuid.uuid4())
        self.send_message_to_agent(
            to_agent="implementation",
            message_type=MessageType.TASK_REQUEST,
            content={
                "task_id": task_id,
                "task_description": "setup_project_structure_with_context",
                "task_data": setup_task
            },
            priority=10  # High priority to create structure first
        )
        
        return task_id
