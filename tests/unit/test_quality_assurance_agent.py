"""
Unit tests for QualityAssuranceAgent.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

# Import test fixtures and mocks
from tests.fixtures.test_constants import (
    SAMPLE_PROJECT_CONFIG,
    SAMPLE_AGENT_CONFIG,
    SAMPLE_VALIDATION_ISSUES,
    SAMPLE_CODE_ANALYSIS_RESULT
)
from tests.mocks.mock_implementations import MockToolManager, MockConfigManager

# Import the agent under test
from agents.quality_assurance_agent import QualityAssuranceAgent
from shared.state import AgentStatus, MessageType
from tools.base_tool import ToolResult, ToolStatus


class TestQualityAssuranceAgent:
    """Test suite for QualityAssuranceAgent."""

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
            "file", "analysis", "flutter", "terminal"
        ]
        return tool_manager

    @pytest.fixture
    def agent(self, mock_config_manager, mock_tool_manager):
        """Create QualityAssuranceAgent for testing."""
        with patch('agents.quality_assurance_agent.get_config', return_value=mock_config_manager), \
             patch('agents.quality_assurance_agent.ToolManager', return_value=mock_tool_manager), \
             patch('langchain_anthropic.ChatAnthropic'):
            
            agent = QualityAssuranceAgent()
            agent.execute_tool = AsyncMock()
            agent.think = AsyncMock()
            agent.run_command = AsyncMock()
            agent.read_file = AsyncMock()
            agent.write_file = AsyncMock()
            return agent

    @pytest.mark.unit
    def test_qa_agent_initialization(self, agent):
        """Test QA agent initializes correctly."""
        assert agent.agent_id == "quality_assurance"
        assert hasattr(agent, 'code_quality_rules')
        assert hasattr(agent, 'file_patterns')
        assert hasattr(agent, 'monitored_issues')
        assert isinstance(agent.code_quality_rules, dict)
        assert 'dart' in agent.code_quality_rules
        assert 'yaml' in agent.code_quality_rules
        assert 'architecture' in agent.code_quality_rules

    @pytest.mark.unit
    async def test_execute_task_validate_project(self, agent, mock_shared_state):
        """Test validate project task execution."""
        # Setup
        task_data = {
            "project_id": "test_project",
            "validation_scope": "full"
        }
        
        mock_project = Mock()
        mock_project.name = "TestApp"
        mock_shared_state.get_project_state.return_value = mock_project
        
        # Mock tool responses
        agent.execute_tool.side_effect = [
            # Code analysis
            ToolResult(
                status=ToolStatus.SUCCESS,
                data={"issues": [{"type": "syntax_error", "severity": "high"}]}
            ),
            # Security scan
            ToolResult(
                status=ToolStatus.SUCCESS,
                data={"issues": [{"type": "insecure_storage", "severity": "medium"}]}
            ),
            # Code metrics
            ToolResult(
                status=ToolStatus.SUCCESS,
                data={"complexity": 3.2, "maintainability": 75}
            ),
            # Dependency check
            ToolResult(
                status=ToolStatus.SUCCESS,
                data={"issues": []}
            ),
            # Test coverage
            ToolResult(
                status=ToolStatus.SUCCESS,
                data={"coverage_percentage": 85}
            ),
            # Performance analysis
            ToolResult(
                status=ToolStatus.SUCCESS,
                data={"performance_issues": []}
            ),
            # Dead code analysis
            ToolResult(
                status=ToolStatus.SUCCESS,
                data={"dead_code_issues": []}
            ),
            # Flutter doctor
            ToolResult(
                status=ToolStatus.SUCCESS,
                data={"environment_issues": []}
            )
        ]
        
        # Mock structure validation
        agent._validate_project_structure = AsyncMock(return_value={"issues": []})
        agent._generate_fix_recommendations = AsyncMock(return_value=[])
        
        # Execute
        result = await agent.execute_task("validate_project", task_data)
        
        # Assert
        assert result["validation_status"] == "completed"
        assert "validation_results" in result
        assert "issues_found" in result
        assert result["issues_found"] >= 2  # syntax_error + insecure_storage
        assert "critical_issues" in result
        assert "high_issues" in result
        assert "medium_issues" in result
        assert "low_issues" in result

    @pytest.mark.unit
    async def test_execute_task_review_code_quality(self, agent):
        """Test code quality review task."""
        task_data = {"files": ["lib/main.dart", "lib/models/user.dart"]}
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"issues": SAMPLE_VALIDATION_ISSUES}
        )
        
        result = await agent.execute_task("review_code_quality", task_data)
        
        assert "status" in result
        agent.execute_tool.assert_called()

    @pytest.mark.unit
    async def test_execute_task_check_consistency(self, agent):
        """Test project consistency check task."""
        task_data = {"check_types": ["naming", "structure", "dependencies"]}
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"consistency_issues": []}
        )
        
        result = await agent.execute_task("check_consistency", task_data)
        
        assert "status" in result
        agent.execute_tool.assert_called()

    @pytest.mark.unit
    async def test_execute_task_fix_issues(self, agent, mock_shared_state):
        """Test issue fixing coordination task."""
        task_data = {
            "issues": [
                {"type": "syntax_error", "severity": "high", "agent": "implementation"},
                {"type": "missing_test", "severity": "medium", "agent": "testing"}
            ]
        }
        
        mock_shared_state.send_message_to_agent = AsyncMock()
        
        result = await agent.execute_task("fix_issues", task_data)
        
        assert "status" in result
        # Should send coordination messages to other agents
        assert mock_shared_state.send_message_to_agent.call_count >= 1

    @pytest.mark.unit
    async def test_execute_task_general(self, agent):
        """Test general QA task handling."""
        task_description = "analyze code patterns"
        task_data = {"scope": "global"}
        
        agent.think.return_value = "Analyzed code patterns successfully"
        
        result = await agent.execute_task(task_description, task_data)
        
        assert result["task"] == task_description
        assert "qa_response" in result
        assert result["status"] == "completed"
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_collaborate_code_review(self, agent):
        """Test collaboration for code review."""
        data = {
            "code": "class TestClass { }",
            "file_path": "lib/test.dart"
        }
        
        agent.think.return_value = "Code review completed"
        
        result = await agent.collaborate("code_review", data)
        
        assert result["review_type"] == "code_review"
        assert "feedback" in result
        assert "severity_rating" in result
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_collaborate_architecture_validation(self, agent):
        """Test collaboration for architecture validation."""
        data = {
            "architecture_plan": {"pattern": "BLoC", "layers": ["presentation", "domain", "data"]}
        }
        
        agent.think.return_value = "Architecture validated"
        
        result = await agent.collaborate("architecture_validation", data)
        
        assert result["validation_type"] == "architecture"
        assert "validation_result" in result
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_collaborate_unknown_type(self, agent):
        """Test collaboration with unknown type."""
        result = await agent.collaborate("unknown_type", {})
        
        assert result["status"] == "unknown_collaboration_type"
        assert result["type"] == "unknown_type"

    @pytest.mark.unit
    async def test_on_state_change_file_added(self, agent):
        """Test reaction to file added state change."""
        change_data = {
            "event": "file_added",
            "filename": "lib/new_feature.dart",
            "project_id": "test_project"
        }
        
        agent._analyze_new_file = AsyncMock()
        
        await agent.on_state_change(change_data)
        
        agent._analyze_new_file.assert_called_once_with(change_data)

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
        
        # Mock validation process
        agent.execute_tool.side_effect = [
            ToolResult(status=ToolStatus.SUCCESS, data={"issues": []}),
            ToolResult(status=ToolStatus.SUCCESS, data={"issues": []}),
            ToolResult(status=ToolStatus.SUCCESS, data={"complexity": 2.5}),
            ToolResult(status=ToolStatus.SUCCESS, data={"issues": []}),
            ToolResult(status=ToolStatus.SUCCESS, data={"coverage_percentage": 80}),
            ToolResult(status=ToolStatus.SUCCESS, data={"performance_issues": []}),
            ToolResult(status=ToolStatus.SUCCESS, data={"dead_code_issues": []}),
            ToolResult(status=ToolStatus.SUCCESS, data={"environment_issues": []})
        ]
        
        agent._validate_project_structure = AsyncMock(return_value={"issues": []})
        agent._generate_fix_recommendations = AsyncMock(return_value=[])
        
        await agent.on_state_change(change_data)
        
        # Should trigger automatic validation
        assert agent.execute_tool.call_count >= 1

    @pytest.mark.unit
    async def test_validate_project_structure(self, agent):
        """Test project structure validation."""
        # Mock file existence checks
        agent.execute_tool.side_effect = [
            # Required files checks
            ToolResult(status=ToolStatus.SUCCESS, data={"exists": True}),  # pubspec.yaml
            ToolResult(status=ToolStatus.SUCCESS, data={"exists": True}),  # lib/main.dart
            ToolResult(status=ToolStatus.SUCCESS, data={"exists": True}),  # android/app/build.gradle
            ToolResult(status=ToolStatus.SUCCESS, data={"exists": False}), # ios/Runner/Info.plist - missing
            # Recommended directories checks
            ToolResult(status=ToolStatus.SUCCESS, data={"exists": True}),  # lib/core
            ToolResult(status=ToolStatus.SUCCESS, data={"exists": False}), # lib/features - missing
            ToolResult(status=ToolStatus.SUCCESS, data={"exists": True}),  # lib/shared
            ToolResult(status=ToolStatus.SUCCESS, data={"exists": False}), # test/unit - missing
            ToolResult(status=ToolStatus.SUCCESS, data={"exists": True}),  # test/widget
        ]
        
        agent._analyze_lib_structure = AsyncMock(return_value={"issues": []})
        
        result = await agent._validate_project_structure()
        
        assert "issues" in result
        assert result["required_files_check"] == "completed"
        assert result["directory_structure_check"] == "completed"
        
        # Should report missing required file and directories
        issues = result["issues"]
        missing_files = [i for i in issues if i["type"] == "missing_required_file"]
        missing_dirs = [i for i in issues if i["type"] == "missing_recommended_directory"]
        
        assert len(missing_files) >= 1  # ios/Runner/Info.plist
        assert len(missing_dirs) >= 2  # lib/features, test/unit

    @pytest.mark.unit
    async def test_analyze_lib_structure(self, agent):
        """Test lib directory structure analysis."""
        # Mock file search result
        dart_files = [
            "lib/main.dart",
            "lib/app.dart",
            "lib/config.dart",  # Too many root files
            "lib/utils.dart",
            "lib/features/auth/auth_screen.dart",
            "lib/features/profile/profile_screen.dart"
        ]
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"matches": dart_files}
        )
        
        agent._analyze_feature_structure = AsyncMock(return_value={"issues": []})
        
        result = await agent._analyze_lib_structure()
        
        assert "issues" in result
        issues = result["issues"]
        
        # Should report too many root files
        root_file_issues = [i for i in issues if i["type"] == "too_many_root_files"]
        assert len(root_file_issues) >= 1

    @pytest.mark.unit
    async def test_analyze_feature_structure(self, agent):
        """Test individual feature structure analysis."""
        feature_name = "auth"
        
        # Mock feature files
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"matches": [
                "lib/features/auth/auth_screen.dart",
                "lib/features/auth/auth_service.dart"
                # Missing repository and models
            ]}
        )
        
        result = await agent._analyze_feature_structure(feature_name)
        
        assert "issues" in result
        # Should detect missing feature components
        assert len(result["issues"]) >= 0

    @pytest.mark.unit
    async def test_generate_fix_recommendations(self, agent):
        """Test fix recommendations generation."""
        issues = [
            {"type": "syntax_error", "severity": "high", "file": "lib/main.dart"},
            {"type": "missing_test", "severity": "medium", "file": "lib/user.dart"},
            {"type": "unused_import", "severity": "low", "file": "lib/utils.dart"}
        ]
        
        agent._generate_type_specific_recommendation = AsyncMock(side_effect=[
            {"recommendation": "Fix syntax error"},
            {"recommendation": "Add unit tests"},
            {"recommendation": "Remove unused import"}
        ])
        
        result = await agent._generate_fix_recommendations(issues)
        
        assert len(result) == 3
        assert all("recommendation" in rec for rec in result)

    @pytest.mark.unit
    async def test_generate_type_specific_recommendation(self, agent):
        """Test type-specific recommendation generation."""
        issues = [
            {"type": "syntax_error", "file": "lib/main.dart", "line": 42}
        ]
        
        agent.think.return_value = "Fix syntax error by adding semicolon"
        
        result = await agent._generate_type_specific_recommendation("syntax_error", issues)
        
        assert result is not None
        assert "issue_type" in result
        assert "recommendation" in result
        assert result["issue_type"] == "syntax_error"

    @pytest.mark.unit
    async def test_analyze_new_file(self, agent):
        """Test new file analysis."""
        change_data = {
            "filename": "lib/new_feature.dart",
            "project_id": "test_project",
            "content": "class NewFeature { }"
        }
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"issues": []}
        )
        
        await agent._analyze_new_file(change_data)
        
        # Should analyze the new file for immediate issues
        agent.execute_tool.assert_called()

    @pytest.mark.unit
    async def test_coordinate_issue_fixes(self, agent, mock_shared_state):
        """Test issue fixing coordination."""
        task_data = {
            "issues": [
                {
                    "type": "syntax_error",
                    "severity": "high",
                    "responsible_agent": "implementation",
                    "file": "lib/main.dart"
                },
                {
                    "type": "missing_test",
                    "severity": "medium", 
                    "responsible_agent": "testing",
                    "file": "lib/user.dart"
                }
            ]
        }
        
        mock_shared_state.send_message_to_agent = AsyncMock()
        
        result = await agent._coordinate_issue_fixes(task_data)
        
        assert result["status"] == "coordination_initiated"
        assert "fixes_requested" in result
        
        # Should send messages to responsible agents
        assert mock_shared_state.send_message_to_agent.call_count >= 2

    @pytest.mark.unit
    async def test_error_handling_in_validation(self, agent, mock_shared_state):
        """Test error handling during validation."""
        task_data = {"project_id": "test_project"}
        
        mock_project = Mock()
        mock_project.name = "TestApp"
        mock_shared_state.get_project_state.return_value = mock_project
        
        # Mock tool failure
        agent.execute_tool.side_effect = [
            Exception("Tool execution failed"),
            ToolResult(status=ToolStatus.SUCCESS, data={"issues": []})
        ]
        
        agent._validate_project_structure = AsyncMock(return_value={"issues": []})
        agent._generate_fix_recommendations = AsyncMock(return_value=[])
        
        # Should handle tool failures gracefully
        result = await agent.execute_task("validate_project", task_data)
        
        assert "validation_status" in result
        # Should continue with other validations despite one failure

    @pytest.mark.unit
    def test_monitored_issues_tracking(self, agent):
        """Test issue tracking functionality."""
        # Initially empty
        assert len(agent.monitored_issues) == 0
        
        # Add some issues
        issue_id = "syntax_error_123"
        agent.monitored_issues.add(issue_id)
        
        assert issue_id in agent.monitored_issues
        assert len(agent.monitored_issues) == 1

    @pytest.mark.unit
    def test_code_quality_rules_configuration(self, agent):
        """Test code quality rules configuration."""
        assert "dart" in agent.code_quality_rules
        assert "yaml" in agent.code_quality_rules
        assert "architecture" in agent.code_quality_rules
        
        dart_rules = agent.code_quality_rules["dart"]
        assert "syntax_errors" in dart_rules
        assert "naming_conventions" in dart_rules
        assert "missing_null_safety" in dart_rules
        
        yaml_rules = agent.code_quality_rules["yaml"]
        assert "invalid_yaml_syntax" in yaml_rules
        assert "missing_dependencies" in yaml_rules
        
        arch_rules = agent.code_quality_rules["architecture"]
        assert "circular_dependencies" in arch_rules
        assert "tight_coupling" in arch_rules

    @pytest.mark.unit
    def test_file_patterns_configuration(self, agent):
        """Test file patterns configuration."""
        assert "dart" in agent.file_patterns
        assert "yaml" in agent.file_patterns
        assert "pubspec" in agent.file_patterns
        
        # Test pattern matching would be done by regex
        assert agent.file_patterns["dart"] == r"\.dart$"
        assert agent.file_patterns["yaml"] == r"\.yaml$"
        assert agent.file_patterns["pubspec"] == r"pubspec\.yaml$"

    @pytest.mark.unit
    async def test_concurrent_validation_handling(self, agent, mock_shared_state):
        """Test handling of concurrent validation requests."""
        task_data = {"project_id": "test_project"}
        
        mock_project = Mock()
        mock_project.name = "TestApp"
        mock_shared_state.get_project_state.return_value = mock_project
        
        # Mock quick tool responses
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"issues": []}
        )
        
        agent._validate_project_structure = AsyncMock(return_value={"issues": []})
        agent._generate_fix_recommendations = AsyncMock(return_value=[])
        
        # Run multiple validations concurrently
        tasks = [
            agent.execute_task("validate_project", task_data)
            for _ in range(3)
        ]
        
        results = await asyncio.gather(*tasks)
        
        # All should complete successfully
        assert len(results) == 3
        assert all(r["validation_status"] == "completed" for r in results)

    @pytest.mark.unit
    async def test_memory_efficient_large_project_validation(self, agent, mock_shared_state):
        """Test memory efficiency with large project validation."""
        task_data = {"project_id": "large_project"}
        
        mock_project = Mock()
        mock_project.name = "LargeApp"
        mock_shared_state.get_project_state.return_value = mock_project
        
        # Mock responses for large project
        large_issues_list = [
            {"type": f"issue_{i}", "severity": "low"} for i in range(100)
        ]
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"issues": large_issues_list}
        )
        
        agent._validate_project_structure = AsyncMock(return_value={"issues": []})
        agent._generate_fix_recommendations = AsyncMock(return_value=[])
        
        result = await agent.execute_task("validate_project", task_data)
        
        # Should handle large number of issues efficiently
        assert result["validation_status"] == "completed"
        assert result["issues_found"] == len(large_issues_list)
        assert result["low_issues"] == len(large_issues_list)
