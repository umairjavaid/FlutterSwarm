"""
Architecture Agent - Handles system design and architectural decisions for Flutter projects.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from shared.state import shared_state, AgentStatus, MessageType

class ArchitectureAgent(BaseAgent):
    """
    The Architecture Agent specializes in system design and architectural decisions.
    It creates Flutter app architectures, selects patterns, and makes technology choices.
    """
    
    def __init__(self):
        super().__init__("architecture")
        self.design_patterns = [
            "BLoC", "Provider", "Riverpod", "GetX", "MobX", "Redux"
        ]
        self.architecture_styles = [
            "Clean Architecture", "Layered Architecture", "Hexagonal Architecture", "MVVM"
        ]
        
    async def execute_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute architecture-related tasks."""
        if "design_flutter_architecture" in task_description:
            return await self._design_flutter_architecture(task_data)
        elif "review_architecture" in task_description:
            return await self._review_architecture(task_data)
        elif "select_state_management" in task_description:
            return await self._select_state_management(task_data)
        elif "design_navigation" in task_description:
            return await self._design_navigation(task_data)
        else:
            return await self._handle_general_architecture_task(task_description, task_data)
    
    async def collaborate(self, collaboration_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collaboration requests."""
        if collaboration_type == "architecture_review":
            return await self._provide_architecture_feedback(data)
        elif collaboration_type == "pattern_recommendation":
            return await self._recommend_patterns(data)
        elif collaboration_type == "technology_selection":
            return await self._recommend_technologies(data)
        else:
            return {"status": "unknown_collaboration_type", "type": collaboration_type}
    
    async def on_state_change(self, change_data: Dict[str, Any]) -> None:
        """React to state changes."""
        event = change_data.get("event")
        
        if event == "project_created":
            await self._analyze_new_project(change_data["project_id"])
        elif event == "requirements_updated":
            await self._reassess_architecture(change_data["project_id"])
    
    async def _design_flutter_architecture(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Design a comprehensive Flutter application architecture."""
        project_id = task_data["project_id"]
        requirements = task_data["requirements"]
        planning_output = task_data.get("planning_output", "")
        
        project = shared_state.get_project_state(project_id)
        
        # Safety check for project state
        if not project:
            self.logger.warning(f"Project {project_id} not found in shared state, using task data")
            project_name = task_data.get("name", "Unknown Project")
            project_description = task_data.get("description", "No description available")
        else:
            project_name = project.name
            project_description = project.description
        
        architecture_prompt = f"""
        Design a comprehensive Flutter application architecture for:
        
        Project: {project_name}
        Description: {project_description}
        Requirements: {requirements}
        Planning Context: {planning_output}
        
        Create a detailed architecture that includes:
        
        1. **Overall Architecture Style**: Choose and justify (Clean, Layered, Hexagonal, etc.)
        
        2. **State Management**: Recommend the best solution (BLoC, Provider, Riverpod, etc.)
           - Justify your choice based on app complexity and team requirements
        
        3. **Project Structure**: Define folder organization
           - lib/
             - core/
             - features/
             - shared/
             - etc.
        
        4. **Data Layer Architecture**:
           - Repository pattern implementation
           - Data sources (remote, local)
           - Models and DTOs
           - Caching strategy
        
        5. **Dependency Injection**: Choose DI approach (get_it, injectable, etc.)
        
        6. **Navigation**: Routing strategy (GoRouter, Navigator 2.0, etc.)
        
        7. **Error Handling**: Global error handling strategy
        
        8. **Networking**: HTTP client setup and configuration
        
        9. **Local Storage**: Database choice (Hive, SQLite, Isar, etc.)
        
        10. **Testing Strategy**: Unit, widget, and integration test architecture
        
        11. **Performance Considerations**: Lazy loading, caching, optimization
        
        12. **Security Architecture**: Authentication, data protection, secure storage
        
        Provide specific package recommendations and code structure examples.
        Consider scalability, maintainability, and testability.
        """
        
        architecture_design = await self.think(architecture_prompt, {
            "project": project,
            "available_patterns": self.design_patterns,
            "architecture_styles": self.architecture_styles
        })
        
        # Create architecture decision record
        existing_decisions = project.architecture_decisions if project else []
        architecture_decision = {
            "decision_id": f"arch_{project_id}_{len(existing_decisions) + 1}",
            "title": "Flutter Application Architecture Design",
            "description": architecture_design,
            "status": "proposed",
            "created_by": self.agent_id,
            "created_at": datetime.now().isoformat(),
            "consequences": "Defines the overall structure and patterns for the Flutter application"
        }
        
        # Add to project state if project exists
        if project:
            project.architecture_decisions.append(architecture_decision)
            shared_state.update_project(project_id, architecture_decisions=project.architecture_decisions)
        else:
            # Update with new list if project not found
            updated_decisions = existing_decisions + [architecture_decision]
            shared_state.update_project(project_id, architecture_decisions=updated_decisions)
        
        # Request feedback from other agents
        await self._request_architecture_feedback(project_id, architecture_design)
        
        return {
            "architecture_design": architecture_design,
            "decision_record": architecture_decision,
            "status": "designed",
            "next_step": "implementation_planning"
        }
    
    async def _select_state_management(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Select the most appropriate state management solution."""
        project_id = task_data["project_id"]
        complexity = task_data.get("complexity", "medium")
        team_size = task_data.get("team_size", "small")
        
        selection_prompt = f"""
        Select the best state management solution for this Flutter project:
        
        Project Complexity: {complexity}
        Team Size: {team_size}
        
        Consider the following options and provide detailed analysis:
        
        1. **Provider**: Simple, built-in solution
        2. **BLoC**: Business Logic Component pattern
        3. **Riverpod**: Modern Provider evolution
        4. **GetX**: All-in-one solution
        5. **MobX**: Reactive state management
        6. **Redux**: Predictable state container
        
        For each option, analyze:
        - Learning curve
        - Scalability
        - Testing capabilities
        - Performance implications
        - Community support
        - Maintenance overhead
        
        Provide a clear recommendation with implementation approach.
        """
        
        recommendation = await self.think(selection_prompt, {
            "project": shared_state.get_project_state(project_id),
            "patterns": self.design_patterns
        })
        
        return {
            "recommendation": recommendation,
            "complexity": complexity,
            "team_size": team_size
        }
    
    async def _design_navigation(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Design the navigation architecture for the Flutter app."""
        project_id = task_data["project_id"]
        features = task_data.get("features", [])
        
        navigation_prompt = f"""
        Design the navigation architecture for this Flutter application:
        
        Features: {features}
        
        Consider:
        1. **Navigation Pattern**: Choose between:
           - GoRouter (recommended for most apps)
           - Navigator 2.0 (custom implementation)
           - Auto Route (code generation)
           - Fluro (traditional routing)
        
        2. **Route Structure**: Define the route hierarchy
        
        3. **Deep Linking**: Support for deep links and URL handling
        
        4. **Navigation State**: How to manage navigation state
        
        5. **Nested Navigation**: Handle complex navigation flows
        
        6. **Authentication Routes**: Protected routes and redirects
        
        7. **Error Handling**: 404 pages and error routes
        
        Provide specific implementation examples and route definitions.
        """
        
        navigation_design = await self.think(navigation_prompt, {
            "project": shared_state.get_project_state(project_id),
            "features": features
        })
        
        return {
            "navigation_design": navigation_design,
            "features": features,
            "pattern_selected": "Will be determined from the design"
        }
    
    async def _request_architecture_feedback(self, project_id: str, architecture_design: str) -> None:
        """Request feedback on architecture from other agents."""
        # Request feedback from Security Agent
        self.send_message_to_agent(
            to_agent="security",
            message_type=MessageType.COLLABORATION_REQUEST,
            content={
                "type": "architecture_review",
                "data": {
                    "project_id": project_id,
                    "architecture": architecture_design,
                    "focus": "security_implications"
                }
            }
        )
        
        # Request feedback from Performance Agent
        self.send_message_to_agent(
            to_agent="performance",
            message_type=MessageType.COLLABORATION_REQUEST,
            content={
                "type": "architecture_review",
                "data": {
                    "project_id": project_id,
                    "architecture": architecture_design,
                    "focus": "performance_implications"
                }
            }
        )
        
        # Request feedback from DevOps Agent
        self.send_message_to_agent(
            to_agent="devops",
            message_type=MessageType.COLLABORATION_REQUEST,
            content={
                "type": "architecture_review",
                "data": {
                    "project_id": project_id,
                    "architecture": architecture_design,
                    "focus": "deployment_considerations"
                }
            }
        )
    
    async def _provide_architecture_feedback(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Provide feedback on architecture decisions."""
        architecture = data.get("architecture", "")
        focus = data.get("focus", "general")
        
        feedback_prompt = f"""
        Review the following architecture and provide feedback focusing on {focus}:
        
        Architecture: {architecture}
        
        Provide specific, actionable feedback on:
        1. Strengths of the current design
        2. Potential issues or weaknesses
        3. Specific recommendations for improvement
        4. Alternative approaches to consider
        
        Focus your review on architectural best practices and {focus}.
        """
        
        feedback = await self.think(feedback_prompt, {
            "focus_area": focus,
            "design_patterns": self.design_patterns
        })
        
        return {
            "feedback": feedback,
            "focus": focus,
            "reviewer": self.agent_id
        }
    
    async def _recommend_patterns(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend design patterns for specific scenarios."""
        scenario = data.get("scenario", "")
        requirements = data.get("requirements", [])
        
        pattern_prompt = f"""
        Recommend the best design patterns for this scenario:
        
        Scenario: {scenario}
        Requirements: {requirements}
        
        Available patterns: {self.design_patterns}
        Architecture styles: {self.architecture_styles}
        
        For each recommendation:
        1. Pattern name and description
        2. When to use it
        3. Implementation approach
        4. Pros and cons
        5. Code examples (if applicable)
        """
        
        recommendations = await self.think(pattern_prompt, {
            "scenario": scenario,
            "requirements": requirements
        })
        
        return {
            "recommendations": recommendations,
            "scenario": scenario
        }
    
    async def _recommend_technologies(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend technologies and packages for specific needs."""
        need = data.get("need", "")
        constraints = data.get("constraints", [])
        
        tech_prompt = f"""
        Recommend technologies and Flutter packages for:
        
        Need: {need}
        Constraints: {constraints}
        
        Consider:
        1. Package popularity and maintenance
        2. Performance implications
        3. Learning curve
        4. Integration complexity
        5. Long-term support
        
        Provide specific package names with pub.dev links and reasoning.
        """
        
        recommendations = await self.think(tech_prompt, {
            "need": need,
            "constraints": constraints
        })
        
        return {
            "technology_recommendations": recommendations,
            "need": need
        }
    
    async def _analyze_new_project(self, project_id: str) -> None:
        """Analyze a new project and prepare architecture considerations."""
        project = shared_state.get_project_state(project_id)
        if not project:
            return
        
        analysis_prompt = f"""
        Analyze this new Flutter project and identify key architectural considerations:
        
        Project: {project.name}
        Description: {project.description}
        Requirements: {project.requirements}
        
        Identify:
        1. Complexity level (simple, medium, complex)
        2. Key architectural challenges
        3. Critical decisions needed
        4. Recommended architecture style
        5. Technology stack suggestions
        
        Prepare for detailed architecture design.
        """
        
        analysis = await self.think(analysis_prompt, {"project": project})
        
        # Store analysis in project metadata
        shared_state.update_project(
            project_id,
            metadata={
                "architecture_analysis": analysis,
                "analyzed_by": self.agent_id
            }
        )
    
    async def _handle_general_architecture_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general architecture tasks."""
        response = await self.think(f"Handle this architecture task: {task_description}", task_data)
        return {"response": response, "task": task_description}
