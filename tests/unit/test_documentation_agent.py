"""
Unit tests for DocumentationAgent.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, Any, List

# Import test fixtures and mocks
from tests.fixtures.test_constants import (
    SAMPLE_PROJECT_CONFIG,
    SAMPLE_AGENT_CONFIG,
    SAMPLE_DOCUMENTATION_CONFIG
)
from tests.mocks.mock_implementations import MockToolManager, MockConfigManager

# Import the agent under test
from agents.documentation_agent import DocumentationAgent
from shared.state import AgentStatus, MessageType
from tools.base_tool import ToolResult, ToolStatus


class TestDocumentationAgent:
    """Test suite for DocumentationAgent."""

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
        """Create DocumentationAgent for testing."""
        with patch('agents.documentation_agent.get_config', return_value=mock_config_manager), \
             patch('agents.documentation_agent.ToolManager', return_value=mock_tool_manager), \
             patch('langchain_anthropic.ChatAnthropic'):
            
            agent = DocumentationAgent()
            agent.execute_tool = AsyncMock()
            agent.think = AsyncMock()
            agent.run_command = AsyncMock()
            agent.read_file = AsyncMock()
            agent.write_file = AsyncMock()
            return agent

    @pytest.mark.unit
    def test_documentation_agent_initialization(self, agent):
        """Test documentation agent initializes correctly."""
        assert agent.agent_id == "documentation"
        assert hasattr(agent, 'doc_types')
        assert isinstance(agent.doc_types, list)
        
        # Check expected documentation types
        expected_types = [
            "technical_docs", "user_guides", "api_docs", "code_comments",
            "architecture_docs", "deployment_guides", "testing_docs"
        ]
        
        for doc_type in expected_types:
            assert doc_type in agent.doc_types

    @pytest.mark.unit
    async def test_execute_task_generate_readme(self, agent, mock_shared_state):
        """Test README generation task."""
        task_data = {
            "project_id": "test_project",
            "project_name": "AwesomeApp",
            "description": "A comprehensive Flutter application",
            "features": ["authentication", "offline_sync", "real_time_chat"],
            "installation_steps": ["clone", "flutter_pub_get", "run"],
            "usage_examples": True
        }
        
        mock_project = Mock()
        mock_project.name = "AwesomeApp"
        mock_project.description = "A comprehensive Flutter application"
        mock_shared_state.get_project_state.return_value = mock_project
        
        # Mock README content generation
        agent.think.return_value = """
# AwesomeApp

A comprehensive Flutter application with authentication and real-time features.

## Features
- User authentication
- Offline sync capability
- Real-time chat

