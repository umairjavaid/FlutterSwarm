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
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.state import SharedState, AgentStatus, MessageType, ProjectState, AgentState
from flutter_swarm import FlutterSwarm
from config.config_manager import ConfigManager
from tests.mocks.mock_implementations import MockAgent, MockConfigManager, MockToolManager


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

# Add any other fixtures as needed for the test suite.
