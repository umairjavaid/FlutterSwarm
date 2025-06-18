"""
Unit tests for the SharedState class.
Tests all core functionality of the shared state management system.
"""

import pytest
import asyncio
from datetime import datetime
from unittest.mock import patch, MagicMock

from shared.state import SharedState, AgentStatus, MessageType, AgentMessage, ProjectState, IssueReport


@pytest.mark.unit
class TestSharedState:
    """Test suite for SharedState class."""
    
    def test_initialization(self, clean_shared_state):
        """Test SharedState initialization."""
        state = clean_shared_state
        
        assert isinstance(state._agents, dict)
        assert isinstance(state._projects, dict)
        assert isinstance(state._messages, list)
        assert isinstance(state._message_queue, dict)
        assert isinstance(state._subscribers, dict)
        assert isinstance(state._issues, dict)
        assert state._current_project_id is None
        
    def test_register_agent(self, clean_shared_state):
        """Test agent registration."""
        state = clean_shared_state
        agent_id = "test_agent"
        capabilities = ["testing", "analysis"]
        
        state.register_agent(agent_id, capabilities)
        
        assert agent_id in state._agents
        agent_state = state._agents[agent_id]
        assert agent_state.agent_id == agent_id
        assert agent_state.status == AgentStatus.IDLE
        assert agent_state.capabilities == capabilities
        assert agent_id in state._message_queue
        
    def test_register_agent_duplicate(self, clean_shared_state):
        """Test that registering the same agent twice doesn't cause issues."""
        state = clean_shared_state
        agent_id = "test_agent"
        capabilities = ["testing"]
        
        # Register agent twice
        state.register_agent(agent_id, capabilities)
        state.register_agent(agent_id, capabilities)
        
        # Should only have one instance
        assert len([aid for aid in state._agents.keys() if aid == agent_id]) == 1
        
    def test_update_agent_status(self, clean_shared_state):
        """Test updating agent status."""
        state = clean_shared_state
        agent_id = "test_agent"
        
        # Register agent first
        state.register_agent(agent_id, ["testing"])
        
        # Update status
        new_status = AgentStatus.WORKING
        task = "Running tests"
        progress = 0.5
        metadata = {"test_count": 10}
        
        state.update_agent_status(agent_id, new_status, task, progress, metadata)
        
        agent_state = state._agents[agent_id]
        assert agent_state.status == new_status
        assert agent_state.current_task == task
        assert agent_state.progress == progress
        assert agent_state.metadata["test_count"] == 10
        
    def test_update_nonexistent_agent_status(self, clean_shared_state):
        """Test updating status of non-existent agent raises error."""
        state = clean_shared_state
        
        with pytest.raises(ValueError, match="Agent nonexistent not registered"):
            state.update_agent_status("nonexistent", AgentStatus.WORKING)
            
    def test_create_project(self, clean_shared_state):
        """Test project creation."""
        state = clean_shared_state
        name = "Test Project"
        description = "A test project"
        requirements = ["req1", "req2"]
        
        project_id = state.create_project(name, description, requirements)
        
        assert project_id is not None
        assert project_id in state._projects
        assert state._current_project_id == project_id
        
        project = state._projects[project_id]
        assert project.name == name
        assert project.description == description
        assert project.requirements == requirements
        assert project.current_phase == "planning"
        assert project.progress == 0.0
        
    def test_get_project_state(self, clean_shared_state, sample_project_state):
        """Test getting project state."""
        state = clean_shared_state
        project_id = sample_project_state.project_id
        
        # Test getting non-existent project
        assert state.get_project_state(project_id) is None
        
        # Add project and test retrieval
        state._projects[project_id] = sample_project_state
        state._current_project_id = project_id
        
        retrieved_project = state.get_project_state(project_id)
        assert retrieved_project == sample_project_state
        
        # Test getting current project
        current_project = state.get_project_state()
        assert current_project == sample_project_state
        
    def test_update_project_phase(self, clean_shared_state, sample_project_state):
        """Test updating project phase."""
        state = clean_shared_state
        project_id = sample_project_state.project_id
        state._projects[project_id] = sample_project_state
        
        new_phase = "implementation"
        new_progress = 0.5
        
        state.update_project_phase(project_id, new_phase, new_progress)
        
        project = state._projects[project_id]
        assert project.current_phase == new_phase
        assert project.progress == new_progress
        
    def test_send_message(self, clean_shared_state):
        """Test sending messages between agents."""
        state = clean_shared_state
        
        # Register agents
        state.register_agent("agent1", ["capability1"])
        state.register_agent("agent2", ["capability2"])
        
        # Send message
        message_id = state.send_message(
            from_agent="agent1",
            to_agent="agent2",
            message_type=MessageType.TASK_REQUEST,
            content={"task": "test_task"},
            priority=3
        )
        
        assert message_id is not None
        assert len(state._message_queue["agent2"]) == 1
        
        message = state._message_queue["agent2"][0]
        assert message.from_agent == "agent1"
        assert message.to_agent == "agent2"
        assert message.message_type == MessageType.TASK_REQUEST
        assert message.content["task"] == "test_task"
        assert message.priority == 3
        
    def test_broadcast_message(self, clean_shared_state):
        """Test broadcasting messages to all agents."""
        state = clean_shared_state
        
        # Register multiple agents
        agents = ["agent1", "agent2", "agent3"]
        for agent in agents:
            state.register_agent(agent, ["capability"])
        
        # Send broadcast message
        message_id = state.send_message(
            from_agent="agent1",
            to_agent=None,  # Broadcast
            message_type=MessageType.STATUS_UPDATE,
            content={"status": "working"}
        )
        
        # Check all agents received the message
        for agent in agents:
            if agent != "agent1":  # Sender doesn't receive their own broadcast
                assert len(state._message_queue[agent]) == 1
                
    def test_get_messages(self, clean_shared_state):
        """Test getting messages for an agent."""
        state = clean_shared_state
        agent_id = "test_agent"
        
        state.register_agent(agent_id, ["capability"])
        
        # Send some messages
        for i in range(3):
            state.send_message(
                from_agent="sender",
                to_agent=agent_id,
                message_type=MessageType.TASK_REQUEST,
                content={"task": f"task_{i}"}
            )
        
        # Get messages
        messages = state.get_messages(agent_id)
        assert len(messages) == 3
        
        # Check messages are sorted by priority and timestamp
        for i, message in enumerate(messages):
            assert message.content["task"] == f"task_{i}"
            
    def test_get_messages_with_limit(self, clean_shared_state):
        """Test getting messages with limit."""
        state = clean_shared_state
        agent_id = "test_agent"
        
        state.register_agent(agent_id, ["capability"])
        
        # Send many messages
        for i in range(10):
            state.send_message(
                from_agent="sender",
                to_agent=agent_id,
                message_type=MessageType.TASK_REQUEST,
                content={"task": f"task_{i}"}
            )
        
        # Get limited messages
        messages = state.get_messages(agent_id, limit=5)
        assert len(messages) == 5
        
    def test_add_project_file(self, clean_shared_state, sample_project_state):
        """Test adding files to a project."""
        state = clean_shared_state
        project_id = sample_project_state.project_id
        state._projects[project_id] = sample_project_state
        
        filename = "lib/main.dart"
        content = "void main() { print('Hello'); }"
        
        state.add_project_file(project_id, filename, content)
        
        project = state._projects[project_id]
        assert filename in project.files_created
        assert project.files_created[filename] == content
        
    def test_report_issue(self, clean_shared_state, sample_project_state):
        """Test reporting project issues."""
        state = clean_shared_state
        project_id = sample_project_state.project_id
        state._projects[project_id] = sample_project_state
        
        issue_data = {
            "reporter_agent": "security_agent",
            "type": "security",
            "severity": "high",
            "description": "Potential vulnerability found",
            "affected_files": ["lib/auth.dart"],
            "fix_suggestions": ["Use secure storage"]
        }
        
        issue_id = state.report_issue(project_id, issue_data)
        
        assert issue_id is not None
        issues = state.get_project_issues(project_id)
        assert len(issues) == 1
        
        issue = issues[0]
        assert issue.issue_id == issue_id
        assert issue.reporter_agent == "security_agent"
        assert issue.issue_type == "security"
        assert issue.severity == "high"
        assert issue.status == "open"
        
    def test_update_issue_status(self, clean_shared_state, sample_project_state):
        """Test updating issue status."""
        state = clean_shared_state
        project_id = sample_project_state.project_id
        state._projects[project_id] = sample_project_state
        
        # Report an issue first
        issue_data = {
            "reporter_agent": "test_agent",
            "description": "Test issue"
        }
        issue_id = state.report_issue(project_id, issue_data)
        
        # Update issue status
        success = state.update_issue_status(
            project_id, 
            issue_id, 
            "resolved",
            assigned_agent="fix_agent",
            resolution_notes="Fixed the issue"
        )
        
        assert success is True
        
        issues = state.get_project_issues(project_id)
        issue = issues[0]
        assert issue.status == "resolved"
        assert issue.assigned_agent == "fix_agent"
        assert issue.resolution_notes == "Fixed the issue"
        
    def test_get_agent_states(self, clean_shared_state):
        """Test getting all agent states."""
        state = clean_shared_state
        
        # Register multiple agents
        agents = ["agent1", "agent2", "agent3"]
        for agent in agents:
            state.register_agent(agent, ["capability"])
            
        agent_states = state.get_agent_states()
        
        assert len(agent_states) == 3
        for agent in agents:
            assert agent in agent_states
            assert isinstance(agent_states[agent], type(state._agents[agent]))
            
    def test_get_collaboration_context(self, clean_shared_state, sample_project_state):
        """Test getting collaboration context."""
        state = clean_shared_state
        project_id = sample_project_state.project_id
        state._projects[project_id] = sample_project_state
        state._current_project_id = project_id
        
        # Register agent and send some messages
        state.register_agent("requesting_agent", ["capability"])
        state.send_message(
            "sender", "requesting_agent", 
            MessageType.STATUS_UPDATE, 
            {"status": "active"}
        )
        
        context = state.get_collaboration_context("requesting_agent")
        
        assert "agents" in context
        assert "current_project" in context
        assert "recent_messages" in context
        assert "requesting_agent" in context
        assert "timestamp" in context
        
        assert context["requesting_agent"] == "requesting_agent"
        assert context["current_project"]["project_id"] == project_id
        
    def test_message_cleanup(self, clean_shared_state):
        """Test that old messages are cleaned up properly."""
        state = clean_shared_state
        
        # Override max messages for testing
        state._max_messages = 5
        
        state.register_agent("test_agent", ["capability"])
        
        # Send more messages than the limit
        for i in range(10):
            state.send_message(
                "sender", "test_agent",
                MessageType.TASK_REQUEST,
                {"task": f"task_{i}"}
            )
        
        # Should only keep the most recent messages
        messages = state.get_messages("test_agent")
        assert len(messages) <= state._max_messages
        
    def test_subscribe_and_notify(self, clean_shared_state):
        """Test subscription and notification system."""
        state = clean_shared_state
        
        # Create mock callback
        callback_called = []
        def mock_callback(event_type, data):
            callback_called.append((event_type, data))
        
        # Subscribe to events
        state.subscribe("test_event", mock_callback)
        
        # Trigger notification
        state._notify_subscribers("test_event", {"test": "data"})
        
        assert len(callback_called) == 1
        assert callback_called[0][0] == "test_event"
        assert callback_called[0][1]["test"] == "data"
        
    @pytest.mark.asyncio
    async def test_concurrent_operations(self, clean_shared_state):
        """Test thread safety of concurrent operations."""
        state = clean_shared_state
        
        # Register agents
        for i in range(5):
            state.register_agent(f"agent_{i}", ["capability"])
        
        # Create concurrent tasks
        tasks = []
        
        # Concurrent status updates
        for i in range(5):
            task = asyncio.create_task(
                asyncio.to_thread(
                    state.update_agent_status,
                    f"agent_{i}",
                    AgentStatus.WORKING,
                    f"task_{i}",
                    0.5
                )
            )
            tasks.append(task)
        
        # Concurrent message sending
        for i in range(10):
            task = asyncio.create_task(
                asyncio.to_thread(
                    state.send_message,
                    "sender",
                    f"agent_{i % 5}",
                    MessageType.TASK_REQUEST,
                    {"task": f"concurrent_task_{i}"}
                )
            )
            tasks.append(task)
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks)
        
        # Verify state consistency
        for i in range(5):
            agent_state = state._agents[f"agent_{i}"]
            assert agent_state.status == AgentStatus.WORKING
            assert agent_state.current_task == f"task_{i}"
            
        # Verify messages were sent
        total_messages = sum(len(queue) for queue in state._message_queue.values())
        assert total_messages >= 10  # At least the messages we sent
