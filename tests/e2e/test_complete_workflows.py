"""
End-to-end tests for complete FlutterSwarm workflows.
Updated for LangGraph-based implementation.
"""

import pytest
import asyncio
import tempfile
from unittest.mock import patch, MagicMock, AsyncMock

from flutter_swarm import FlutterSwarm


@pytest.mark.e2e
@pytest.mark.slow
class TestFlutterSwarmE2E:
    """End-to-end test suite for FlutterSwarm."""
    
    @pytest.mark.asyncio
    async def test_complete_app_development_workflow(self):
        """Test complete app development from start to finish using LangGraph."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            swarm = FlutterSwarm(enable_monitoring=False)
            
            # Phase 1: Project Creation
            project_id = swarm.create_project(
                name="TaskMaster",
                description="A comprehensive task management application with collaboration features",
                requirements=[
                    "User authentication with email/password and social login",
                    "Task CRUD operations with categories and priorities",
                    "Real-time collaboration with team members",
                    "Offline synchronization capabilities",
                    "Push notifications for task updates",
                    "File attachments for tasks",
                    "Time tracking and reporting",
                    "Dark/light theme support",
                    "Multi-language support",
                    "Data export functionality"
                ],
                features=[
                    "auth", "crud", "realtime", "offline", "notifications",
                    "attachments", "time_tracking", "theming", "i18n", "export"
                ]
            )
            
            assert project_id is not None
            
            # Phase 2: Start the swarm
            start_task = asyncio.create_task(swarm.start())
            await asyncio.sleep(0.2)  # Let agents start and begin coordination
            
            # Phase 3: Build the project
            mock_result = await self._create_comprehensive_build_result(project_id)
            
            with patch.object(swarm, '_monitor_build_progress', return_value=mock_result):
                build_result = await swarm.build_project(
                    project_id,
                    platforms=["android", "ios", "web"],
                    ci_system="github_actions"
                )
            
            # Phase 4: Verify comprehensive results
            assert build_result["status"] == "completed"
            assert build_result["files_created"] >= 25  # Comprehensive app
            assert build_result["architecture_decisions"] >= 5
            assert "test_results" in build_result
            assert "security_findings" in build_result
            assert "performance_metrics" in build_result
            assert "documentation" in build_result
            assert "deployment_config" in build_result
            
            # Phase 5: Verify agent collaboration occurred
            await self._verify_agent_collaboration(clean_shared_state)
            
            # Phase 6: Check project quality
            await self._verify_project_quality(swarm, project_id, clean_shared_state)
            
            # Phase 7: Stop the swarm
            await swarm.stop()
            
            # Clean up
            start_task.cancel()
            try:
                await start_task
            except asyncio.CancelledError:
                pass
    
    async def _setup_realistic_agent_mocks(self, swarm, clean_shared_state):
        from shared.state import MessageType
        # Orchestrator Agent - Coordinates everything
        async def orchestrator_workflow():
            clean_shared_state.update_agent_status(
                "orchestrator", AgentStatus.WORKING, "Planning project architecture", 0.1
            )
            await asyncio.sleep(0.1)
            # Assign architecture task
            clean_shared_state.send_message(
                "orchestrator", "architecture", MessageType.TASK_REQUEST,
                {"task": "design_app_architecture", "requirements": "comprehensive_task_app"}
            )
            await asyncio.sleep(0.1)
            clean_shared_state.update_agent_status(
                "orchestrator", AgentStatus.WORKING, "Coordinating implementation", 0.5
            )
            # Assign implementation tasks
            clean_shared_state.send_message(
                "orchestrator", "implementation", MessageType.TASK_REQUEST,
                {"task": "implement_core_features", "phase": "development"}
            )
            await asyncio.sleep(0.1)
            clean_shared_state.update_agent_status(
                "orchestrator", AgentStatus.COMPLETED, "Project coordination complete", 1.0
            )
        # Architecture Agent - Designs system
        async def architecture_workflow():
            await asyncio.sleep(0.05)
            clean_shared_state.update_agent_status(
                "architecture", AgentStatus.WORKING, "Designing app architecture", 0.2
            )
            await asyncio.sleep(0.1)
            clean_shared_state.send_message(
                "architecture", "implementation", MessageType.COLLABORATION_REQUEST,
                {"architecture_decisions": [
                    {"pattern": "BLoC", "rationale": "State management"},
                    {"pattern": "Repository", "rationale": "Data layer abstraction"},
                    {"pattern": "Clean Architecture", "rationale": "Maintainability"}
                ]}
            )
            clean_shared_state.update_agent_status(
                "architecture", AgentStatus.COMPLETED, "Architecture design complete", 1.0
            )
        # Implementation Agent - Writes code
        async def implementation_workflow():
            await asyncio.sleep(0.1)
            clean_shared_state.update_agent_status(
                "implementation", AgentStatus.WORKING, "Implementing core features", 0.3
            )
            files_created = [
                "lib/main.dart", "lib/app.dart", "lib/core/theme.dart",
                "lib/features/auth/auth.dart", "lib/features/tasks/tasks.dart",
                "lib/features/collaboration/collaboration.dart"
            ]
            for file in files_created:
                clean_shared_state.add_project_file(
                    clean_shared_state._current_project_id, file, f"// {file} content"
                )
            await asyncio.sleep(0.1)
            clean_shared_state.send_message(
                "implementation", "testing", MessageType.COLLABORATION_REQUEST,
                {"request": "test_implementation", "files": files_created}
            )
            clean_shared_state.send_message(
                "implementation", "security", MessageType.COLLABORATION_REQUEST,
                {"request": "security_review", "auth_files": ["lib/features/auth/auth.dart"]}
            )
            clean_shared_state.update_agent_status(
                "implementation", AgentStatus.COMPLETED, "Core implementation complete", 1.0
            )
        # Testing Agent - Creates and runs tests
        async def testing_workflow():
            await asyncio.sleep(0.15)
            clean_shared_state.update_agent_status(
                "testing", AgentStatus.WORKING, "Creating comprehensive tests", 0.4
            )
            await asyncio.sleep(0.1)
            test_results = {
                "unit_tests": {"passed": 25, "failed": 0, "coverage": "92%"},
                "widget_tests": {"passed": 15, "failed": 0, "coverage": "88%"},
                "integration_tests": {"passed": 8, "failed": 0, "coverage": "85%"}
            }
            clean_shared_state.send_message(
                "testing", "orchestrator", MessageType.STATUS_UPDATE,
                {"test_results": test_results}
            )
            clean_shared_state.update_agent_status(
                "testing", AgentStatus.COMPLETED, "All tests passing", 1.0
            )
        # Security Agent - Reviews security
        async def security_workflow():
            await asyncio.sleep(0.15)
            clean_shared_state.update_agent_status(
                "security", AgentStatus.WORKING, "Conducting security review", 0.4
            )
            await asyncio.sleep(0.1)
            security_findings = [
                {"type": "info", "message": "Authentication implementation follows best practices"},
                {"type": "warning", "message": "Consider implementing rate limiting for API calls"}
            ]
            clean_shared_state.send_message(
                "security", "orchestrator", MessageType.STATUS_UPDATE,
                {"security_findings": security_findings}
            )
            clean_shared_state.update_agent_status(
                "security", AgentStatus.COMPLETED, "Security review complete", 1.0
            )
        swarm.agents["orchestrator"].start = orchestrator_workflow
        swarm.agents["architecture"].start = architecture_workflow
        swarm.agents["implementation"].start = implementation_workflow
        swarm.agents["testing"].start = testing_workflow
        swarm.agents["security"].start = security_workflow
        for agent_id in ["devops", "documentation", "performance", "quality_assurance"]:
            async def simple_workflow(aid=agent_id):
                clean_shared_state.update_agent_status(
                    aid, AgentStatus.WORKING, f"{aid} processing", 0.5
                )
                await asyncio.sleep(0.1)
                clean_shared_state.update_agent_status(
                    aid, AgentStatus.COMPLETED, f"{aid} complete", 1.0
                )
            swarm.agents[agent_id].start = simple_workflow
            swarm.agents[agent_id].stop = AsyncMock()
    
    async def _create_comprehensive_build_result(self, project_id):
        """Create a comprehensive build result for testing."""
        return {
            "status": "completed",
            "project_id": project_id,
            "files_created": 28,
            "architecture_decisions": 6,
            "test_results": {
                "unit": {"status": "passed", "tests": 25, "coverage": "92%"},
                "widget": {"status": "passed", "tests": 15, "coverage": "88%"},
                "integration": {"status": "passed", "tests": 8, "coverage": "85%"}
            },
            "security_findings": [
                {"type": "info", "message": "No critical security issues found"},
                {"type": "warning", "message": "Consider implementing rate limiting"}
            ],
            "performance_metrics": {
                "build_time": "2m 45s",
                "app_size": "8.2 MB",
                "startup_time": "1.8s",
                "memory_usage": "45 MB"
            },
            "documentation": [
                "README.md", "API_DOCUMENTATION.md", "ARCHITECTURE.md",
                "DEPLOYMENT_GUIDE.md", "USER_MANUAL.md"
            ],
            "deployment_config": {
                "status": "configured",
                "platforms": ["android", "ios", "web"],
                "ci_cd": "github_actions",
                "environments": ["dev", "staging", "prod"]
            },
            "code_quality": {
                "lint_score": "A+",
                "complexity_score": "B",
                "maintainability_index": 85
            }
        }
    
    async def _verify_agent_collaboration(self, clean_shared_state):
        """Verify that agents collaborated effectively."""
        # Check that messages were exchanged
        orchestrator_messages = clean_shared_state.get_messages("orchestrator")
        implementation_messages = clean_shared_state.get_messages("implementation")
        testing_messages = clean_shared_state.get_messages("testing")
        security_messages = clean_shared_state.get_messages("security")
        
        # Orchestrator should have received status updates
        assert len(orchestrator_messages) >= 2
        
        # Implementation should have received tasks
        assert len(implementation_messages) >= 2
        
        # Testing should have received collaboration requests
        assert len(testing_messages) >= 1
        
        # Security should have received collaboration requests
        assert len(security_messages) >= 1
        
        # Check agent final states
        agent_states = clean_shared_state.get_agent_states()
        key_agents = ["orchestrator", "architecture", "implementation", "testing", "security"]
        
        for agent_id in key_agents:
            if agent_id in agent_states:
                assert agent_states[agent_id].status == AgentStatus.COMPLETED
    
    async def _verify_project_quality(self, swarm, project_id, clean_shared_state):
        """Verify the quality of the generated project."""
        project = clean_shared_state.get_project_state(project_id)
        
        # Check project completeness
        assert project.name == "TaskMaster"
        assert len(project.requirements) == 10  # All requirements preserved
        assert len(project.files_created) >= 6   # Core files created
        
        # Verify project status
        status = swarm.get_project_status(project_id)
        assert "project" in status
        assert "agents" in status
        assert status["project"]["name"] == "TaskMaster"
        
        # Check for issues
        issues = clean_shared_state.get_project_issues(project_id)
        # Should have minimal critical issues
        critical_issues = [issue for issue in issues if issue.severity == "critical"]
        assert len(critical_issues) == 0
    
    @pytest.mark.asyncio
    async def test_multi_project_workflow(
        self, 
        clean_shared_state, 
        mock_anthropic_client, 
        mock_config, 
        mock_tool_manager
    ):
        """Test handling multiple projects simultaneously."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            swarm = FlutterSwarm()
            
            # Create multiple projects
            projects = []
            project_names = ["QuickNote", "ExpenseTracker", "FitnessApp"]
            
            for name in project_names:
                project_id = swarm.create_project(
                    name=name,
                    description=f"A {name.lower()} application",
                    requirements=[f"{name} core functionality", "User interface", "Data persistence"]
                )
                projects.append(project_id)
            
            # Verify all projects were created
            assert len(projects) == 3
            for project_id in projects:
                project = clean_shared_state.get_project_state(project_id)
                assert project is not None
                assert project.name in project_names
    
    @pytest.mark.asyncio
    async def test_error_recovery_e2e(
        self, 
        clean_shared_state, 
        mock_anthropic_client, 
        mock_config, 
        mock_tool_manager
    ):
        """Test end-to-end error recovery workflow."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            swarm = FlutterSwarm()
            
            # Mock agents with error scenarios
            async def error_prone_implementation():
                clean_shared_state.update_agent_status(
                    "implementation", AgentStatus.WORKING, "Starting implementation", 0.1
                )
                await asyncio.sleep(0.05)
                
                # Simulate error
                clean_shared_state.update_agent_status(
                    "implementation", AgentStatus.ERROR, "Dependency conflict detected", 0.2
                )
                
                # Report issue
                clean_shared_state.report_issue(
                    clean_shared_state._current_project_id,
                    {
                        "reporter_agent": "implementation",
                        "type": "dependency",
                        "severity": "high",
                        "description": "Conflicting package versions",
                        "affected_files": ["pubspec.yaml"],
                        "fix_suggestions": ["Update package versions", "Use dependency overrides"]
                    }
                )
                
                await asyncio.sleep(0.05)
                
                # Simulate recovery
                clean_shared_state.update_agent_status(
                    "implementation", AgentStatus.WORKING, "Resolving dependencies", 0.5
                )
                await asyncio.sleep(0.05)
                
                clean_shared_state.update_agent_status(
                    "implementation", AgentStatus.COMPLETED, "Dependencies resolved", 1.0
                )
            
            swarm.agents["implementation"].start = error_prone_implementation
            
            # Mock other agents
            for agent_id, agent in swarm.agents.items():
                if agent_id != "implementation":
                    agent.start = AsyncMock()
                    agent.stop = AsyncMock()
            
            # Create project
            project_id = swarm.create_project(
                name="ErrorRecoveryTest",
                description="Testing error recovery"
            )
            
            # Start implementation agent
            await swarm.agents["implementation"].start()
            
            # Verify error was reported and recovered
            issues = clean_shared_state.get_project_issues(project_id)
            assert len(issues) >= 1
            
            error_issue = next((issue for issue in issues if issue.severity == "high"), None)
            assert error_issue is not None
            assert "dependency" in error_issue.description.lower()
            
            # Verify agent recovered
            agent_state = clean_shared_state.get_agent_state("implementation")
            assert agent_state.status == AgentStatus.COMPLETED
    
    @pytest.mark.asyncio 
    async def test_performance_under_load(
        self, 
        clean_shared_state, 
        mock_anthropic_client, 
        mock_config, 
        mock_tool_manager
    ):
        """Test system performance under load."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            swarm = FlutterSwarm()
            
            # Mock agents for concurrent operations
            for agent in swarm.agents.values():
                agent.start = AsyncMock()
                agent.stop = AsyncMock()
            
            # Create multiple projects concurrently
            async def create_project_with_delay(name_suffix):
                await asyncio.sleep(0.01 * int(name_suffix))  # Stagger creation
                return swarm.create_project(
                    name=f"LoadTest{name_suffix}",
                    description=f"Load testing project {name_suffix}",
                    requirements=[f"Requirement {name_suffix}.1", f"Requirement {name_suffix}.2"]
                )
            
            # Create 10 projects concurrently
            project_tasks = [
                asyncio.create_task(create_project_with_delay(str(i)))
                for i in range(10)
            ]
            
            project_ids = await asyncio.gather(*project_tasks)
            
            # Verify all projects were created successfully
            assert len(project_ids) == 10
            for project_id in project_ids:
                assert project_id is not None
                project = clean_shared_state.get_project_state(project_id)
                assert project is not None
            
            # Simulate concurrent agent operations
            async def concurrent_agent_work(agent_id, iterations=5):
                for i in range(iterations):
                    clean_shared_state.update_agent_status(
                        agent_id, AgentStatus.WORKING, f"Task {i}", i / iterations
                    )
                    await asyncio.sleep(0.01)
                clean_shared_state.update_agent_status(
                    agent_id, AgentStatus.COMPLETED, "All tasks complete", 1.0
                )
            
            # Register agents and run concurrent operations
            agent_ids = list(swarm.agents.keys())[:5]  # Use first 5 agents
            for agent_id in agent_ids:
                clean_shared_state.register_agent(agent_id, ["capability"])
            
            agent_tasks = [
                asyncio.create_task(concurrent_agent_work(agent_id))
                for agent_id in agent_ids
            ]
            
            await asyncio.gather(*agent_tasks)
            
            # Verify system remained stable
            agent_states = clean_shared_state.get_agent_states()
            for agent_id in agent_ids:
                assert agent_states[agent_id].status == AgentStatus.COMPLETED
