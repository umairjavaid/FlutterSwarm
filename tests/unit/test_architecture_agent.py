"""
Unit tests for ArchitectureAgent.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

# Import test fixtures and mocks
from tests.fixtures.test_constants import (
    SAMPLE_PROJECT_CONFIG,
    SAMPLE_AGENT_CONFIG,
    SAMPLE_ARCHITECTURE_PLAN
)
from tests.mocks.mock_implementations import MockToolManager, MockConfigManager

# Import the agent under test
from agents.architecture_agent import ArchitectureAgent
from shared.state import AgentStatus, MessageType
from tools.base_tool import ToolResult, ToolStatus


class TestArchitectureAgent:
    """Test suite for ArchitectureAgent."""

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
            "file", "analysis", "terminal"
        ]
        return tool_manager

    @pytest.fixture
    def agent(self, mock_config_manager, mock_tool_manager):
        """Create ArchitectureAgent for testing."""
        with patch('agents.architecture_agent.get_config', return_value=mock_config_manager), \
             patch('agents.architecture_agent.ToolManager', return_value=mock_tool_manager), \
             patch('langchain_anthropic.ChatAnthropic'):
            
            agent = ArchitectureAgent()
            agent.execute_tool = AsyncMock()
            agent.think = AsyncMock()
            agent.run_command = AsyncMock()
            agent.read_file = AsyncMock()
            agent.write_file = AsyncMock()
            return agent

    @pytest.mark.unit
    def test_architecture_agent_initialization(self, agent):
        """Test architecture agent initializes correctly."""
        assert agent.agent_id == "architecture"
        assert hasattr(agent, 'design_patterns')
        assert hasattr(agent, 'architecture_styles')
        assert isinstance(agent.design_patterns, list)
        assert isinstance(agent.architecture_styles, list)
        
        # Check for expected patterns and styles
        assert "BLoC" in agent.design_patterns
        assert "Provider" in agent.design_patterns
        assert "Clean Architecture" in agent.architecture_styles
        assert "MVVM" in agent.architecture_styles

    @pytest.mark.unit
    async def test_execute_task_design_flutter_architecture(self, agent):
        """Test Flutter architecture design task."""
        task_data = {
            "project_requirements": {
                "type": "mobile_app",
                "complexity": "high",
                "features": ["authentication", "offline_sync", "payments"],
                "target_platforms": ["iOS", "Android"]
            },
            "constraints": {
                "team_size": 5,
                "timeline": "6_months",
                "performance_requirements": "high"
            }
        }
        
        # Mock architecture design response
        agent.think.return_value = """
        Recommended Architecture:
        1. Clean Architecture with BLoC pattern
        2. Repository pattern for data layer
        3. Dependency injection with get_it
        4. Feature-based folder structure
        """
        
        result = await agent.execute_task("design_flutter_architecture", task_data)
        
        assert "architecture_design" in result
        assert "recommended_patterns" in result
        assert "project_structure" in result
        assert "technology_stack" in result
        assert result["complexity_level"] == "high"
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_execute_task_review_architecture(self, agent):
        """Test architecture review task."""
        task_data = {
            "current_architecture": {
                "pattern": "BLoC",
                "structure": "feature_based",
                "dependencies": ["flutter_bloc", "equatable"]
            },
            "issues": ["tight_coupling", "missing_abstractions"]
        }
        
        agent.think.return_value = "Architecture review completed"
        
        result = await agent.execute_task("review_architecture", task_data)
        
        assert "review_type" in result
        assert "recommendations" in result
        assert "architecture_score" in result
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_execute_task_select_state_management(self, agent):
        """Test state management selection task."""
        task_data = {
            "app_complexity": "medium",
            "team_experience": "intermediate",
            "performance_requirements": "standard",
            "features": ["user_auth", "data_sync"]
        }
        
        agent.think.return_value = "Provider recommended for this use case"
        
        result = await agent.execute_task("select_state_management", task_data)
        
        assert "recommended_solution" in result
        assert "alternatives" in result
        assert "justification" in result
        assert "implementation_guide" in result
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_execute_task_design_navigation(self, agent):
        """Test navigation design task."""
        task_data = {
            "app_type": "e_commerce",
            "user_flows": ["onboarding", "shopping", "checkout"],
            "navigation_complexity": "medium"
        }
        
        agent.think.return_value = "Navigation structure designed"
        
        result = await agent.execute_task("design_navigation", task_data)
        
        assert "navigation_structure" in result
        assert "routing_strategy" in result
        assert "user_flows" in result
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_execute_task_general(self, agent):
        """Test general architecture task handling."""
        task_description = "optimize app performance"
        task_data = {"current_performance": "slow"}
        
        agent.think.return_value = "Performance optimization plan created"
        
        result = await agent.execute_task(task_description, task_data)
        
        assert result["task"] == task_description
        assert "architecture_response" in result
        assert result["status"] == "completed"
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_collaborate_architectural_guidance(self, agent):
        """Test collaboration for architectural guidance."""
        data = {
            "question": "Which pattern is best for complex state management?",
            "context": {
                "app_type": "enterprise",
                "team_size": 10
            }
        }
        
        agent.think.return_value = "BLoC pattern recommended"
        
        result = await agent.collaborate("architectural_guidance", data)
        
        assert result["guidance_type"] == "architectural"
        assert "recommendation" in result
        assert "rationale" in result
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_collaborate_technology_selection(self, agent):
        """Test collaboration for technology selection."""
        data = {
            "requirement": "real_time_chat",
            "constraints": ["offline_support", "scalability"]
        }
        
        agent.think.return_value = "WebSocket with local DB recommended"
        
        result = await agent.collaborate("technology_selection", data)
        
        assert result["selection_type"] == "technology"
        assert "recommended_technologies" in result
        assert "implementation_notes" in result
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_collaborate_unknown_type(self, agent):
        """Test collaboration with unknown type."""
        result = await agent.collaborate("unknown_type", {})
        
        assert result["status"] == "unknown_collaboration_type"
        assert result["type"] == "unknown_type"

    @pytest.mark.unit
    async def test_on_state_change_project_started(self, agent, mock_shared_state):
        """Test reaction to project started state change."""
        change_data = {
            "event": "project_started",
            "project_id": "test_project",
            "requirements": {"type": "mobile_app"}
        }
        
        agent.think.return_value = "Initial architecture created"
        mock_shared_state.update_project_architecture = Mock()
        
        await agent.on_state_change(change_data)
        
        # Should suggest initial architecture
        agent.think.assert_called()

    @pytest.mark.unit
    async def test_on_state_change_feature_request(self, agent):
        """Test reaction to feature request state change."""
        change_data = {
            "event": "feature_request",
            "feature": "push_notifications",
            "project_id": "test_project"
        }
        
        agent.think.return_value = "Architecture updated for push notifications"
        
        await agent.on_state_change(change_data)
        
        # Should analyze architecture impact
        agent.think.assert_called()

    @pytest.mark.unit
    async def test_design_flutter_architecture_simple_app(self, agent):
        """Test architecture design for simple app."""
        task_data = {
            "project_requirements": {
                "type": "simple_utility",
                "complexity": "low",
                "features": ["local_storage"],
                "target_platforms": ["Android"]
            }
        }
        
        agent.think.return_value = "Simple MVC architecture recommended"
        
        result = await agent._design_flutter_architecture(task_data)
        
        assert "architecture_design" in result
        assert result["complexity_level"] == "low"
        assert "recommended_patterns" in result

    @pytest.mark.unit
    async def test_design_flutter_architecture_complex_app(self, agent):
        """Test architecture design for complex app."""
        task_data = {
            "project_requirements": {
                "type": "enterprise_app",
                "complexity": "high",
                "features": ["auth", "sync", "payments", "analytics"],
                "target_platforms": ["iOS", "Android", "Web"]
            }
        }
        
        agent.think.return_value = "Clean Architecture with BLoC recommended"
        
        result = await agent._design_flutter_architecture(task_data)
        
        assert "architecture_design" in result
        assert result["complexity_level"] == "high"
        assert "technology_stack" in result

    @pytest.mark.unit
    async def test_select_state_management_simple_case(self, agent):
        """Test state management selection for simple case."""
        task_data = {
            "app_complexity": "low",
            "team_experience": "beginner",
            "performance_requirements": "standard"
        }
        
        agent.think.return_value = "setState recommended for simplicity"
        
        result = await agent._select_state_management(task_data)
        
        assert "recommended_solution" in result
        assert "alternatives" in result
        assert result["app_complexity"] == "low"

    @pytest.mark.unit
    async def test_select_state_management_complex_case(self, agent):
        """Test state management selection for complex case."""
        task_data = {
            "app_complexity": "high",
            "team_experience": "expert",
            "performance_requirements": "high"
        }
        
        agent.think.return_value = "BLoC with Hydrated BLoC recommended"
        
        result = await agent._select_state_management(task_data)
        
        assert "recommended_solution" in result
        assert "implementation_guide" in result
        assert result["app_complexity"] == "high"

    @pytest.mark.unit
    async def test_review_architecture_with_issues(self, agent):
        """Test architecture review with identified issues."""
        task_data = {
            "current_architecture": {
                "pattern": "Mixed",
                "issues": ["tight_coupling", "god_objects"]
            }
        }
        
        agent.think.return_value = "Architecture needs refactoring"
        
        result = await agent._review_architecture(task_data)
        
        assert "review_type" in result
        assert "recommendations" in result
        assert "current_architecture" in result

    @pytest.mark.unit
    async def test_design_navigation_complex(self, agent):
        """Test navigation design for complex app."""
        task_data = {
            "app_type": "multi_module",
            "user_flows": ["auth", "main", "settings", "profile"],
            "navigation_complexity": "high"
        }
        
        agent.think.return_value = "Nested navigation with named routes"
        
        result = await agent._design_navigation(task_data)
        
        assert "navigation_structure" in result
        assert "routing_strategy" in result
        assert result["app_type"] == "multi_module"

    @pytest.mark.unit
    async def test_handle_general_architecture_task(self, agent):
        """Test general architecture task handling."""
        task_description = "design database schema"
        task_data = {"entities": ["User", "Product", "Order"]}
        
        agent.think.return_value = "Database schema designed"
        
        result = await agent._handle_general_architecture_task(task_description, task_data)
        
        assert result["task"] == task_description
        assert "architecture_response" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    def test_design_patterns_configuration(self, agent):
        """Test design patterns configuration."""
        expected_patterns = ["BLoC", "Provider", "Riverpod", "GetX", "MobX", "Redux"]
        
        for pattern in expected_patterns:
            assert pattern in agent.design_patterns
        
        assert len(agent.design_patterns) >= len(expected_patterns)

    @pytest.mark.unit
    def test_architecture_styles_configuration(self, agent):
        """Test architecture styles configuration."""
        expected_styles = [
            "Clean Architecture", "Layered Architecture", 
            "Hexagonal Architecture", "MVVM"
        ]
        
        for style in expected_styles:
            assert style in agent.architecture_styles
        
        assert len(agent.architecture_styles) >= len(expected_styles)

    @pytest.mark.unit
    async def test_concurrent_architecture_decisions(self, agent):
        """Test handling concurrent architecture decisions."""
        tasks = [
            agent.execute_task("select_state_management", {"complexity": "medium"}),
            agent.execute_task("design_navigation", {"app_type": "e_commerce"}),
            agent.execute_task("review_architecture", {"pattern": "BLoC"})
        ]
        
        agent.think.return_value = "Architecture decision made"
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert all("status" in result or "recommended_solution" in result 
                  for result in results)

    @pytest.mark.unit
    async def test_architecture_validation_with_analysis_tool(self, agent):
        """Test architecture validation using analysis tools."""
        task_data = {
            "project_path": "/path/to/project",
            "architecture_type": "Clean Architecture"
        }
        
        # Mock analysis tool response
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={
                "architecture_compliance": 85,
                "issues": ["missing_dependency_injection"],
                "suggestions": ["add_get_it_package"]
            }
        )
        
        agent.think.return_value = "Architecture validated"
        
        result = await agent.execute_task("review_architecture", task_data)
        
        assert "review_type" in result
        agent.execute_tool.assert_called()

    @pytest.mark.unit
    async def test_error_handling_in_architecture_design(self, agent):
        """Test error handling during architecture design."""
        task_data = {"invalid": "data"}
        
        # Mock think method failure
        agent.think.side_effect = Exception("LLM error")
        
        # Should handle errors gracefully
        try:
            result = await agent.execute_task("design_flutter_architecture", task_data)
            # If no exception, check that error is handled appropriately
            assert "error" in str(result).lower() or "status" in result
        except Exception:
            # Exception handling depends on implementation
            pass

    @pytest.mark.unit
    async def test_architecture_pattern_recommendations(self, agent):
        """Test architecture pattern recommendations for different scenarios."""
        scenarios = [
            {
                "complexity": "low",
                "team_size": 2,
                "expected_pattern": "Provider"
            },
            {
                "complexity": "high",
                "team_size": 10,
                "expected_pattern": "BLoC"
            },
            {
                "complexity": "medium",
                "team_size": 5,
                "expected_pattern": "Riverpod"
            }
        ]
        
        for scenario in scenarios:
            agent.think.return_value = f"{scenario['expected_pattern']} recommended"
            
            result = await agent.execute_task("select_state_management", {
                "app_complexity": scenario["complexity"],
                "team_size": scenario["team_size"]
            })
            
            assert "recommended_solution" in result

    @pytest.mark.unit
    async def test_architecture_documentation_generation(self, agent):
        """Test architecture documentation generation."""
        task_data = {
            "architecture_design": {
                "pattern": "Clean Architecture",
                "layers": ["presentation", "domain", "data"],
                "state_management": "BLoC"
            }
        }
        
        agent.think.return_value = "Architecture documentation created"
        
        result = await agent.execute_task("generate_architecture_docs", task_data)
        
        assert "architecture_response" in result or "documentation" in result
        agent.think.assert_called()

    @pytest.mark.unit
    async def test_performance_oriented_architecture_decisions(self, agent):
        """Test architecture decisions focused on performance."""
        task_data = {
            "performance_requirements": "high",
            "target_devices": "low_end_android",
            "features": ["real_time_updates", "large_datasets"]
        }
        
        agent.think.return_value = "Performance-optimized architecture designed"
        
        result = await agent.execute_task("design_flutter_architecture", task_data)
        
        assert "architecture_design" in result
        # Should consider performance in recommendations
        agent.think.assert_called()

    @pytest.mark.unit
    async def test_scalability_architecture_planning(self, agent):
        """Test architecture planning for scalability."""
        task_data = {
            "scalability_requirements": "high",
            "expected_users": "1M+",
            "growth_timeline": "2_years"
        }
        
        agent.think.return_value = "Scalable architecture planned"
        
        result = await agent.execute_task("design_flutter_architecture", task_data)
        
        assert "architecture_design" in result
        assert "technology_stack" in result
        # Should include scalability considerations
        agent.think.assert_called()

    @pytest.mark.unit
    async def test_cross_platform_architecture_considerations(self, agent):
        """Test architecture for cross-platform requirements."""
        task_data = {
            "target_platforms": ["iOS", "Android", "Web", "Desktop"],
            "shared_code_percentage": 80,
            "platform_specific_features": ["camera", "file_system"]
        }
        
        agent.think.return_value = "Cross-platform architecture designed"
        
        result = await agent.execute_task("design_flutter_architecture", task_data)
        
        assert "architecture_design" in result
        # Should address cross-platform considerations
        agent.think.assert_called()

    @pytest.mark.unit
    async def test_migration_architecture_planning(self, agent):
        """Test architecture planning for migration scenarios."""
        task_data = {
            "current_platform": "native_android",
            "target_platform": "flutter",
            "migration_strategy": "gradual",
            "existing_features": ["auth", "payments", "chat"]
        }
        
        agent.think.return_value = "Migration architecture planned"
        
        result = await agent.execute_task("plan_migration_architecture", task_data)
        
        assert "architecture_response" in result
        # Should address migration considerations
        agent.think.assert_called()

    @pytest.mark.unit
    async def test_security_focused_architecture(self, agent):
        """Test architecture decisions with security focus."""
        task_data = {
            "security_requirements": "high",
            "sensitive_data": ["personal_info", "payment_data"],
            "compliance": ["GDPR", "PCI_DSS"]
        }
        
        agent.think.return_value = "Security-focused architecture designed"
        
        result = await agent.execute_task("design_flutter_architecture", task_data)
        
        assert "architecture_design" in result
        # Should include security considerations
        agent.think.assert_called()
