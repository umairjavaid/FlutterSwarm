"""
End-to-end tests for complete FlutterSwarm workflows.
"""

import pytest
import asyncio
import tempfile
import shutil
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

from flutter_swarm import FlutterSwarm
from cli import FlutterSwarmCLI
from tests.mocks.mock_implementations import (
    MockAgent, MockToolManager, MockAnthropicClient, 
    MockConfigManager, create_mock_build_result
)
from tests.fixtures.test_constants import SAMPLE_PROJECT_DATA, TEST_CONFIG_DATA


@pytest.mark.e2e
class TestCompleteWorkflows:
    """End-to-end test suite for complete FlutterSwarm workflows."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for E2E tests."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def mock_e2e_environment(self, temp_workspace):
        """Mock complete E2E environment."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}), \
             patch('langchain_anthropic.ChatAnthropic') as mock_anthropic, \
             patch('tools.ToolManager') as mock_tool_manager_class, \
             patch('config.config_manager.get_config') as mock_get_config:
            
            # Mock Anthropic client
            mock_client = MockAnthropicClient()
            mock_anthropic.return_value = mock_client
            
            # Mock tool manager
            mock_tool_manager = MockToolManager()
            mock_tool_manager_class.return_value = mock_tool_manager
            
            # Mock configuration
            mock_config = MockConfigManager(TEST_CONFIG_DATA)
            mock_get_config.return_value = mock_config
            
            yield {
                'workspace': temp_workspace,
                'anthropic': mock_client,
                'tool_manager': mock_tool_manager,
                'config': mock_config
            }
    
    @pytest.mark.asyncio
    async def test_complete_todo_app_workflow(self, mock_e2e_environment):
        """Test complete workflow for creating a todo application."""
        workspace = mock_e2e_environment['workspace']
        
        # Initialize FlutterSwarm
        swarm = FlutterSwarm()
        
        # Create todo app project
        project_data = SAMPLE_PROJECT_DATA["simple_todo"]
        project_id = swarm.create_project(
            name=project_data["name"],
            description=project_data["description"],
            requirements=project_data["requirements"],
            features=project_data["features"]
        )
        
        assert project_id is not None
        
        # Mock agent behaviors for the workflow
        for agent in swarm.agents.values():
            agent.start = AsyncMock()
            agent.stop = AsyncMock()
            agent._agent_loop = AsyncMock()
            
        # Start the swarm
        start_task = asyncio.create_task(swarm.start())
        await asyncio.sleep(0.1)  # Let agents initialize
        
        # Build the project
        with patch.object(swarm, '_monitor_build_progress') as mock_monitor:
            mock_monitor.return_value = create_mock_build_result(
                status="completed",
                files_created=12,
                has_issues=False
            )
            
            build_result = await swarm.build_project(
                project_id,
                platforms=project_data["platforms"]
            )
        
        # Verify build completion
        assert build_result["status"] == "completed"
        assert build_result["files_created"] == 12
        assert len(build_result["security_findings"]) == 0
        
        # Stop the swarm
        await swarm.stop()
        
        # Verify all agents were stopped
        for agent in swarm.agents.values():
            agent.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_complex_ecommerce_workflow(self, mock_e2e_environment):
        """Test complex workflow for creating an e-commerce application."""
        # Initialize FlutterSwarm
        swarm = FlutterSwarm()
        
        # Create e-commerce app project
        project_data = SAMPLE_PROJECT_DATA["complex_ecommerce"]
        project_id = swarm.create_project(
            name=project_data["name"],
            description=project_data["description"],
            requirements=project_data["requirements"],
            features=project_data["features"]
        )
        
        # Mock agent behaviors
        for agent in swarm.agents.values():
            agent.start = AsyncMock()
            agent.stop = AsyncMock()
            agent._agent_loop = AsyncMock()
        
        # Start the swarm
        start_task = asyncio.create_task(swarm.start())
        await asyncio.sleep(0.1)
        
        # Build the project with some issues
        with patch.object(swarm, '_monitor_build_progress') as mock_monitor:
            mock_monitor.return_value = create_mock_build_result(
                status="completed_with_issues",
                files_created=25,
                has_issues=True
            )
            
            build_result = await swarm.build_project(
                project_id,
                platforms=project_data["platforms"]
            )
        
        # Verify build completion with issues
        assert build_result["status"] == "completed_with_issues"
        assert build_result["files_created"] == 25
        assert len(build_result["security_findings"]) > 0
        
        # Get project status
        status = swarm.get_project_status(project_id)
        assert status["project"]["name"] == project_data["name"]
        
        # Stop the swarm
        await swarm.stop()
    
    @pytest.mark.asyncio
    async def test_cli_to_build_workflow(self, mock_e2e_environment):
        """Test complete CLI to build workflow."""
        with patch('cli.FlutterSwarm') as mock_swarm_class, \
             patch('cli.get_config') as mock_get_config, \
             patch('cli.console') as mock_console:
            
            # Setup mocks
            mock_swarm = MagicMock()
            mock_swarm_class.return_value = mock_swarm
            mock_get_config.return_value = mock_e2e_environment['config']
            
            # Mock project creation and building
            mock_swarm.create_project.return_value = "cli_project_123"
            build_future = asyncio.Future()
            build_future.set_result(create_mock_build_result())
            mock_swarm.build_project.return_value = build_future
            
            # Mock console
            mock_console.print = MagicMock()
            
            # Initialize CLI
            cli = FlutterSwarmCLI()
            
            # Mock CLI methods
            cli.display_build_results = MagicMock()
            cli.build_project_with_progress = AsyncMock()
            
            # Create arguments for project creation with build
            args = MagicMock()
            args.name = "CLITestApp"
            args.description = "App created via CLI"
            args.requirements = "auth,database"
            args.features = "login,crud"
            args.platforms = "android,ios"
            args.build = True
            
            # Execute CLI command
            await cli.create_project(args)
            
            # Verify project was created and built
            mock_swarm.create_project.assert_called_once()
            cli.build_project_with_progress.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_interactive_development_session(self, mock_e2e_environment):
        """Test interactive development session workflow."""
        with patch('cli.FlutterSwarm') as mock_swarm_class, \
             patch('cli.get_config') as mock_get_config, \
             patch('cli.console') as mock_console:
            
            # Setup mocks
            mock_swarm = MagicMock()
            mock_swarm_class.return_value = mock_swarm
            mock_get_config.return_value = mock_e2e_environment['config']
            
            # Mock swarm operations
            mock_swarm.start = AsyncMock()
            mock_swarm.stop = AsyncMock()
            mock_swarm.create_project.return_value = "interactive_project_123"
            mock_swarm.list_projects.return_value = [
                {
                    "id": "interactive_project_123",
                    "name": "InteractiveApp",
                    "current_phase": "implementation",
                    "progress": 0.6
                }
            ]
            mock_swarm.get_project_status.return_value = {
                "project": {
                    "name": "InteractiveApp",
                    "current_phase": "implementation",
                    "progress": 0.6
                },
                "agents": {
                    "implementation": {"status": "working"}
                }
            }
            
            # Mock interactive session commands
            commands = [
                "help",
                "create InteractiveApp An interactive app",
                "list",
                "status interactive_project_123",
                "quit"
            ]
            mock_console.input.side_effect = commands
            mock_console.print = MagicMock()
            
            # Initialize CLI
            cli = FlutterSwarmCLI()
            
            # Mock CLI methods
            cli.show_interactive_help = MagicMock()
            cli.handle_interactive_create = AsyncMock()
            cli.handle_interactive_list = MagicMock()
            cli.handle_interactive_status = AsyncMock()
            cli.display_project_status = MagicMock()
            
            # Execute interactive session
            args = MagicMock()
            await cli.run_interactive(args)
            
            # Verify interactive commands were executed
            cli.show_interactive_help.assert_called_once()
            cli.handle_interactive_create.assert_called_once()
            cli.handle_interactive_list.assert_called_once()
            cli.handle_interactive_status.assert_called_once()
            mock_swarm.stop.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_multi_platform_build_workflow(self, mock_e2e_environment):
        """Test multi-platform build workflow."""
        # Initialize FlutterSwarm
        swarm = FlutterSwarm()
        
        # Create project for multi-platform build
        project_id = swarm.create_project(
            name="MultiPlatformApp",
            description="App for multiple platforms",
            requirements=["cross_platform_ui", "platform_channels"],
            features=["responsive_design", "platform_specific_features"]
        )
        
        # Mock agent behaviors
        for agent in swarm.agents.values():
            agent.start = AsyncMock()
            agent.stop = AsyncMock()
            agent._agent_loop = AsyncMock()
        
        # Start the swarm
        start_task = asyncio.create_task(swarm.start())
        await asyncio.sleep(0.1)
        
        # Build for multiple platforms
        platforms = ["android", "ios", "web", "desktop"]
        
        with patch.object(swarm, '_monitor_build_progress') as mock_monitor:
            # Mock successful multi-platform build
            build_result = create_mock_build_result()
            build_result["platforms"] = platforms
            build_result["platform_builds"] = {
                platform: {"status": "success", "size": f"{10 + i}MB"}
                for i, platform in enumerate(platforms)
            }
            mock_monitor.return_value = build_result
            
            result = await swarm.build_project(project_id, platforms=platforms)
        
        # Verify multi-platform build
        assert result["platforms"] == platforms
        assert len(result["platform_builds"]) == 4
        
        # Stop the swarm
        await swarm.stop()
    
    @pytest.mark.asyncio
    async def test_error_recovery_workflow(self, mock_e2e_environment):
        """Test error recovery workflow."""
        # Initialize FlutterSwarm
        swarm = FlutterSwarm()
        
        # Create project
        project_id = swarm.create_project(
            name="ErrorRecoveryApp",
            description="App to test error recovery",
            requirements=["error_handling", "resilience"],
            features=["retry_logic", "graceful_degradation"]
        )
        
        # Mock agent behaviors with some failures
        for agent in swarm.agents.values():
            agent.start = AsyncMock()
            agent.stop = AsyncMock()
            agent._agent_loop = AsyncMock()
        
        # Start the swarm
        start_task = asyncio.create_task(swarm.start())
        await asyncio.sleep(0.1)
        
        # Mock build with initial failure then recovery
        with patch.object(swarm, '_monitor_build_progress') as mock_monitor:
            # First call returns failure
            failed_result = create_mock_build_result()
            failed_result["status"] = "failed"
            failed_result["error"] = "Build process failed due to dependency conflicts"
            
            mock_monitor.return_value = failed_result
            
            # Attempt build (should fail)
            result = await swarm.build_project(project_id)
            
            # Verify failure was handled
            assert result["status"] == "failed"
            assert "error" in result
        
        # Simulate recovery attempt
        with patch.object(swarm, '_monitor_build_progress') as mock_monitor:
            # Second call returns success after recovery
            success_result = create_mock_build_result()
            success_result["status"] = "completed"
            success_result["recovery_attempts"] = 1
            
            mock_monitor.return_value = success_result
            
            # Retry build (should succeed)
            result = await swarm.build_project(project_id)
            
            # Verify recovery
            assert result["status"] == "completed"
            assert result["recovery_attempts"] == 1
        
        # Stop the swarm
        await swarm.stop()
    
    @pytest.mark.asyncio
    async def test_performance_optimization_workflow(self, mock_e2e_environment):
        """Test performance optimization workflow."""
        # Initialize FlutterSwarm
        swarm = FlutterSwarm()
        
        # Create performance-critical project
        project_id = swarm.create_project(
            name="PerformanceApp",
            description="High-performance application",
            requirements=["60fps_guarantee", "fast_startup", "low_memory"],
            features=["optimized_rendering", "lazy_loading", "caching"]
        )
        
        # Mock agent behaviors
        for agent in swarm.agents.values():
            agent.start = AsyncMock()
            agent.stop = AsyncMock()
            agent._agent_loop = AsyncMock()
        
        # Start the swarm
        start_task = asyncio.create_task(swarm.start())
        await asyncio.sleep(0.1)
        
        # Build with performance monitoring
        with patch.object(swarm, '_monitor_build_progress') as mock_monitor:
            perf_result = create_mock_build_result()
            perf_result["performance_metrics"] = {
                "build_time": 35.2,
                "app_size": "8.5MB",
                "startup_time": "0.8s",
                "frame_rate": "60fps",
                "memory_usage": "45MB"
            }
            perf_result["optimizations_applied"] = [
                "code_splitting",
                "image_compression", 
                "tree_shaking",
                "lazy_loading"
            ]
            mock_monitor.return_value = perf_result
            
            result = await swarm.build_project(project_id)
        
        # Verify performance optimizations
        assert result["performance_metrics"]["frame_rate"] == "60fps"
        assert result["performance_metrics"]["startup_time"] == "0.8s"
        assert len(result["optimizations_applied"]) == 4
        
        # Stop the swarm
        await swarm.stop()
    
    @pytest.mark.asyncio
    async def test_security_compliance_workflow(self, mock_e2e_environment):
        """Test security compliance workflow."""
        # Initialize FlutterSwarm
        swarm = FlutterSwarm()
        
        # Create security-critical project
        project_id = swarm.create_project(
            name="SecureApp",
            description="Security-compliant application",
            requirements=["GDPR_compliance", "data_encryption", "secure_auth"],
            features=["biometric_auth", "encrypted_storage", "audit_logging"]
        )
        
        # Mock agent behaviors
        for agent in swarm.agents.values():
            agent.start = AsyncMock()
            agent.stop = AsyncMock()
            agent._agent_loop = AsyncMock()
        
        # Start the swarm
        start_task = asyncio.create_task(swarm.start())
        await asyncio.sleep(0.1)
        
        # Build with security scanning
        with patch.object(swarm, '_monitor_build_progress') as mock_monitor:
            secure_result = create_mock_build_result()
            secure_result["security_scan"] = {
                "vulnerabilities_found": 0,
                "compliance_checks": {
                    "GDPR": {"compliant": True, "score": 95},
                    "OWASP": {"compliant": True, "score": 92}
                },
                "security_features": [
                    "biometric_authentication",
                    "end_to_end_encryption",
                    "secure_storage",
                    "certificate_pinning"
                ]
            }
            mock_monitor.return_value = secure_result
            
            result = await swarm.build_project(project_id)
        
        # Verify security compliance
        assert result["security_scan"]["vulnerabilities_found"] == 0
        assert result["security_scan"]["compliance_checks"]["GDPR"]["compliant"]
        assert result["security_scan"]["compliance_checks"]["OWASP"]["compliant"]
        assert len(result["security_scan"]["security_features"]) == 4
        
        # Stop the swarm
        await swarm.stop()
    
    @pytest.mark.asyncio
    async def test_continuous_integration_workflow(self, mock_e2e_environment):
        """Test continuous integration workflow."""
        # Initialize FlutterSwarm
        swarm = FlutterSwarm()
        
        # Create CI-enabled project
        project_id = swarm.create_project(
            name="CIApp",
            description="Application with CI/CD pipeline",
            requirements=["automated_testing", "continuous_deployment"],
            features=["ci_cd_integration", "automated_quality_checks"]
        )
        
        # Mock agent behaviors
        for agent in swarm.agents.values():
            agent.start = AsyncMock()
            agent.stop = AsyncMock()
            agent._agent_loop = AsyncMock()
        
        # Start the swarm
        start_task = asyncio.create_task(swarm.start())
        await asyncio.sleep(0.1)
        
        # Build with CI/CD setup
        with patch.object(swarm, '_monitor_build_progress') as mock_monitor:
            ci_result = create_mock_build_result()
            ci_result["ci_cd_setup"] = {
                "platform": "github_actions",
                "workflows": [
                    "test_on_push",
                    "build_on_merge",
                    "deploy_on_release"
                ],
                "quality_gates": [
                    "test_coverage_80",
                    "security_scan_pass",
                    "performance_check_pass"
                ],
                "deployment_targets": ["staging", "production"]
            }
            ci_result["automation_tests"] = {
                "unit_tests": {"count": 45, "status": "passed"},
                "integration_tests": {"count": 12, "status": "passed"},
                "e2e_tests": {"count": 8, "status": "passed"}
            }
            mock_monitor.return_value = ci_result
            
            result = await swarm.build_project(
                project_id,
                ci_system="github_actions"
            )
        
        # Verify CI/CD setup
        assert result["ci_cd_setup"]["platform"] == "github_actions"
        assert len(result["ci_cd_setup"]["workflows"]) == 3
        assert len(result["ci_cd_setup"]["quality_gates"]) == 3
        assert result["automation_tests"]["unit_tests"]["status"] == "passed"
        
        # Stop the swarm
        await swarm.stop()
    
    @pytest.mark.asyncio
    async def test_scalability_testing_workflow(self, mock_e2e_environment):
        """Test scalability testing workflow."""
        # Initialize FlutterSwarm
        swarm = FlutterSwarm()
        
        # Create scalable project
        project_id = swarm.create_project(
            name="ScalableApp",
            description="Highly scalable application",
            requirements=["horizontal_scaling", "load_balancing", "caching"],
            features=["microservices", "distributed_caching", "auto_scaling"]
        )
        
        # Mock agent behaviors
        for agent in swarm.agents.values():
            agent.start = AsyncMock()
            agent.stop = AsyncMock()
            agent._agent_loop = AsyncMock()
        
        # Start the swarm
        start_task = asyncio.create_task(swarm.start())
        await asyncio.sleep(0.1)
        
        # Build with scalability testing
        with patch.object(swarm, '_monitor_build_progress') as mock_monitor:
            scalability_result = create_mock_build_result()
            scalability_result["scalability_tests"] = {
                "load_testing": {
                    "concurrent_users": 1000,
                    "response_time_p95": "250ms",
                    "throughput": "500 req/s",
                    "status": "passed"
                },
                "stress_testing": {
                    "max_capacity": "2000 users",
                    "breaking_point": "2500 users",
                    "recovery_time": "30s",
                    "status": "passed"
                },
                "capacity_planning": {
                    "recommended_instances": 3,
                    "auto_scaling_threshold": "80% CPU",
                    "scaling_strategy": "horizontal"
                }
            }
            mock_monitor.return_value = scalability_result
            
            result = await swarm.build_project(project_id)
        
        # Verify scalability testing
        scalability = result["scalability_tests"]
        assert scalability["load_testing"]["status"] == "passed"
        assert scalability["stress_testing"]["status"] == "passed"
        assert scalability["capacity_planning"]["recommended_instances"] == 3
        
        # Stop the swarm
        await swarm.stop()
    
    @pytest.mark.asyncio
    async def test_documentation_generation_workflow(self, mock_e2e_environment):
        """Test comprehensive documentation generation workflow."""
        # Initialize FlutterSwarm
        swarm = FlutterSwarm()
        
        # Create project requiring extensive documentation
        project_id = swarm.create_project(
            name="DocumentedApp",
            description="Well-documented application",
            requirements=["api_documentation", "user_guides", "technical_docs"],
            features=["auto_documentation", "interactive_docs", "code_samples"]
        )
        
        # Mock agent behaviors
        for agent in swarm.agents.values():
            agent.start = AsyncMock()
            agent.stop = AsyncMock()
            agent._agent_loop = AsyncMock()
        
        # Start the swarm
        start_task = asyncio.create_task(swarm.start())
        await asyncio.sleep(0.1)
        
        # Build with documentation generation
        with patch.object(swarm, '_monitor_build_progress') as mock_monitor:
            doc_result = create_mock_build_result()
            doc_result["documentation"] = {
                "api_docs": {
                    "files": ["api/auth.md", "api/users.md", "api/products.md"],
                    "endpoints_documented": 25,
                    "coverage": "100%"
                },
                "user_guides": {
                    "files": ["user_guide.md", "installation.md", "troubleshooting.md"],
                    "sections": 15,
                    "examples": 30
                },
                "technical_docs": {
                    "files": ["architecture.md", "deployment.md", "security.md"],
                    "diagrams": 8,
                    "code_samples": 45
                },
                "auto_generated": True,
                "formats": ["markdown", "html", "pdf"]
            }
            mock_monitor.return_value = doc_result
            
            result = await swarm.build_project(project_id)
        
        # Verify documentation generation
        docs = result["documentation"]
        assert docs["api_docs"]["coverage"] == "100%"
        assert docs["user_guides"]["sections"] == 15
        assert docs["technical_docs"]["code_samples"] == 45
        assert docs["auto_generated"] == True
        
        # Stop the swarm
        await swarm.stop()
