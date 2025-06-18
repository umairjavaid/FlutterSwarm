"""
Integration tests for FlutterSwarm system with real agent interactions.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from flutter_swarm import FlutterSwarm
from shared.state import shared_state, AgentStatus


@pytest.mark.integration
class TestFlutterSwarmIntegration:
    """Test suite for FlutterSwarm system integration."""
    
    @pytest.mark.asyncio
    async def test_complete_project_workflow(self, clean_shared_state, mock_anthropic_client, mock_config, mock_tool_manager):
        """Test a complete project creation and build workflow."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            swarm = FlutterSwarm()
            
            # Mock agent methods to avoid actual AI calls
            for agent in swarm.agents.values():
                agent.start = AsyncMock()
                agent.stop = AsyncMock()
                agent.process_message = AsyncMock(return_value={"status": "processed"})
                agent.execute_task = AsyncMock(return_value={"status": "completed"})
            
            # Create a project
            project_id = swarm.create_project(
                name="IntegrationTestApp",
                description="A comprehensive Flutter app for testing",
                requirements=[
                    "User authentication",
                    "Data persistence",
                    "Real-time updates",
                    "Push notifications",
                    "Offline support"
                ],
                features=["auth", "database", "realtime", "notifications", "offline"]
            )
            
            assert project_id is not None
            
            # Verify project was created in shared state
            project = clean_shared_state.get_project_state(project_id)
            assert project is not None
            assert project.name == "IntegrationTestApp"
            assert len(project.requirements) == 5
            
            # Start the swarm briefly
            start_task = asyncio.create_task(swarm.start())
            await asyncio.sleep(0.1)  # Let agents start
            
            assert swarm.is_running
            
            # Verify all agents were started
            for agent in swarm.agents.values():
                agent.start.assert_called_once()
            
            # Mock build progress monitoring
            mock_result = {
                "status": "completed",
                "project_id": project_id,
                "files_created": 15,
                "architecture_decisions": 3,
                "test_results": {"unit": {"status": "passed"}},
                "security_findings": [],
                "performance_metrics": {"load_time": "2.3s"},
                "documentation": ["README.md", "API.md"],
                "deployment_config": {"status": "configured"}
            }
            
            with patch.object(swarm, '_monitor_build_progress', return_value=mock_result):
                # Build the project
                result = await swarm.build_project(
                    project_id,
                    platforms=["android", "ios", "web"],
                    ci_system="github_actions"
                )
                
                assert result["status"] == "completed"
                assert result["project_id"] == project_id
                assert result["files_created"] == 15
                
            # Stop the swarm
            await swarm.stop()
            
            # Verify all agents were stopped
            for agent in swarm.agents.values():
                agent.stop.assert_called_once()
                
            # Clean up
            start_task.cancel()
            try:
                await start_task
            except asyncio.CancelledError:
                pass
    
    @pytest.mark.asyncio
    async def test_agent_coordination_during_build(self, clean_shared_state, mock_anthropic_client, mock_config, mock_tool_manager):
        """Test agent coordination during a build process."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            swarm = FlutterSwarm()
            
            # Mock agents with realistic behavior
            orchestrator = swarm.agents["orchestrator"]
            implementation = swarm.agents["implementation"]
            testing = swarm.agents["testing"]
            
            # Mock orchestrator to coordinate tasks
            async def mock_orchestrator_work():
                clean_shared_state.update_agent_status(
                    "orchestrator", AgentStatus.WORKING, "Planning project", 0.1
                )
                await asyncio.sleep(0.1)
                
                # Send task to implementation
                clean_shared_state.send_message(
                    "orchestrator", "implementation",
                    "TASK_REQUEST",
                    {"task": "create_auth_feature"}
                )
                
                clean_shared_state.update_agent_status(
                    "orchestrator", AgentStatus.COMPLETED, "Planning complete", 1.0
                )
            
            # Mock implementation agent
            async def mock_implementation_work():
                clean_shared_state.update_agent_status(
                    "implementation", AgentStatus.WORKING, "Implementing auth", 0.3
                )
                await asyncio.sleep(0.1)
                
                # Send task to testing
                clean_shared_state.send_message(
                    "implementation", "testing",
                    "COLLABORATION_REQUEST",
                    {"request": "test_auth_feature", "files": ["auth.dart"]}
                )
                
                clean_shared_state.update_agent_status(
                    "implementation", AgentStatus.COMPLETED, "Auth implemented", 1.0
                )
            
            # Mock testing agent
            async def mock_testing_work():
                clean_shared_state.update_agent_status(
                    "testing", AgentStatus.WORKING, "Testing auth", 0.5
                )
                await asyncio.sleep(0.1)
                
                clean_shared_state.update_agent_status(
                    "testing", AgentStatus.COMPLETED, "Tests passed", 1.0
                )
            
            orchestrator.start = mock_orchestrator_work
            implementation.start = mock_implementation_work
            testing.start = mock_testing_work
            
            # Mock other agents
            for agent_id, agent in swarm.agents.items():
                if agent_id not in ["orchestrator", "implementation", "testing"]:
                    agent.start = AsyncMock()
                    agent.stop = AsyncMock()
            
            # Create project
            project_id = swarm.create_project(
                name="CoordinationTest",
                description="Testing agent coordination"
            )
            
            # Start agents
            start_tasks = []
            for agent in swarm.agents.values():
                task = asyncio.create_task(agent.start())
                start_tasks.append(task)
            
            # Wait for coordination to complete
            await asyncio.gather(*start_tasks)
            
            # Verify agent coordination occurred
            # Check that messages were sent between agents
            impl_messages = clean_shared_state.get_messages("implementation")
            test_messages = clean_shared_state.get_messages("testing")
            
            assert len(impl_messages) >= 1  # Received task from orchestrator
            assert len(test_messages) >= 1  # Received collaboration request
            
            # Check final agent states
            agent_states = clean_shared_state.get_agent_states()
            assert agent_states["orchestrator"].status == AgentStatus.COMPLETED
            assert agent_states["implementation"].status == AgentStatus.COMPLETED
            assert agent_states["testing"].status == AgentStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, clean_shared_state, mock_anthropic_client, mock_config, mock_tool_manager):
        """Test error recovery during project build."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            swarm = FlutterSwarm()
            
            # Mock agents for error scenario
            for agent in swarm.agents.values():
                agent.start = AsyncMock()
                agent.stop = AsyncMock()
            
            # Create project
            project_id = swarm.create_project(
                name="ErrorRecoveryTest",
                description="Testing error recovery"
            )
            
            # Simulate an error in implementation agent
            clean_shared_state.update_agent_status(
                "implementation", AgentStatus.ERROR, "Dependency error", 0.2
            )
            
            # Report the issue
            issue_id = clean_shared_state.report_issue(project_id, {
                "reporter_agent": "implementation",
                "type": "dependency",
                "severity": "high",
                "description": "Missing Flutter dependency",
                "affected_files": ["pubspec.yaml"],
                "fix_suggestions": ["Add missing dependency to pubspec.yaml"]
            })
            
            assert issue_id is not None
            
            # Verify issue was recorded
            issues = clean_shared_state.get_project_issues(project_id)
            assert len(issues) == 1
            assert issues[0].severity == "high"
            
            # Mock orchestrator resolving the issue
            success = clean_shared_state.update_issue_status(
                project_id, issue_id, "resolved",
                assigned_agent="orchestrator",
                resolution_notes="Added missing dependency"
            )
            
            assert success is True
            
            # Agent can continue after resolution
            clean_shared_state.update_agent_status(
                "implementation", AgentStatus.WORKING, "Retrying implementation", 0.3
            )
            
            # Get project status to verify recovery
            status = swarm.get_project_status(project_id)
            assert status["agents"]["implementation"]["status"] == "working"
    
    @pytest.mark.asyncio
    async def test_multi_platform_build_coordination(self, clean_shared_state, mock_anthropic_client, mock_config, mock_tool_manager):
        """Test coordination for multi-platform builds."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            swarm = FlutterSwarm()
            
            # Mock DevOps agent for platform-specific tasks
            devops_agent = swarm.agents["devops"]
            
            async def mock_devops_work():
                platforms = ["android", "ios", "web"]
                
                for i, platform in enumerate(platforms):
                    clean_shared_state.update_agent_status(
                        "devops", AgentStatus.WORKING, 
                        f"Building for {platform}", (i + 1) / len(platforms)
                    )
                    await asyncio.sleep(0.05)
                    
                    # Simulate platform-specific build
                    clean_shared_state.send_message(
                        "devops", "orchestrator",
                        "STATUS_UPDATE",
                        {"platform": platform, "status": "build_complete"}
                    )
                
                clean_shared_state.update_agent_status(
                    "devops", AgentStatus.COMPLETED, "All platforms built", 1.0
                )
            
            devops_agent.start = mock_devops_work
            
            # Mock other agents
            for agent_id, agent in swarm.agents.items():
                if agent_id != "devops":
                    agent.start = AsyncMock()
                    agent.stop = AsyncMock()
            
            # Create project
            project_id = swarm.create_project(
                name="MultiPlatformTest",
                description="Testing multi-platform builds"
            )
            
            # Start DevOps agent
            await devops_agent.start()
            
            # Check that platform builds were coordinated
            orchestrator_messages = clean_shared_state.get_messages("orchestrator")
            platform_messages = [
                msg for msg in orchestrator_messages 
                if msg.content.get("status") == "build_complete"
            ]
            
            assert len(platform_messages) == 3  # android, ios, web
            
            platforms_built = [msg.content["platform"] for msg in platform_messages]
            assert "android" in platforms_built
            assert "ios" in platforms_built
            assert "web" in platforms_built
    
    @pytest.mark.asyncio
    async def test_performance_monitoring_integration(self, clean_shared_state, mock_anthropic_client, mock_config, mock_tool_manager):
        """Test performance monitoring during build process."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            swarm = FlutterSwarm()
            
            # Mock performance agent
            performance_agent = swarm.agents["performance"]
            
            async def mock_performance_monitoring():
                metrics = [
                    {"metric": "build_time", "value": "45s"},
                    {"metric": "bundle_size", "value": "2.3MB"},
                    {"metric": "startup_time", "value": "1.2s"}
                ]
                
                for metric in metrics:
                    clean_shared_state.update_agent_status(
                        "performance", AgentStatus.WORKING,
                        f"Monitoring {metric['metric']}", 0.5
                    )
                    await asyncio.sleep(0.05)
                    
                    # Report metric
                    clean_shared_state.send_message(
                        "performance", "orchestrator",
                        "STATUS_UPDATE",
                        {"metric_update": metric}
                    )
                
                clean_shared_state.update_agent_status(
                    "performance", AgentStatus.COMPLETED, "Monitoring complete", 1.0
                )
            
            performance_agent.start = mock_performance_monitoring
            
            # Mock other agents
            for agent_id, agent in swarm.agents.items():
                if agent_id != "performance":
                    agent.start = AsyncMock()
                    agent.stop = AsyncMock()
            
            # Create project
            project_id = swarm.create_project(
                name="PerformanceTest",
                description="Testing performance monitoring"
            )
            
            # Start performance monitoring
            await performance_agent.start()
            
            # Check that performance metrics were reported
            orchestrator_messages = clean_shared_state.get_messages("orchestrator")
            metric_messages = [
                msg for msg in orchestrator_messages 
                if "metric_update" in msg.content
            ]
            
            assert len(metric_messages) == 3
            
            # Verify specific metrics were reported
            reported_metrics = [msg.content["metric_update"]["metric"] for msg in metric_messages]
            assert "build_time" in reported_metrics
            assert "bundle_size" in reported_metrics
            assert "startup_time" in reported_metrics
    
    def test_project_state_persistence(self, clean_shared_state):
        """Test that project state persists correctly through operations."""
        # Create multiple projects
        project1_id = clean_shared_state.create_project(
            "Project1", "First test project", ["req1", "req2"]
        )
        project2_id = clean_shared_state.create_project(
            "Project2", "Second test project", ["req3", "req4"]
        )
        
        # Add files to projects
        clean_shared_state.add_project_file(project1_id, "main.dart", "content1")
        clean_shared_state.add_project_file(project2_id, "app.dart", "content2")
        
        # Update project phases
        clean_shared_state.update_project_phase(project1_id, "implementation", 0.5)
        clean_shared_state.update_project_phase(project2_id, "testing", 0.8)
        
        # Verify state persistence
        project1 = clean_shared_state.get_project_state(project1_id)
        project2 = clean_shared_state.get_project_state(project2_id)
        
        assert project1.name == "Project1"
        assert project1.current_phase == "implementation"
        assert project1.progress == 0.5
        assert "main.dart" in project1.files_created
        
        assert project2.name == "Project2"
        assert project2.current_phase == "testing"
        assert project2.progress == 0.8
        assert "app.dart" in project2.files_created
