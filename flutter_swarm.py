"""
FlutterSwarm - Multi-Agent Flutter Development System
Main orchestration system that coordinates all agents using LangGraph.
"""

import asyncio
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import all agents
from agents.orchestrator_agent import OrchestratorAgent
from agents.architecture_agent import ArchitectureAgent
from agents.implementation_agent import ImplementationAgent
from agents.testing_agent import TestingAgent
from agents.security_agent import SecurityAgent
from agents.devops_agent import DevOpsAgent
from agents.documentation_agent import DocumentationAgent
from agents.performance_agent import PerformanceAgent
from agents.quality_assurance_agent import QualityAssuranceAgent

# Import shared state
from shared.state import shared_state, AgentStatus, MessageType

class FlutterSwarm:
    """
    Main FlutterSwarm system that orchestrates all agents.
    Provides high-level API for creating and building Flutter projects.
    """
    
    def __init__(self):
        self.agents = {}
        self.is_running = False
        self._initialize_agents()
        
    def _initialize_agents(self):
        """Initialize all agents."""
        print("🐝 Initializing FlutterSwarm agents...")
        
        # Create all agent instances
        self.agents = {
            "orchestrator": OrchestratorAgent(),
            "architecture": ArchitectureAgent(),
            "implementation": ImplementationAgent(),
            "testing": TestingAgent(),
            "security": SecurityAgent(),
            "devops": DevOpsAgent(),
            "documentation": DocumentationAgent(),
            "performance": PerformanceAgent(),
            "quality_assurance": QualityAssuranceAgent()
        }
        
        print(f"✅ Initialized {len(self.agents)} agents")
    
    async def start(self):
        """Start all agents."""
        if self.is_running:
            print("⚠️  FlutterSwarm is already running")
            return
        
        print("🚀 Starting FlutterSwarm...")
        self.is_running = True
        
        # Start all agents concurrently
        agent_tasks = []
        for agent_id, agent in self.agents.items():
            task = asyncio.create_task(agent.start())
            agent_tasks.append(task)
            print(f"📡 Started {agent_id} agent")
        
        print("🐝 All agents are now active and collaborating!")
        
        # Keep the system running
        try:
            await asyncio.gather(*agent_tasks)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down FlutterSwarm...")
            await self.stop()
    
    async def stop(self):
        """Stop all agents."""
        if not self.is_running:
            return
        
        print("🛑 Stopping all agents...")
        
        # Stop all agents
        stop_tasks = []
        for agent in self.agents.values():
            task = asyncio.create_task(agent.stop())
            stop_tasks.append(task)
        
        await asyncio.gather(*stop_tasks)
        self.is_running = False
        print("✅ FlutterSwarm stopped")
    
    def create_project(self, name: str, description: str, 
                      requirements: List[str] = None,
                      features: List[str] = None) -> str:
        """
        Create a new Flutter project.
        
        Args:
            name: Project name
            description: Project description
            requirements: List of requirements
            features: List of features to implement
            
        Returns:
            Project ID
        """
        if requirements is None:
            requirements = []
        if features is None:
            features = []
        
        print(f"🎯 Creating new Flutter project: {name}")
        
        # Create project in shared state
        project_id = shared_state.create_project(name, description, requirements)
        
        print(f"✅ Project created with ID: {project_id}")
        return project_id
    
    async def build_project(self, project_id: str, 
                           platforms: List[str] = None,
                           ci_system: str = "github_actions") -> Dict[str, Any]:
        """
        Build a Flutter project using the agent swarm.
        
        Args:
            project_id: Project ID to build
            platforms: Target platforms (android, ios, web, desktop)
            ci_system: CI/CD system to use
            
        Returns:
            Build result with status and artifacts
        """
        if platforms is None:
            platforms = ["android", "ios"]
        
        project = shared_state.get_project_state(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        print(f"🏗️  Building Flutter project: {project.name}")
        print(f"📱 Target platforms: {platforms}")
        
        # Send initial task to orchestrator
        orchestrator = self.agents["orchestrator"]
        task_id = orchestrator.send_message_to_agent(
            to_agent="orchestrator",
            message_type=MessageType.TASK_REQUEST,
            content={
                "task_description": "create_project",
                "task_data": {
                    "name": project.name,
                    "description": project.description,
                    "requirements": project.requirements,
                    "platforms": platforms,
                    "ci_system": ci_system
                }
            },
            priority=5
        )
        
        print(f"📋 Assigned build task {task_id} to orchestrator")
        
        # Monitor progress
        return await self._monitor_build_progress(project_id)
    
    async def _monitor_build_progress(self, project_id: str) -> Dict[str, Any]:
        """Monitor the build progress and return when complete."""
        print("📊 Monitoring build progress...")
        
        while True:
            project = shared_state.get_project_state(project_id)
            if not project:
                break
            
            # Check agent statuses
            agent_states = shared_state.get_agent_states()
            
            # Print progress update
            active_agents = [
                agent_id for agent_id, state in agent_states.items() 
                if state.status == AgentStatus.WORKING
            ]
            
            if active_agents:
                print(f"🔄 Active agents: {', '.join(active_agents)}")
            
            # Check if build is complete (simplified check)
            if (project.current_phase == "deployment" and 
                project.progress >= 0.8 and 
                not active_agents):
                
                print("🎉 Build completed!")
                return {
                    "status": "completed",
                    "project_id": project_id,
                    "files_created": len(project.files_created),
                    "architecture_decisions": len(project.architecture_decisions),
                    "test_results": project.test_results,
                    "security_findings": len(project.security_findings),
                    "performance_metrics": project.performance_metrics,
                    "documentation": list(project.documentation.keys()),
                    "deployment_config": project.deployment_config
                }
            
            # Wait before next check
            await asyncio.sleep(5)
    
    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get current project status."""
        project = shared_state.get_project_state(project_id)
        if not project:
            return {"error": "Project not found"}
        
        agent_states = shared_state.get_agent_states()
        
        return {
            "project": {
                "id": project.project_id,
                "name": project.name,
                "current_phase": project.current_phase,
                "progress": project.progress,
                "files_created": len(project.files_created),
                "architecture_decisions": len(project.architecture_decisions),
                "security_findings": len(project.security_findings)
            },
            "agents": {
                agent_id: {
                    "status": state.status.value,
                    "current_task": state.current_task,
                    "progress": state.progress,
                    "last_update": state.last_update.isoformat()
                }
                for agent_id, state in agent_states.items()
            }
        }
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects."""
        # This would be implemented to return all projects from shared state
        # For now, return the current project if it exists
        current_project = shared_state.get_project_state()
        if current_project:
            return [{
                "id": current_project.project_id,
                "name": current_project.name,
                "description": current_project.description,
                "current_phase": current_project.current_phase,
                "progress": current_project.progress
            }]
        return []
    
    def get_agent_status(self, agent_id: str = None) -> Dict[str, Any]:
        """Get status of specific agent or all agents."""
        if agent_id:
            state = shared_state.get_agent_state(agent_id)
            if state:
                return {
                    "agent_id": agent_id,
                    "status": state.status.value,
                    "current_task": state.current_task,
                    "progress": state.progress,
                    "capabilities": state.capabilities,
                    "last_update": state.last_update.isoformat()
                }
            return {"error": "Agent not found"}
        else:
            agent_states = shared_state.get_agent_states()
            return {
                agent_id: {
                    "status": state.status.value,
                    "current_task": state.current_task,
                    "progress": state.progress,
                    "last_update": state.last_update.isoformat()
                }
                for agent_id, state in agent_states.items()
            }

# Convenience function to create and run FlutterSwarm
async def run_flutter_swarm():
    """Create and run FlutterSwarm system."""
    swarm = FlutterSwarm()
    await swarm.start()

if __name__ == "__main__":
    # Example usage
    async def main():
        # Create FlutterSwarm instance
        swarm = FlutterSwarm()
        
        # Create a sample project
        project_id = swarm.create_project(
            name="TodoApp",
            description="A Flutter todo application with user authentication",
            requirements=[
                "User authentication",
                "Todo CRUD operations", 
                "Offline synchronization",
                "Push notifications",
                "Dark mode support"
            ],
            features=["auth", "crud", "offline_sync", "notifications"]
        )
        
        # Start the swarm (this will run indefinitely)
        # In a real application, you'd want to handle this differently
        await swarm.start()
    
    asyncio.run(main())
