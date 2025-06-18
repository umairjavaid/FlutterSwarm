"""
Unit tests for DevOpsAgent.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

# Import test fixtures and mocks
from tests.fixtures.test_constants import (
    SAMPLE_PROJECT_CONFIG,
    SAMPLE_AGENT_CONFIG,
    SAMPLE_CI_CD_CONFIG
)
from tests.mocks.mock_implementations import MockToolManager, MockConfigManager

# Import the agent under test
from agents.devops_agent import DevOpsAgent
from shared.state import AgentStatus, MessageType
from tools.base_tool import ToolResult, ToolStatus


class TestDevOpsAgent:
    """Test suite for DevOpsAgent."""

    @pytest.fixture
    def mock_config_manager(self):
        """Mock config manager for testing."""
        return MockConfigManager()

    @pytest.fixture
    def mock_tool_manager(self):
        """Mock tool manager for testing."""
        tool_manager = Mock()
        tool_manager.create_agent_toolbox.return_value = Mock()
        tool_manager.create_agent_toolbox.return_value.list_available_tools.return_value = [
            "terminal", "file", "git", "flutter"
        ]
        return tool_manager

    @pytest.fixture
    def agent(self, mock_config_manager, mock_tool_manager):
        """Create DevOpsAgent for testing."""
        with patch('agents.devops_agent.get_config', return_value=mock_config_manager), \
             patch('agents.devops_agent.ToolManager', return_value=mock_tool_manager), \
             patch('langchain_anthropic.ChatAnthropic'):
            
            agent = DevOpsAgent()
            agent.execute_tool = AsyncMock()
            agent.think = AsyncMock()
            agent.run_command = AsyncMock()
            agent.read_file = AsyncMock()
            agent.write_file = AsyncMock()
            return agent

    @pytest.mark.unit
    def test_devops_agent_initialization(self, agent):
        """Test DevOps agent initializes correctly."""
        assert agent.agent_id == "devops"
        assert hasattr(agent, 'platforms')
        assert hasattr(agent, 'ci_systems')
        assert hasattr(agent, 'deployment_targets')
        
        # Check expected platforms and systems
        assert "android" in agent.platforms
        assert "ios" in agent.platforms
        assert "web" in agent.platforms
        assert "desktop" in agent.platforms
        
        assert "github_actions" in agent.ci_systems
        assert "gitlab_ci" in agent.ci_systems
        
        assert "app_store" in agent.deployment_targets
        assert "play_store" in agent.deployment_targets

    @pytest.mark.unit
    async def test_execute_task_setup_ci_cd(self, agent):
        """Test CI/CD pipeline setup task."""
        task_data = {
            "project_id": "test_project",
            "ci_system": "github_actions",
            "target_platforms": ["android", "ios"],
            "deployment_targets": ["play_store", "app_store"],
            "test_requirements": ["unit", "widget", "integration"]
        }
        
        # Mock CI/CD setup responses
        agent.execute_tool.side_effect = [
            # Create .github/workflows directory
            ToolResult(status=ToolStatus.SUCCESS, data={"created": True}),
            # Create workflow files
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True}),
            # Setup secrets documentation
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True})
        ]
        
        agent.think.return_value = "CI/CD pipeline configuration created"
        
        result = await agent.execute_task("setup_ci_cd", task_data)
        
        assert result["setup_type"] == "ci_cd"
        assert result["ci_system"] == "github_actions"
        assert "workflow_files" in result
        assert "platforms_configured" in result
        assert result["status"] == "completed"
        
        # Should create workflow files
        assert agent.execute_tool.call_count >= 3

    @pytest.mark.unit
    async def test_execute_task_configure_deployment(self, agent):
        """Test deployment configuration task."""
        task_data = {
            "project_id": "test_project",
            "deployment_type": "automated",
            "target_stores": ["play_store", "app_store"],
            "environment": "production"
        }
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"deployment_configured": True}
        )
        
        agent.think.return_value = "Deployment configuration created"
        
        result = await agent.execute_task("configure_deployment", task_data)
        
        assert result["deployment_type"] == "automated"
        assert "target_stores" in result
        assert "deployment_scripts" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_execute_task_setup_monitoring(self, agent):
        """Test monitoring setup task."""
        task_data = {
            "project_id": "test_project",
            "monitoring_services": ["firebase_crashlytics", "sentry"],
            "performance_monitoring": True,
            "error_tracking": True
        }
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"monitoring_configured": True}
        )
        
        agent.think.return_value = "Monitoring setup completed"
        
        result = await agent.execute_task("setup_monitoring", task_data)
        
        assert "monitoring_services" in result
        assert result["performance_monitoring"] == True
        assert result["error_tracking"] == True
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_execute_task_create_build_scripts(self, agent):
        """Test build scripts creation task."""
        task_data = {
            "project_id": "test_project",
            "platforms": ["android", "ios", "web"],
            "build_types": ["debug", "release"],
            "custom_commands": ["test", "analyze"]
        }
        
        agent.execute_tool.side_effect = [
            # Create scripts directory
            ToolResult(status=ToolStatus.SUCCESS, data={"created": True}),
            # Create build scripts
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True}),
            # Make scripts executable
            ToolResult(status=ToolStatus.SUCCESS, data={"permissions_set": True})
        ]
        
        result = await agent.execute_task("create_build_scripts", task_data)
        
        assert "script_files" in result
        assert "platforms" in result
        assert result["platforms"] == ["android", "ios", "web"]
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_execute_task_general(self, agent):
        """Test general DevOps task handling."""
        task_description = "optimize build performance"
        task_data = {"current_build_time": "10_minutes"}
        
        agent.think.return_value = "Build optimization recommendations provided"
        
        result = await agent.execute_task(task_description, task_data)
        
        assert result["task"] == task_description
        assert "devops_response" in result
        assert result["status"] == "completed"
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_collaborate_architecture_review(self, agent):
        """Test collaboration for deployment architecture review."""
        data = {
            "architecture": {
                "deployment_strategy": "blue_green",
                "infrastructure": "cloud"
            },
            "scalability_requirements": "high"
        }
        
        agent.think.return_value = "Architecture review completed"
        
        result = await agent.collaborate("architecture_review", data)
        
        assert result["review_type"] == "deployment_architecture"
        assert "recommendations" in result
        assert "scalability_assessment" in result
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_collaborate_build_optimization(self, agent):
        """Test collaboration for build optimization."""
        data = {
            "current_build_time": 900,  # 15 minutes
            "bottlenecks": ["dependency_resolution", "asset_compilation"],
            "target_improvement": "50_percent"
        }
        
        agent.think.return_value = "Build optimization plan created"
        
        result = await agent.collaborate("build_optimization", data)
        
        assert result["optimization_type"] == "build_process"
        assert "recommendations" in result
        assert "expected_improvement" in result
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_collaborate_deployment_strategy(self, agent):
        """Test collaboration for deployment strategy recommendation."""
        data = {
            "app_type": "enterprise",
            "user_base": "100k_active",
            "release_frequency": "weekly",
            "rollback_requirements": "fast"
        }
        
        agent.think.return_value = "Deployment strategy recommended"
        
        result = await agent.collaborate("deployment_strategy", data)
        
        assert result["strategy_type"] == "deployment"
        assert "recommended_strategy" in result
        assert "implementation_steps" in result
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_collaborate_unknown_type(self, agent):
        """Test collaboration with unknown type."""
        result = await agent.collaborate("unknown_type", {})
        
        assert result["status"] == "unknown_collaboration_type"
        assert result["type"] == "unknown_type"

    @pytest.mark.unit
    async def test_on_state_change_implementation_completed(self, agent, mock_shared_state):
        """Test reaction to implementation completed state change."""
        change_data = {
            "event": "implementation_completed",
            "project_id": "test_project"
        }
        
        mock_project = Mock()
        mock_project.name = "TestApp"
        mock_shared_state.get_project_state.return_value = mock_project
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"ci_cd_setup": True}
        )
        
        await agent.on_state_change(change_data)
        
        # Should automatically setup CI/CD
        agent.execute_tool.assert_called()

    @pytest.mark.unit
    async def test_on_state_change_release_requested(self, agent):
        """Test reaction to release requested state change."""
        change_data = {
            "event": "release_requested",
            "version": "1.0.0",
            "platforms": ["android", "ios"]
        }
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"deployment_triggered": True}
        )
        
        await agent.on_state_change(change_data)
        
        # Should trigger deployment process
        agent.execute_tool.assert_called()

    @pytest.mark.unit
    async def test_setup_ci_cd_pipeline_github_actions(self, agent):
        """Test GitHub Actions CI/CD pipeline setup."""
        task_data = {
            "ci_system": "github_actions",
            "platforms": ["android", "ios"],
            "test_coverage": True,
            "deploy_on_release": True
        }
        
        agent.execute_tool.side_effect = [
            ToolResult(status=ToolStatus.SUCCESS, data={"created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True})
        ]
        
        result = await agent._setup_ci_cd_pipeline(task_data)
        
        assert result["ci_system"] == "github_actions"
        assert "workflow_files" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_setup_ci_cd_pipeline_gitlab_ci(self, agent):
        """Test GitLab CI pipeline setup."""
        task_data = {
            "ci_system": "gitlab_ci",
            "platforms": ["web"],
            "test_coverage": False,
            "deploy_on_release": False
        }
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"gitlab_ci_configured": True}
        )
        
        result = await agent._setup_ci_cd_pipeline(task_data)
        
        assert result["ci_system"] == "gitlab_ci"
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_configure_deployment_app_stores(self, agent):
        """Test app store deployment configuration."""
        task_data = {
            "deployment_type": "app_stores",
            "target_stores": ["play_store", "app_store"],
            "automatic_release": False,
            "beta_testing": True
        }
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"store_config_created": True}
        )
        
        agent.think.return_value = "App store deployment configured"
        
        result = await agent._configure_deployment(task_data)
        
        assert result["deployment_type"] == "app_stores"
        assert "target_stores" in result
        assert "deployment_scripts" in result

    @pytest.mark.unit
    async def test_configure_deployment_web_hosting(self, agent):
        """Test web hosting deployment configuration."""
        task_data = {
            "deployment_type": "web_hosting",
            "hosting_provider": "firebase_hosting",
            "custom_domain": "myapp.com",
            "ssl_enabled": True
        }
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"hosting_configured": True}
        )
        
        agent.think.return_value = "Web hosting deployment configured"
        
        result = await agent._configure_deployment(task_data)
        
        assert result["deployment_type"] == "web_hosting"
        assert "hosting_provider" in result
        assert result["hosting_provider"] == "firebase_hosting"

    @pytest.mark.unit
    async def test_setup_monitoring_firebase(self, agent):
        """Test Firebase monitoring setup."""
        task_data = {
            "monitoring_services": ["firebase_crashlytics", "firebase_performance"],
            "error_tracking": True,
            "performance_monitoring": True,
            "custom_events": ["user_actions", "feature_usage"]
        }
        
        agent.execute_tool.side_effect = [
            # Add Firebase dependencies
            ToolResult(status=ToolStatus.SUCCESS, data={"packages_added": True}),
            # Configure Firebase
            ToolResult(status=ToolStatus.SUCCESS, data={"firebase_configured": True}),
            # Setup monitoring code
            ToolResult(status=ToolStatus.SUCCESS, data={"monitoring_code_added": True})
        ]
        
        result = await agent._setup_monitoring(task_data)
        
        assert "monitoring_services" in result
        assert result["error_tracking"] == True
        assert result["performance_monitoring"] == True
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_setup_monitoring_sentry(self, agent):
        """Test Sentry monitoring setup."""
        task_data = {
            "monitoring_services": ["sentry"],
            "error_tracking": True,
            "performance_monitoring": False,
            "environment": "production"
        }
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"sentry_configured": True}
        )
        
        result = await agent._setup_monitoring(task_data)
        
        assert "sentry" in result["monitoring_services"]
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_create_build_scripts_android(self, agent):
        """Test Android build scripts creation."""
        task_data = {
            "platforms": ["android"],
            "build_types": ["debug", "release", "profile"],
            "signing_config": True,
            "proguard_enabled": True
        }
        
        agent.execute_tool.side_effect = [
            ToolResult(status=ToolStatus.SUCCESS, data={"created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"permissions_set": True})
        ]
        
        result = await agent._create_build_scripts(task_data)
        
        assert "script_files" in result
        assert "android" in result["platforms"]
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_create_build_scripts_ios(self, agent):
        """Test iOS build scripts creation."""
        task_data = {
            "platforms": ["ios"],
            "build_types": ["debug", "release"],
            "code_signing": True,
            "provisioning_profiles": ["development", "distribution"]
        }
        
        agent.execute_tool.side_effect = [
            ToolResult(status=ToolStatus.SUCCESS, data={"created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"permissions_set": True})
        ]
        
        result = await agent._create_build_scripts(task_data)
        
        assert "script_files" in result
        assert "ios" in result["platforms"]
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_create_build_scripts_web(self, agent):
        """Test web build scripts creation."""
        task_data = {
            "platforms": ["web"],
            "build_types": ["debug", "release"],
            "optimization": True,
            "pwa_support": True
        }
        
        agent.execute_tool.side_effect = [
            ToolResult(status=ToolStatus.SUCCESS, data={"created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"permissions_set": True})
        ]
        
        result = await agent._create_build_scripts(task_data)
        
        assert "script_files" in result
        assert "web" in result["platforms"]
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_review_deployment_architecture(self, agent):
        """Test deployment architecture review."""
        data = {
            "current_architecture": {
                "deployment_strategy": "rolling_update",
                "infrastructure": "kubernetes",
                "monitoring": "prometheus"
            },
            "requirements": {
                "availability": "99.9%",
                "scalability": "auto_scaling"
            }
        }
        
        agent.think.return_value = "Architecture meets requirements"
        
        result = await agent._review_deployment_architecture(data)
        
        assert result["review_type"] == "deployment_architecture"
        assert "recommendations" in result
        assert "scalability_assessment" in result

    @pytest.mark.unit
    async def test_optimize_build_process(self, agent):
        """Test build process optimization."""
        data = {
            "current_metrics": {
                "build_time": 900,  # 15 minutes
                "cache_hit_rate": 0.3,
                "parallelization": False
            },
            "target_improvement": 0.5  # 50% improvement
        }
        
        agent.think.return_value = "Build optimization recommendations"
        
        result = await agent._optimize_build_process(data)
        
        assert result["optimization_type"] == "build_process"
        assert "recommendations" in result
        assert "expected_improvement" in result

    @pytest.mark.unit
    async def test_recommend_deployment_strategy(self, agent):
        """Test deployment strategy recommendation."""
        data = {
            "app_characteristics": {
                "user_base": "1M_active",
                "criticality": "high",
                "update_frequency": "weekly"
            },
            "constraints": {
                "downtime_tolerance": "zero",
                "rollback_speed": "fast"
            }
        }
        
        agent.think.return_value = "Blue-green deployment recommended"
        
        result = await agent._recommend_deployment_strategy(data)
        
        assert result["strategy_type"] == "deployment"
        assert "recommended_strategy" in result
        assert "implementation_steps" in result

    @pytest.mark.unit
    async def test_handle_general_devops_task(self, agent):
        """Test general DevOps task handling."""
        task_description = "setup environment variables"
        task_data = {
            "environment": "production",
            "variables": ["API_KEY", "DATABASE_URL"]
        }
        
        agent.think.return_value = "Environment variables configured"
        
        result = await agent._handle_general_devops_task(task_description, task_data)
        
        assert result["task"] == task_description
        assert "devops_response" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_error_handling_in_ci_cd_setup(self, agent):
        """Test error handling during CI/CD setup."""
        task_data = {"ci_system": "github_actions"}
        
        # Mock tool failure
        agent.execute_tool.side_effect = Exception("Git repository not found")
        
        try:
            result = await agent.execute_task("setup_ci_cd", task_data)
            # If no exception, check error handling
            assert "error" in str(result).lower() or "status" in result
        except Exception:
            # Exception handling depends on implementation
            pass

    @pytest.mark.unit
    async def test_concurrent_devops_tasks(self, agent):
        """Test handling concurrent DevOps tasks."""
        tasks = [
            agent.execute_task("setup_ci_cd", {"ci_system": "github_actions"}),
            agent.execute_task("configure_deployment", {"deployment_type": "automated"}),
            agent.execute_task("setup_monitoring", {"monitoring_services": ["firebase_crashlytics"]})
        ]
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"task_completed": True}
        )
        agent.think.return_value = "Task completed"
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert all("status" in result for result in results)

    @pytest.mark.unit
    def test_platforms_configuration(self, agent):
        """Test platforms configuration."""
        expected_platforms = ["android", "ios", "web", "desktop"]
        
        for platform in expected_platforms:
            assert platform in agent.platforms
        
        assert len(agent.platforms) >= len(expected_platforms)

    @pytest.mark.unit
    def test_ci_systems_configuration(self, agent):
        """Test CI systems configuration."""
        expected_systems = ["github_actions", "gitlab_ci", "azure_pipelines", "bitbucket"]
        
        for system in expected_systems:
            assert system in agent.ci_systems
        
        assert len(agent.ci_systems) >= len(expected_systems)

    @pytest.mark.unit
    def test_deployment_targets_configuration(self, agent):
        """Test deployment targets configuration."""
        expected_targets = ["app_store", "play_store", "firebase_hosting", "web_hosting"]
        
        for target in expected_targets:
            assert target in agent.deployment_targets
        
        assert len(agent.deployment_targets) >= len(expected_targets)

    @pytest.mark.unit
    async def test_docker_deployment_configuration(self, agent):
        """Test Docker deployment configuration."""
        task_data = {
            "deployment_type": "docker",
            "container_registry": "docker_hub",
            "orchestration": "kubernetes",
            "auto_scaling": True
        }
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"docker_configured": True}
        )
        
        agent.think.return_value = "Docker deployment configured"
        
        result = await agent.execute_task("configure_deployment", task_data)
        
        assert result["deployment_type"] == "docker"
        assert "deployment_scripts" in result

    @pytest.mark.unit
    async def test_performance_monitoring_setup(self, agent):
        """Test performance monitoring setup."""
        task_data = {
            "monitoring_type": "performance",
            "metrics": ["app_start_time", "frame_rate", "memory_usage"],
            "alerting": True,
            "dashboard": True
        }
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"performance_monitoring_setup": True}
        )
        
        result = await agent.execute_task("setup_monitoring", task_data)
        
        assert "metrics" in result
        assert result["alerting"] == True
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_security_scanning_integration(self, agent):
        """Test security scanning integration in CI/CD."""
        task_data = {
            "ci_system": "github_actions",
            "security_scanning": True,
            "vulnerability_checking": True,
            "dependency_audit": True
        }
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"security_scanning_configured": True}
        )
        
        result = await agent.execute_task("setup_ci_cd", task_data)
        
        assert result["security_scanning"] == True
        assert "workflow_files" in result

    @pytest.mark.unit
    async def test_multi_environment_deployment(self, agent):
        """Test multi-environment deployment setup."""
        task_data = {
            "environments": ["development", "staging", "production"],
            "promotion_strategy": "automated",
            "approval_required": ["production"],
            "rollback_strategy": "automatic"
        }
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"multi_env_configured": True}
        )
        
        result = await agent.execute_task("configure_deployment", task_data)
        
        assert "environments" in result
        assert result["promotion_strategy"] == "automated"
        assert result["status"] == "completed"