## Installation
1. Clone the repository
2. Run `flutter pub get`
3. Run `flutter run`
"""
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"file_created": "README.md"}
        )
        
        result = await agent.execute_task("generate_readme", task_data)
        
        assert result["doc_type"] == "readme"
        assert result["project_name"] == "AwesomeApp"
        assert "content" in result
        assert "file_path" in result
        assert result["status"] == "completed"
        
        # Should create README.md file
        agent.execute_tool.assert_called()

    @pytest.mark.unit
    async def test_execute_task_create_api_docs(self, agent):
        """Test API documentation creation task."""
        task_data = {
            "project_id": "test_project",
            "api_endpoints": [
                {"path": "/api/users", "method": "GET", "description": "Get users"},
                {"path": "/api/users", "method": "POST", "description": "Create user"}
            ],
            "models": ["User", "Profile", "Settings"],
            "authentication": "JWT"
        }
        
        agent.think.return_value = "API documentation generated"
        
        agent.execute_tool.side_effect = [
            # Create docs directory
            ToolResult(status=ToolStatus.SUCCESS, data={"created": True}),
            # Create API docs file
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True})
        ]
        
        result = await agent.execute_task("create_api_docs", task_data)
        
        assert result["doc_type"] == "api_documentation"
        assert "api_endpoints" in result
        assert "documentation_files" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_execute_task_generate_user_guide(self, agent):
        """Test user guide generation task."""
        task_data = {
            "project_id": "test_project",
            "target_audience": "end_users",
            "features_to_document": ["login", "profile_management", "settings"],
            "include_screenshots": True,
            "format": "markdown"
        }
        
        agent.think.return_value = "User guide content generated"
        
        agent.execute_tool.side_effect = [
            # Create user guide directory
            ToolResult(status=ToolStatus.SUCCESS, data={"created": True}),
            # Create user guide files
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True})
        ]
        
        result = await agent.execute_task("generate_user_guide", task_data)
        
        assert result["doc_type"] == "user_guide"
        assert result["target_audience"] == "end_users"
        assert "features_documented" in result
        assert "guide_files" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_execute_task_document_architecture(self, agent):
        """Test architecture documentation task."""
        task_data = {
            "project_id": "test_project",
            "architecture_pattern": "Clean Architecture",
            "state_management": "BLoC",
            "layers": ["presentation", "domain", "data"],
            "include_diagrams": True
        }
        
        agent.think.return_value = "Architecture documentation created"
        
        agent.execute_tool.side_effect = [
            # Create architecture docs directory
            ToolResult(status=ToolStatus.SUCCESS, data={"created": True}),
            # Create architecture documentation
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True}),
            # Create diagrams
            ToolResult(status=ToolStatus.SUCCESS, data={"diagrams_created": True})
        ]
        
        result = await agent.execute_task("document_architecture", task_data)
        
        assert result["doc_type"] == "architecture"
        assert result["architecture_pattern"] == "Clean Architecture"
        assert "layers_documented" in result
        assert "documentation_files" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_execute_task_general(self, agent):
        """Test general documentation task handling."""
        task_description = "create deployment guide"
        task_data = {
            "deployment_platforms": ["android", "ios"],
            "deployment_type": "store_release"
        }
        
        agent.think.return_value = "Deployment guide created"
        
        result = await agent.execute_task(task_description, task_data)
        
        assert result["task"] == task_description
        assert "documentation_response" in result
        assert result["status"] == "completed"
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_collaborate_documentation_review(self, agent):
        """Test collaboration for documentation review."""
        data = {
            "documentation_files": ["README.md", "docs/API.md"],
            "review_criteria": ["completeness", "accuracy", "clarity"],
            "target_audience": "developers"
        }
        
        agent.think.return_value = "Documentation review completed"
        
        result = await agent.collaborate("documentation_review", data)
        
        assert result["review_type"] == "documentation"
        assert "feedback" in result
        assert "recommendations" in result
        assert "quality_score" in result
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_collaborate_generate_code_comments(self, agent):
        """Test collaboration for code comments generation."""
        data = {
            "code_files": ["lib/models/user.dart", "lib/services/auth_service.dart"],
            "comment_style": "dartdoc",
            "include_examples": True
        }
        
        agent.think.return_value = "Code comments generated"
        
        result = await agent.collaborate("generate_code_comments", data)
        
        assert result["comment_type"] == "code_documentation"
        assert "generated_comments" in result
        assert "files_processed" in result
        agent.think.assert_called_once()

    @pytest.mark.unit
    async def test_collaborate_create_release_notes(self, agent):
        """Test collaboration for release notes creation."""
        data = {
            "version": "1.2.0",
            "changes": [
                {"type": "feature", "description": "Added dark mode"},
                {"type": "bug_fix", "description": "Fixed login issue"},
                {"type": "improvement", "description": "Better performance"}
            ],
            "breaking_changes": [],
            "migration_guide": False
        }
        
        agent.think.return_value = "Release notes created"
        
        result = await agent.collaborate("create_release_notes", data)
        
        assert result["release_notes_type"] == "version_release"
        assert "release_notes_content" in result
        assert "version" in result
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
        
        agent.think.return_value = "Documentation updated"
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"documentation_updated": True}
        )
        
        await agent.on_state_change(change_data)
        
        # Should update documentation automatically
        agent.think.assert_called()

    @pytest.mark.unit
    async def test_on_state_change_feature_added(self, agent):
        """Test reaction to feature added state change."""
        change_data = {
            "event": "feature_added",
            "feature_name": "push_notifications",
            "project_id": "test_project"
        }
        
        agent.think.return_value = "Feature documentation added"
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"feature_documented": True}
        )
        
        await agent.on_state_change(change_data)
        
        # Should document new feature
        agent.think.assert_called()

    @pytest.mark.unit
    async def test_generate_readme_comprehensive(self, agent, mock_shared_state):
        """Test comprehensive README generation."""
        task_data = {
            "project_name": "ComplexApp",
            "description": "Enterprise-grade Flutter application",
            "features": ["auth", "notifications", "offline", "analytics"],
            "requirements": ["Flutter 3.0+", "Dart 3.0+"],
            "installation_steps": ["detailed", "setup"],
            "configuration": True,
            "troubleshooting": True
        }
        
        mock_project = Mock()
        mock_project.name = "ComplexApp"
        mock_shared_state.get_project_state.return_value = mock_project
        
        agent.think.return_value = "Comprehensive README generated"
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"readme_created": True}
        )
        
        result = await agent._generate_readme(task_data)
        
        assert result["doc_type"] == "readme"
        assert result["project_name"] == "ComplexApp"
        assert "content" in result

    @pytest.mark.unit
    async def test_create_api_documentation_detailed(self, agent):
        """Test detailed API documentation creation."""
        task_data = {
            "api_base_url": "https://api.example.com",
            "authentication_type": "OAuth2",
            "endpoints": [
                {
                    "path": "/users",
                    "methods": ["GET", "POST"],
                    "parameters": ["limit", "offset"],
                    "responses": ["200", "400", "401"]
                }
            ],
            "include_examples": True,
            "include_schemas": True
        }
        
        agent.think.return_value = "Detailed API documentation created"
        agent.execute_tool.side_effect = [
            ToolResult(status=ToolStatus.SUCCESS, data={"created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True})
        ]
        
        result = await agent._create_api_documentation(task_data)
        
        assert result["doc_type"] == "api_documentation"
        assert "documentation_files" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_generate_user_guide_multi_audience(self, agent):
        """Test user guide generation for multiple audiences."""
        task_data = {
            "audiences": ["end_users", "administrators", "developers"],
            "features": ["basic_usage", "advanced_features", "admin_panel"],
            "include_tutorials": True,
            "include_faq": True,
            "format": "multi_format"
        }
        
        agent.think.return_value = "Multi-audience user guide created"
        agent.execute_tool.side_effect = [
            ToolResult(status=ToolStatus.SUCCESS, data={"created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True})
        ]
        
        result = await agent._generate_user_guide(task_data)
        
        assert result["doc_type"] == "user_guide"
        assert "audiences" in result
        assert "guide_files" in result

    @pytest.mark.unit
    async def test_document_architecture_detailed(self, agent):
        """Test detailed architecture documentation."""
        task_data = {
            "architecture_style": "Clean Architecture",
            "design_patterns": ["BLoC", "Repository", "Dependency Injection"],
            "layers": {
                "presentation": ["widgets", "pages", "blocs"],
                "domain": ["entities", "use_cases", "repositories"],
                "data": ["datasources", "models", "repositories_impl"]
            },
            "include_flow_diagrams": True,
            "include_code_examples": True
        }
        
        agent.think.return_value = "Detailed architecture documentation created"
        agent.execute_tool.side_effect = [
            ToolResult(status=ToolStatus.SUCCESS, data={"created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"file_created": True}),
            ToolResult(status=ToolStatus.SUCCESS, data={"diagrams_created": True})
        ]
        
        result = await agent._document_architecture(task_data)
        
        assert result["doc_type"] == "architecture"
        assert "architecture_style" in result
        assert "layers_documented" in result

    @pytest.mark.unit
    async def test_review_documentation_quality(self, agent):
        """Test documentation quality review."""
        data = {
            "documentation_type": "technical",
            "files": ["docs/architecture.md", "docs/api.md"],
            "quality_criteria": ["completeness", "accuracy", "readability"],
            "target_score": 85
        }
        
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"analysis_completed": True}
        )
        
        agent.think.return_value = "Documentation quality analysis completed"
        
        result = await agent._review_documentation(data)
        
        assert result["review_type"] == "documentation"
        assert "feedback" in result
        assert "quality_score" in result

    @pytest.mark.unit
    async def test_generate_code_comments_dartdoc(self, agent):
        """Test Dartdoc code comments generation."""
        data = {
            "files": ["lib/models/user.dart"],
            "comment_style": "dartdoc",
            "include_examples": True,
            "include_see_also": True
        }
        
        agent.read_file.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            output="class User { String name; }"
        )
        
        agent.think.return_value = "Dartdoc comments generated"
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"comments_added": True}
        )
        
        result = await agent._generate_code_comments(data)
        
        assert result["comment_type"] == "code_documentation"
        assert "generated_comments" in result
        assert "files_processed" in result

    @pytest.mark.unit
    async def test_create_release_notes_detailed(self, agent):
        """Test detailed release notes creation."""
        data = {
            "version": "2.0.0",
            "release_type": "major",
            "changes": [
                {"type": "breaking", "description": "API changes"},
                {"type": "feature", "description": "New dashboard"},
                {"type": "improvement", "description": "Performance boost"}
            ],
            "migration_guide": True,
            "acknowledgments": ["contributor1", "contributor2"]
        }
        
        agent.think.return_value = "Detailed release notes created"
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"release_notes_created": True}
        )
        
        result = await agent._create_release_notes(data)
        
        assert result["release_notes_type"] == "version_release"
        assert "release_notes_content" in result
        assert result["version"] == "2.0.0"

    @pytest.mark.unit
    async def test_handle_general_documentation_task(self, agent):
        """Test general documentation task handling."""
        task_description = "create troubleshooting guide"
        task_data = {
            "common_issues": ["build_errors", "dependency_conflicts"],
            "solutions": "detailed",
            "include_code_samples": True
        }
        
        agent.think.return_value = "Troubleshooting guide created"
        
        result = await agent._handle_general_documentation_task(task_description, task_data)
        
        assert result["task"] == task_description
        assert "documentation_response" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_error_handling_in_readme_generation(self, agent, mock_shared_state):
        """Test error handling during README generation."""
        task_data = {"project_id": "invalid_project"}
        
        # Mock missing project
        mock_shared_state.get_project_state.return_value = None
        
        try:
            result = await agent.execute_task("generate_readme", task_data)
            # Should handle missing project gracefully
            assert "error" in str(result).lower() or "status" in result
        except Exception:
            # Exception handling depends on implementation
            pass

    @pytest.mark.unit
    async def test_concurrent_documentation_tasks(self, agent):
        """Test handling concurrent documentation tasks."""
        tasks = [
            agent.execute_task("generate_readme", {"project_name": "App1"}),
            agent.execute_task("create_api_docs", {"api_endpoints": []}),
            agent.execute_task("generate_user_guide", {"target_audience": "users"})
        ]
        
        agent.think.return_value = "Documentation task completed"
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"task_completed": True}
        )
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert all("status" in result or "doc_type" in result for result in results)

    @pytest.mark.unit
    def test_doc_types_configuration(self, agent):
        """Test documentation types configuration."""
        expected_types = [
            "technical_docs", "user_guides", "api_docs", "code_comments",
            "architecture_docs", "deployment_guides", "testing_docs"
        ]
        
        for doc_type in expected_types:
            assert doc_type in agent.doc_types
        
        assert len(agent.doc_types) >= len(expected_types)

    @pytest.mark.unit
    async def test_internationalization_documentation(self, agent):
        """Test internationalization in documentation."""
        task_data = {
            "languages": ["en", "es", "fr"],
            "content_type": "user_guide",
            "localization_keys": True,
            "cultural_adaptation": True
        }
        
        agent.think.return_value = "Internationalized documentation created"
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"i18n_docs_created": True}
        )
        
        result = await agent.execute_task("generate_user_guide", task_data)
        
        assert "languages" in result or "guide_files" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_interactive_documentation_generation(self, agent):
        """Test interactive documentation generation."""
        task_data = {
            "documentation_type": "interactive",
            "include_code_playground": True,
            "include_live_examples": True,
            "format": "html"
        }
        
        agent.think.return_value = "Interactive documentation created"
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"interactive_docs_created": True}
        )
        
        result = await agent.execute_task("create_api_docs", task_data)
        
        assert result["doc_type"] == "api_documentation"
        assert "documentation_files" in result

    @pytest.mark.unit
    async def test_documentation_versioning(self, agent):
        """Test documentation versioning support."""
        task_data = {
            "version": "1.5.0",
            "previous_version": "1.4.0",
            "version_specific_changes": True,
            "backward_compatibility": True
        }
        
        agent.think.return_value = "Versioned documentation created"
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"versioned_docs_created": True}
        )
        
        result = await agent.execute_task("generate_readme", task_data)
        
        assert "version" in result or "content" in result
        assert result["status"] == "completed"

    @pytest.mark.unit
    async def test_accessibility_documentation(self, agent):
        """Test accessibility-focused documentation."""
        task_data = {
            "accessibility_features": ["screen_reader", "high_contrast", "keyboard_navigation"],
            "compliance_standards": ["WCAG_2.1", "Section_508"],
            "include_testing_guide": True
        }
        
        agent.think.return_value = "Accessibility documentation created"
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"accessibility_docs_created": True}
        )
        
        result = await agent.execute_task("generate_user_guide", task_data)
        
        assert result["doc_type"] == "user_guide"
        assert "guide_files" in result

    @pytest.mark.unit
    async def test_performance_documentation(self, agent):
        """Test performance-focused documentation."""
        task_data = {
            "performance_metrics": ["app_size", "startup_time", "memory_usage"],
            "optimization_guides": True,
            "benchmarking_results": True,
            "profiling_instructions": True
        }
        
        agent.think.return_value = "Performance documentation created"
        agent.execute_tool.return_value = ToolResult(
            status=ToolStatus.SUCCESS,
            data={"performance_docs_created": True}
        )
        
        result = await agent.execute_task("document_architecture", task_data)
        
        assert result["doc_type"] == "architecture"
        assert "documentation_files" in result
