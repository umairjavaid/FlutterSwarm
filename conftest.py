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
def mock_config():
    """Fixture for a mock config manager."""
    from tests.mocks.mock_implementations import MockConfigManager
    return MockConfigManager()


@pytest.fixture
def mock_tool_manager():
    """Fixture for a mock tool manager."""
    from tests.mocks.mock_implementations import MockToolManager
    return MockToolManager()


@pytest.fixture
def agent_capabilities():
    """Fixture for agent capabilities from test constants."""
    from tests.fixtures.test_constants import AGENT_CAPABILITIES
    return AGENT_CAPABILITIES


@pytest.fixture(autouse=True)
def patch_shared_state(monkeypatch, clean_shared_state):
    """Patch the global shared_state in all modules to use the test's clean_shared_state."""
    import shared.state as shared_state_module
    monkeypatch.setattr(shared_state_module, "shared_state", clean_shared_state)
    import flutter_swarm as flutter_swarm_module
    monkeypatch.setattr(flutter_swarm_module, "shared_state", clean_shared_state)
    # Patch in all agent modules
    import agents.orchestrator_agent as orchestrator_agent_module
    monkeypatch.setattr(orchestrator_agent_module, "shared_state", clean_shared_state)
    import agents.architecture_agent as architecture_agent_module
    monkeypatch.setattr(architecture_agent_module, "shared_state", clean_shared_state)
    import agents.implementation_agent as implementation_agent_module
    monkeypatch.setattr(implementation_agent_module, "shared_state", clean_shared_state)
    import agents.testing_agent as testing_agent_module
    monkeypatch.setattr(testing_agent_module, "shared_state", clean_shared_state)
    import agents.security_agent as security_agent_module
    monkeypatch.setattr(security_agent_module, "shared_state", clean_shared_state)
    import agents.devops_agent as devops_agent_module
    monkeypatch.setattr(devops_agent_module, "shared_state", clean_shared_state)
    import agents.documentation_agent as documentation_agent_module
    monkeypatch.setattr(documentation_agent_module, "shared_state", clean_shared_state)
    import agents.performance_agent as performance_agent_module
    monkeypatch.setattr(performance_agent_module, "shared_state", clean_shared_state)
    import agents.quality_assurance_agent as quality_assurance_agent_module
    monkeypatch.setattr(quality_assurance_agent_module, "shared_state", clean_shared_state)
