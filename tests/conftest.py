"""
Test configuration and fixtures for FlutterSwarm tests.
"""

import pytest
import asyncio
import tempfile
import shutil
import os
import sys
from unittest.mock import Mock, MagicMock, AsyncMock, patch
from typing import Dict, Any, Generator
from datetime import datetime

# Add the parent directory to sys.path to import FlutterSwarm modules
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Mock the problematic modules BEFORE any imports
sys.modules['agents.orchestrator_agent'] = MagicMock()
sys.modules['agents.architecture_agent'] = MagicMock()
sys.modules['agents.implementation_agent'] = MagicMock()
sys.modules['agents.testing_agent'] = MagicMock()
sys.modules['agents.security_agent'] = MagicMock()
sys.modules['agents.devops_agent'] = MagicMock()
sys.modules['agents.documentation_agent'] = MagicMock()
sys.modules['agents.performance_agent'] = MagicMock()
sys.modules['agents.quality_assurance_agent'] = MagicMock()
sys.modules['langchain_anthropic'] = MagicMock()
sys.modules['monitoring.agent_logger'] = MagicMock()
sys.modules['monitoring.build_monitor'] = MagicMock()
sys.modules['monitoring.live_display'] = MagicMock()

# Mock tools modules with the necessary attributes
mock_tool_status = MagicMock()
mock_tool_status.SUCCESS = "success"
mock_tool_status.ERROR = "error"
mock_tool_status.WARNING = "warning"

mock_tool_result = MagicMock()
mock_tool_result.return_value = MagicMock()

mock_tools = MagicMock()
mock_tools.base_tool = MagicMock()
mock_tools.base_tool.ToolResult = mock_tool_result
mock_tools.base_tool.ToolStatus = mock_tool_status

sys.modules['tools'] = mock_tools
sys.modules['tools.base_tool'] = mock_tools.base_tool

# Import shared components first (these have fewer dependencies)
from shared.state import SharedState, AgentStatus, MessageType, ProjectState, AgentState
from tests.mocks.mock_implementations import MockAgent, MockConfigManager, MockToolManager

# Now safe to import these
from flutter_swarm import FlutterSwarm
from config.config_manager import ConfigManager


@pytest.fixture
def temp_directory():
    """Create a temporary directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_anthropic_client():
    """Mock Anthropic client for testing."""
    with patch('langchain_anthropic.ChatAnthropic') as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance
        # Mock the completion response
        mock_response = MagicMock()
        mock_response.content = "Mocked AI response"
        mock_instance.invoke.return_value = mock_response
        mock_instance.ainvoke.return_value = mock_response
        yield mock_instance


@pytest.fixture
def clean_shared_state():
    """Provide a clean shared state for each test."""
    state = SharedState()
    # Clear any existing data
    state._agents.clear()
    state._projects.clear()
    state._messages.clear()
    state._message_queue.clear()
    state._subscribers.clear()
    state._current_project_id = None
    state._issues.clear()
    yield state


@pytest.fixture
def sample_agent_state():
    """Sample agent state for testing."""
    return AgentState(
        agent_id="test_agent",
        status=AgentStatus.IDLE,
        last_update=datetime.now(),  # Fixed attribute name
        current_task=None,
        progress=0.0,
        capabilities=["test_capability"],
        metadata={}
    )


@pytest.fixture
def sample_project_state():
    """Sample project state for testing."""
    return ProjectState(
        project_id="test_project_123",
        name="Test Project",
        description="A test project for unit testing",
        requirements=["req1", "req2"],
        current_phase="development",
        progress=0.5,
        files_created={},
        architecture_decisions=[],
        test_results={},
        security_findings=[],
        performance_metrics={},
        documentation={},
        deployment_config={}
    )


class TestAgentMock(MockAgent):
    """TestAgentMock for agent collaboration tests."""
    pass

@pytest.fixture
def mock_config():
    """Mock config manager for testing."""
    return MockConfigManager()

@pytest.fixture
def mock_tool_manager():
    """Mock tool manager for testing."""
    return MockToolManager()


@pytest.fixture
def flutter_swarm_instance(mock_anthropic_client, mock_config, mock_tool_manager):
    """Create a FlutterSwarm instance for testing."""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        swarm = FlutterSwarm()
        return swarm


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "name": "Test Flutter App",
        "description": "A test Flutter application",
        "requirements": [
            "Cross-platform mobile app",
            "User authentication",
            "Data persistence",
            "Clean architecture"
        ],
        "features": [
            "User login/registration",
            "Data synchronization",
            "Offline support",
            "Push notifications"
        ]
    }


# Add any other fixtures as needed for the test suite.
