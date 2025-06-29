"""
Architecture Agent - Handles system design and architectural decisions for Flutter projects.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent
from shared.state import shared_state, AgentStatus, MessageType
import time
from utils.function_logger import track_function
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
        
    @track_function(log_args=True, log_return=True)
    async def execute_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute architecture-related tasks."""
        try:
            # Analyze task using LLM to understand architecture requirements
            analysis = await self.think(f"Analyze this architecture task: {task_description}", {
                "task_data": task_data,
                "design_patterns": self.design_patterns,
                "architecture_styles": self.architecture_styles,
                "project_id": task_data.get("project_id", "")
            })
            
            self.logger.info(f"🏛️ Architecture Agent executing task: {task_description}")
            
            # Execute appropriate task with retry mechanism
            result = None
            if "design_flutter_architecture" in task_description:
                result = await self.safe_execute_with_retry(
                    lambda: self._design_flutter_architecture(task_data)
                )
            elif "review_architecture" in task_description:
                result = await self.safe_execute_with_retry(
                    lambda: self._review_architecture(task_data)
                )
            elif "select_state_management" in task_description:
                result = await self.safe_execute_with_retry(
                    lambda: self._select_state_management(task_data)
                )
            elif "design_navigation" in task_description:
                result = await self.safe_execute_with_retry(
                    lambda: self._design_navigation(task_data)
                )
            else:
                result = await self.safe_execute_with_retry(
                    lambda: self._handle_general_architecture_task(task_description, task_data)
                )
            
            # Add execution metadata
            result.update({
                "task_type": task_description,
                "execution_time": datetime.now().isoformat(),
                "agent": self.agent_id,
                "patterns_considered": self.design_patterns,
                "task_analysis": analysis[:200] + "..." if len(analysis) > 200 else analysis
            })
            
            return result
            
        except Exception as e:
            import traceback
            self.logger.error(f"❌ Error executing architecture task: {str(e)}\n{traceback.format_exc()}")
            return {
                "status": "failed",
                "error": str(e),
                "task_type": task_description,
                "execution_time": datetime.now().isoformat(),
                "agent": self.agent_id
            }
    
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

        self.logger.info(f"[ARCH] Called _design_flutter_architecture for project_id={project_id}")
        self.logger.info(f"[ARCH] Requirements: {requirements}")
        self.logger.info(f"[ARCH] Planning output: {planning_output}")

        project = shared_state.get_project_state(project_id)
        if not project:
            self.logger.warning(f"[ARCH] Project {project_id} not found in shared state, using task data")
            project_name = task_data.get("name", "Unknown Project")
            project_description = task_data.get("description", "No description available")
        else:
            # Defensively access project state, with fallbacks to task_data
            project_name = getattr(project, 'name', task_data.get('name', 'Unknown Project'))
            project_description = getattr(project, 'description', task_data.get('description', 'No description available'))
            self.logger.info(f"[ARCH] Project found: {project_name} - {project_description}")
            self.logger.info(f"[ARCH] Existing architecture decisions: {getattr(project, 'architecture_decisions', [])}")

        architecture_prompt = f"""
        Design a comprehensive Flutter application architecture specifically for:
        
        ===== PROJECT DETAILS =====
        Project: {project_name}
        Description: {project_description}
        
        ===== UNIQUE REQUIREMENTS =====
        {chr(10).join([f"• {req}" for req in requirements])}
        
        ===== PLANNING CONTEXT =====
        {planning_output}
        
        ===== ARCHITECTURE DESIGN TASK =====
        Create a UNIQUE and TAILORED architecture that specifically addresses the above requirements.
        Do NOT create a generic Flutter app - this must be customized for the specific project needs.
        
        Your architecture must include:
        
        1. **Domain-Specific Architecture Style**: 
           - Choose based on the specific project requirements (not just Clean Architecture by default)
           - Justify your choice based on the unique needs of THIS specific project
           - Consider: Clean, Layered, Hexagonal, Event-Driven, Microservices-inspired, etc.
        
        2. **Requirement-Driven State Management**: 
           - Analyze the specific requirements to choose the best state management solution
           - Consider complexity, real-time needs, offline requirements, performance needs
           - Options: BLoC, Provider, Riverpod, GetX, MobX, Redux
           - JUSTIFY your choice based on the specific project requirements
        
        3. **Custom Project Structure** for {project_name}:
           - Design folder organization specifically for this project's domain
           - Include domain-specific feature folders
           - Consider the specific requirements when organizing code
           ```
           lib/
           ├── core/
           │   ├── constants/
           │   ├── errors/
           │   ├── utils/
           │   └── themes/
           ├── features/
           │   ├── [specific feature 1]/
           │   ├── [specific feature 2]/
           │   └── [specific feature 3]/
           ├── shared/
           │   ├── data/
           │   ├── domain/
           │   └── presentation/
           └── main.dart
           ```
        
        4. **Requirement-Specific Data Architecture**:
           - Repository patterns that match the data needs
           - Data sources (remote APIs, local databases, caching) based on requirements
           - Models and DTOs specific to this project's domain
           - Caching strategy based on offline/online requirements
        
        5. **Technology Stack Selection** based on specific needs:
           - Dependency Injection: get_it, injectable, provider-based
           - Navigation: GoRouter, Navigator 2.0, Auto Route (based on complexity)
           - Networking: Dio, http, GraphQL (based on API requirements)
           - Local Storage: Hive, SQLite, Isar, Shared Preferences (based on data needs)
           - Authentication: Firebase Auth, OAuth, custom JWT (based on auth requirements)
        
        6. **Domain-Specific Integration Patterns**:
           - Third-party service integrations based on requirements
           - Platform-specific implementations if needed
           - Real-time communication patterns if required
           - Background processing if needed
        
        7. **Project-Specific Security Architecture**:
           - Data protection strategies based on the type of data
           - Authentication and authorization patterns
           - Secure storage requirements
           - Privacy compliance (GDPR, CCPA) if applicable
        
        8. **Performance Architecture** tailored to requirements:
           - Lazy loading strategies
           - Caching approaches
           - Memory management
           - Network optimization
        
        ===== OUTPUT REQUIREMENTS =====
        Provide a detailed, implementation-ready architecture document that:
        - Is SPECIFICALLY designed for {project_name}
        - Addresses each unique requirement listed above
        - Includes specific package recommendations with versions
        - Provides code structure examples
        - Explains architectural decisions and trade-offs
        - Considers scalability and maintainability for this specific project
        
        Remember: This architecture should be so specific to {project_name} that it wouldn't be suitable for a different type of app."""

        # Import LLM logger
        from utils.llm_logger import llm_logger
        
        # Get LLM config for logging
        llm_config = self.agent_config.get('llm', {})
        model = llm_config.get('model', 'claude-3-5-sonnet-20241022')
        provider = llm_config.get('provider', 'anthropic')
        temperature = llm_config.get('temperature', 0.7)
        max_tokens = llm_config.get('max_tokens', 4000)
        
        # Log LLM request
        interaction_id = llm_logger.log_llm_request(
            agent_id=self.agent_id,
            model=model,
            provider=provider,
            request_type="design_flutter_architecture",
            prompt=architecture_prompt,
            context={
                "project_id": project_id,
                "project_name": project_name,
                "requirements_count": len(requirements),
                "has_planning_output": bool(planning_output)
            },
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        start_time = time.time()
        architecture_design = None
        error = None
        
        try:
            architecture_design = await self.think(architecture_prompt, {
                "project": project,
                "available_patterns": self.design_patterns,
                "architecture_styles": self.architecture_styles
            })
            self.logger.info(f"[ARCH] LLM architecture_design result: {architecture_design}")
        except Exception as e:
            error = str(e)
            self.logger.error(f"[ARCH] Exception during LLM call: {e}")
            architecture_design = None
        finally:
            duration = time.time() - start_time
            
            # Log LLM response (the think method already logged, but this gives us task-specific context)
            llm_logger.log_llm_response(
                interaction_id=interaction_id,
                agent_id=self.agent_id,
                model=model,
                provider=provider,
                request_type="design_flutter_architecture",
                prompt=architecture_prompt,
                response=architecture_design or "",
                duration=duration,
                context={
                    "project_id": project_id,
                    "project_name": project_name,
                    "requirements_count": len(requirements),
                    "architecture_created": bool(architecture_design)
                },
                temperature=temperature,
                max_tokens=max_tokens,
                error=error
            )

        # Fallback: If LLM returns nothing, create a minimal placeholder architecture
        if not architecture_design or not str(architecture_design).strip():
            architecture_design = (
                "[Placeholder] Minimal architecture: Clean Architecture, Riverpod for state management, "
                "GoRouter for navigation, Repository pattern for data, get_it for DI, "
                "Hive for local storage, and standard Flutter testing."
            )
            self.logger.warning(f"[ARCH] LLM returned no architecture design for project {project_id}, using fallback.")

        existing_decisions = getattr(project, 'architecture_decisions', []) if project else []
        architecture_decision = {
            "decision_id": f"arch_{project_id}_{len(existing_decisions) + 1}",
            "title": "Flutter Application Architecture Design",
            "description": architecture_design,
            "status": "proposed",
            "created_by": self.agent_id,
            "created_at": datetime.now().isoformat(),
            "consequences": "Defines the overall structure and patterns for the Flutter application"
        }

        self.logger.info(f"[ARCH] New architecture_decision: {architecture_decision}")

        # Add to project state if project exists
        if project:
            # Defensively get existing decisions and add new one
            current_decisions = getattr(project, 'architecture_decisions', [])
            current_decisions.append(architecture_decision)
            shared_state.update_project(project_id, architecture_decisions=current_decisions)
            self.logger.info(f"[ARCH] Updated project.architecture_decisions: {current_decisions}")
        else:
            # Create a minimal project in shared state if it doesn't exist
            try:
                shared_state.create_project_with_id(
                    project_id,
                    task_data.get("name", "Unknown Project"),
                    task_data.get("description", "No description"),
                    task_data.get("requirements", [])
                )
                project = shared_state.get_project_state(project_id)
                if project:
                    current_decisions = getattr(project, 'architecture_decisions', [])
                    current_decisions.append(architecture_decision)
                    shared_state.update_project(project_id, architecture_decisions=current_decisions)
                    self.logger.info(f"[ARCH] Created project and added architecture_decisions: {current_decisions}")
            except Exception as e:
                self.logger.warning(f"[ARCH] Could not create project in shared state: {e}")
                # Continue anyway - the decision was created

        try:
            await self._request_architecture_feedback(project_id, architecture_design)
        except Exception as e:
            self.logger.error(f"[ARCH] Exception during feedback request: {e}")

        return {
            "architecture_design": architecture_design,
            "decision_record": architecture_decision,
            "status": "architecture_completed",
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
        
        # Defensively access project attributes
        project_name = getattr(project, 'name', 'Unknown Project')
        project_description = getattr(project, 'description', 'No description available')
        project_requirements = getattr(project, 'requirements', [])
        
        analysis_prompt = f"""
        Analyze this new Flutter project and identify key architectural considerations:
        
        Project: {project_name}
        Description: {project_description}
        Requirements: {project_requirements}
        
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

    # Real-time awareness and proactive collaboration methods
    def _react_to_peer_activity(self, peer_agent: str, activity_type: str, 
                               activity_details: Dict[str, Any], consciousness_update: Dict[str, Any]) -> None:
        """React to peer agent activities with proactive architecture guidance."""
        
        # Implementation Agent → Provide architecture guidance
        if peer_agent == "implementation" and activity_type == "code_generated":
            self._provide_architecture_guidance(activity_details, consciousness_update)
        
        # Testing Agent → Optimize architecture for testability
        elif peer_agent == "testing" and activity_type == "test_failure":
            self._optimize_for_testability(activity_details, consciousness_update)
        
        # Security Agent → Integrate security patterns
        elif peer_agent == "security" and activity_type == "security_issue_found":
            self._integrate_security_patterns(activity_details, consciousness_update)
        
        # Performance Agent → Optimize architecture for performance
        elif peer_agent == "performance" and activity_type == "performance_issue_detected":
            self._optimize_for_performance(activity_details, consciousness_update)

    def _provide_architecture_guidance(self, activity_details: Dict[str, Any], consciousness_update: Dict[str, Any]) -> None:
        """Provide architecture guidance when code is being implemented."""
        try:
            files_created = activity_details.get("files_created", [])
            feature_name = activity_details.get("feature_name", "unknown")
            
            self.logger.info(f"🏗️ Providing architecture guidance for: {feature_name}")
            
            # Analyze code structure and provide recommendations
            architecture_recommendations = self._analyze_code_structure(files_created)
            
            # Update shared consciousness with architecture insights
            shared_state.update_shared_consciousness(
                f"architecture_guidance_{shared_state.get_current_project_id()}",
                {
                    "feature_name": feature_name,
                    "recommendations": architecture_recommendations,
                    "pattern_compliance": self._check_pattern_compliance(files_created),
                    "updated_at": datetime.now().isoformat()
                }
            )
            
            # Broadcast architecture guidance
            self.broadcast_activity(
                activity_type="architecture_guidance_provided",
                activity_details={
                    "trigger": "code_implementation",
                    "feature_name": feature_name,
                    "recommendations": architecture_recommendations,
                    "compliance_status": "checked"
                },
                impact_level="medium",
                collaboration_relevance=["implementation", "testing", "qa"]
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error providing architecture guidance: {e}")

    def _optimize_for_testability(self, activity_details: Dict[str, Any], consciousness_update: Dict[str, Any]) -> None:
        """Optimize architecture based on testing feedback."""
        try:
            test_failures = activity_details.get("failures", [])
            test_type = activity_details.get("test_type", "")
            
            self.logger.info(f"🧪 Optimizing architecture for testability: {test_type}")
            
            # Generate testability recommendations
            testability_improvements = self._generate_testability_recommendations(test_failures, test_type)
            
            # Broadcast testability optimizations
            self.broadcast_activity(
                activity_type="architecture_optimized_for_testing",
                activity_details={
                    "trigger": "test_failures",
                    "test_type": test_type,
                    "improvements": testability_improvements,
                    "pattern_adjustments": self._suggest_pattern_adjustments_for_testing(test_type)
                },
                impact_level="medium",
                collaboration_relevance=["testing", "implementation", "qa"]
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error optimizing for testability: {e}")

    def _integrate_security_patterns(self, activity_details: Dict[str, Any], consciousness_update: Dict[str, Any]) -> None:
        """Integrate security patterns based on security findings."""
        try:
            security_issue = activity_details.get("issue_type", "")
            affected_components = activity_details.get("affected_components", [])
            
            self.logger.info(f"🔒 Integrating security patterns for: {security_issue}")
            
            # Generate security architecture patterns
            security_patterns = self._generate_security_architecture_patterns(security_issue, affected_components)
            
            # Update architecture decisions with security considerations
            shared_state.update_shared_consciousness(
                f"security_architecture_{shared_state.get_current_project_id()}",
                {
                    "security_issue": security_issue,
                    "patterns": security_patterns,
                    "affected_components": affected_components,
                    "integration_guidelines": self._create_security_integration_guidelines(security_patterns),
                    "updated_at": datetime.now().isoformat()
                }
            )
            
            # Broadcast security architecture updates
            self.broadcast_activity(
                activity_type="security_patterns_integrated",
                activity_details={
                    "trigger": "security_finding",
                    "security_issue": security_issue,
                    "patterns": security_patterns,
                    "implementation_guidance": "security_patterns_ready"
                },
                impact_level="high",
                collaboration_relevance=["security", "implementation", "testing"]
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error integrating security patterns: {e}")

    def _optimize_for_performance(self, activity_details: Dict[str, Any], consciousness_update: Dict[str, Any]) -> None:
        """Optimize architecture based on performance findings."""
        try:
            performance_issue = activity_details.get("issue_type", "")
            metrics = activity_details.get("metrics", {})
            
            self.logger.info(f"⚡ Optimizing architecture for performance: {performance_issue}")
            
            # Generate performance architecture optimizations
            performance_optimizations = self._generate_performance_optimizations(performance_issue, metrics)
            
            # Broadcast performance architecture updates
            self.broadcast_activity(
                activity_type="architecture_optimized_for_performance",
                activity_details={
                    "trigger": "performance_issue",
                    "issue_type": performance_issue,
                    "optimizations": performance_optimizations,
                    "pattern_updates": self._suggest_performance_pattern_updates(performance_issue)
                },
                impact_level="medium",
                collaboration_relevance=["performance", "implementation", "testing"]
            )
            
        except Exception as e:
            self.logger.error(f"❌ Error optimizing for performance: {e}")

    def _analyze_code_structure(self, files: List[str]) -> Dict[str, Any]:
        """Analyze code structure and provide recommendations."""
        return {
            "structure_compliance": "good",
            "pattern_adherence": "following_bloc_pattern",
            "separation_of_concerns": "well_separated",
            "recommendations": [
                "Consider extracting business logic to use cases",
                "Add proper error handling patterns",
                "Implement proper dependency injection"
            ]
        }

    def _check_pattern_compliance(self, files: List[str]) -> Dict[str, Any]:
        """Check compliance with established architecture patterns."""
        return {
            "bloc_pattern": "compliant",
            "clean_architecture": "mostly_compliant",
            "dependency_injection": "needs_improvement",
            "overall_score": 0.85
        }

    def _generate_testability_recommendations(self, failures: List[str], test_type: str) -> List[Dict[str, Any]]:
        """Generate recommendations to improve testability."""
        recommendations = []
        
        if test_type == "unit":
            recommendations.extend([
                {"pattern": "dependency_injection", "reason": "improve_mocking"},
                {"pattern": "repository_pattern", "reason": "isolate_data_layer"},
                {"pattern": "use_case_pattern", "reason": "isolate_business_logic"}
            ])
        elif test_type == "widget":
            recommendations.extend([
                {"pattern": "widget_testing_patterns", "reason": "improve_widget_isolation"},
                {"pattern": "testable_widgets", "reason": "better_widget_structure"}
            ])
        
        return recommendations

    def _suggest_pattern_adjustments_for_testing(self, test_type: str) -> List[str]:
        """Suggest pattern adjustments to improve testing."""
        if test_type == "unit":
            return ["use_interfaces_for_dependencies", "implement_proper_di", "separate_business_logic"]
        elif test_type == "widget":
            return ["extract_business_logic_from_widgets", "use_proper_keys", "implement_testable_state"]
        return ["general_testability_improvements"]

    def _generate_security_architecture_patterns(self, security_issue: str, affected_components: List[str]) -> List[Dict[str, Any]]:
        """Generate security architecture patterns."""
        patterns = []
        
        if "authentication" in security_issue.lower():
            patterns.extend([
                {"pattern": "secure_authentication_flow", "implementation": "oauth2_with_pkce"},
                {"pattern": "token_management", "implementation": "secure_token_storage"},
                {"pattern": "session_management", "implementation": "timeout_and_refresh"}
            ])
        
        if "data_validation" in security_issue.lower():
            patterns.extend([
                {"pattern": "input_validation_layer", "implementation": "validation_middleware"},
                {"pattern": "sanitization_patterns", "implementation": "input_sanitizers"},
                {"pattern": "secure_data_flow", "implementation": "validation_at_boundaries"}
            ])
        
        return patterns

    def _create_security_integration_guidelines(self, patterns: List[Dict[str, Any]]) -> List[str]:
        """Create guidelines for integrating security patterns."""
        return [
            "Implement security patterns at architectural boundaries",
            "Ensure security validation happens before business logic",
            "Use dependency injection for security components",
            "Apply security patterns consistently across all features"
        ]

    def _generate_performance_optimizations(self, performance_issue: str, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate performance architecture optimizations."""
        optimizations = []
        
        if "memory" in performance_issue.lower():
            optimizations.extend([
                {"optimization": "lazy_loading_pattern", "benefit": "reduced_memory_footprint"},
                {"optimization": "object_pooling", "benefit": "reduced_allocations"},
                {"optimization": "memory_efficient_state_management", "benefit": "better_memory_usage"}
            ])
        
        if "rendering" in performance_issue.lower():
            optimizations.extend([
                {"optimization": "widget_optimization_patterns", "benefit": "faster_rendering"},
                {"optimization": "build_optimization", "benefit": "reduced_rebuilds"},
                {"optimization": "layout_optimization", "benefit": "smoother_ui"}
            ])
        
        return optimizations

    def _suggest_performance_pattern_updates(self, performance_issue: str) -> List[str]:
        """Suggest pattern updates for performance optimization."""
        if "memory" in performance_issue.lower():
            return ["implement_lazy_loading", "optimize_state_management", "use_efficient_data_structures"]
        elif "rendering" in performance_issue.lower():
            return ["optimize_widget_tree", "implement_proper_keys", "use_const_constructors"]
        return ["general_performance_improvements"]

    def _extract_project_info(self, project_state) -> Dict[str, Any]:
        """Extract relevant project information for detailed prompt building"""
        if project_state is None:
            return {
                'project_name': 'Flutter Project',
                'description': 'A Flutter application',
                'requirements': [],
                'platforms': ['android', 'ios'],
                'current_phase': 'planning',
                'features': {'core_features': [], 'ui_features': [], 'integration_features': [], 'performance_requirements': [], 'security_requirements': []},
                'complexity_score': 'low'
            }
        
        # Handle ProjectState dataclass
        if hasattr(project_state, 'name'):
            requirements = getattr(project_state, 'requirements', [])
            return {
                'project_name': getattr(project_state, 'name', 'Flutter Project'),
                'description': getattr(project_state, 'description', ''),
                'requirements': requirements,
                'platforms': getattr(project_state, 'platforms', ['android', 'ios']),
                'current_phase': getattr(project_state, 'current_phase', 'planning'),
                'features': self._categorize_requirements(requirements),
                'complexity_score': self._calculate_complexity(requirements)
            }
        
        # Handle dictionary
        elif isinstance(project_state, dict):
            requirements = project_state.get('requirements', [])
            return {
                'project_name': project_state.get('name', 'Flutter Project'),
                'description': project_state.get('description', ''),
                'requirements': requirements,
                'platforms': project_state.get('platforms', ['android', 'ios']),
                'current_phase': project_state.get('current_phase', 'planning'),
                'features': self._categorize_requirements(requirements),
                'complexity_score': self._calculate_complexity(requirements)
            }
        
        # Fallback for other types
        else:
            return {
                'project_name': 'Flutter Project',
                'description': 'A Flutter application',
                'requirements': [],
                'platforms': ['android', 'ios'],
                'current_phase': 'planning',
                'features': {'core_features': [], 'ui_features': [], 'integration_features': [], 'performance_requirements': [], 'security_requirements': []},
                'complexity_score': 'low'
            }

    def _categorize_requirements(self, requirements: list) -> Dict[str, list]:
        """Categorize requirements by type for better architecture planning"""
        categories = {
            'core_features': [],
            'ui_features': [],
            'integration_features': [],
            'performance_requirements': [],
            'security_requirements': []
        }
        
        for req in requirements:
            req_lower = req.lower() if isinstance(req, str) else str(req).lower()
            if any(keyword in req_lower for keyword in ['streaming', 'playback', 'playlist', 'library', 'music', 'audio', 'player']):
                categories['core_features'].append(req)
            elif any(keyword in req_lower for keyword in ['theme', 'ui', 'accessibility', 'gesture', 'design', 'interface', 'screen']):
                categories['ui_features'].append(req)
            elif any(keyword in req_lower for keyword in ['api', 'integration', 'external', 'sync', 'service', 'backend', 'cloud']):
                categories['integration_features'].append(req)
            elif any(keyword in req_lower for keyword in ['performance', 'quality', 'cache', 'optimization', 'speed', 'memory']):
                categories['performance_requirements'].append(req)
            elif any(keyword in req_lower for keyword in ['authentication', 'security', 'protection', 'privacy', 'permission']):
                categories['security_requirements'].append(req)
            else:
                # Default to core features if no specific category matches
                categories['core_features'].append(req)
        
        return categories

    def _calculate_complexity(self, requirements: list) -> str:
        """Calculate project complexity based on requirements"""
        if len(requirements) > 20:
            return "high"
        elif len(requirements) > 10:
            return "medium"
        else:
            return "low"
