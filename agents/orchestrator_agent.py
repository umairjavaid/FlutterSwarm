"""
Orchestrator Agent - Master coordinator for FlutterSwarm.
Manages workflow, coordinates other agents, and makes high-level decisions.
"""

import asyncio
from typing import Dict, List, Any, Optional
from agents.base_agent import BaseAgent
from shared.state import shared_state, AgentStatus, MessageType

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
        if "create_project" in task_description.lower():
            return await self._create_flutter_project(task_data)
        elif "coordinate_phase" in task_description.lower():
            return await self._coordinate_phase(task_data)
        elif "assign_task" in task_description.lower():
            return await self._assign_task_to_agent(task_data)
        else:
            return await self._handle_general_coordination(task_description, task_data)
    
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
            await self._handle_agent_status_change(change_data)
        elif event == "phase_completed":
            await self._advance_to_next_phase(change_data)
    
    async def _create_flutter_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new Flutter project and initiate the workflow."""
        name = project_data["name"]
        description = project_data["description"]
        requirements = project_data.get("requirements", [])
        
        # Create project in shared state
        project_id = shared_state.create_project(name, description, requirements)
        
        # Start the workflow
        await self._initiate_project_workflow(project_id)
        
        return {
            "project_id": project_id,
            "status": "created",
            "next_phase": "planning"
        }
    
    async def _initiate_project_workflow(self, project_id: str) -> None:
        """Initiate the Flutter project development workflow."""
        project = shared_state.get_project_state(project_id)
        if not project:
            return
        
        # Start with planning phase
        planning_prompt = f"""
        Analyze the project requirements and create a comprehensive plan:
        
        Project: {project.name}
        Description: {project.description}
        Requirements: {project.requirements}
        
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
        
        # FIRST: Create the actual Flutter project structure
        self.send_message_to_agent(
            to_agent="implementation",
            message_type=MessageType.TASK_REQUEST,
            content={
                "task_description": "setup_project_structure",
                "task_data": {
                    "project_id": project_id,
                    "architecture_style": "clean_architecture",
                    "planning_output": plan
                }
            },
            priority=10  # High priority to create structure first
        )
        
        # THEN: Assign architecture task to Architecture Agent
        self.send_message_to_agent(
            to_agent="architecture",
            message_type=MessageType.TASK_REQUEST,
            content={
                "task_description": "design_flutter_architecture",
                "task_data": {
                    "project_id": project_id,
                    "requirements": project.requirements,
                    "planning_output": plan
                }
            },
            priority=5
        )
        
        print(f"🎯 Orchestrator: Initiated workflow for project {project.name}")
    
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
        task_description = task_data["task_description"]
        required_capabilities = task_data.get("required_capabilities", [])
        
        # Find the best agent for the task
        best_agent = await self._find_best_agent_for_task(required_capabilities)
        
        if best_agent:
            self.send_message_to_agent(
                to_agent=best_agent,
                message_type=MessageType.TASK_REQUEST,
                content=task_data,
                priority=task_data.get("priority", 3)
            )
            
            return {
                "assigned_to": best_agent,
                "task": task_description,
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
            self.send_message_to_agent(
                to_agent="architecture",
                message_type=MessageType.TASK_REQUEST,
                content={
                    "task_description": f"handle_{phase}_phase",
                    "task_data": {"project_id": project_id, "plan": plan}
                }
            )
        elif "implementation" in phase.lower():
            self.send_message_to_agent(
                to_agent="implementation",
                message_type=MessageType.TASK_REQUEST,
                content={
                    "task_description": f"handle_{phase}_phase",
                    "task_data": {"project_id": project_id, "plan": plan}
                }
            )
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
            current_phase_index = self.workflow_phases.index(project.current_phase)
            if current_phase_index < len(self.workflow_phases) - 1:
                next_phase = self.workflow_phases[current_phase_index + 1]
                shared_state.update_project(project.project_id, current_phase=next_phase)
                
                # Coordinate the next phase
                await self._coordinate_phase({
                    "phase": next_phase,
                    "project_id": project.project_id
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
            current_phase_index = self.workflow_phases.index(project.current_phase)
            progress = (current_phase_index + 1) / total_phases
            
            shared_state.update_project(project.project_id, progress=progress)
