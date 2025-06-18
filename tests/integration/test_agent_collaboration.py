"""
Integration tests for agent collaboration and communication.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from shared.state import shared_state, AgentStatus, MessageType
from flutter_swarm import FlutterSwarm
from tests.mocks.mock_implementations import MockAgent


@pytest.mark.integration
class TestAgentCollaboration:
    """Test suite for agent collaboration scenarios."""
    
    @pytest.fixture
    def mock_agents(self):
        """Create mock agents for testing."""
        agents = {
            "orchestrator": MockAgent("orchestrator", ["coordination", "planning"]),
            "implementation": MockAgent("implementation", ["coding", "flutter"]),
            "testing": MockAgent("testing", ["testing", "quality_assurance"]),
            "security": MockAgent("security", ["security", "analysis"])
        }
        return agents
    
    @pytest.mark.asyncio
    async def test_basic_agent_communication(self, clean_shared_state, mock_agents):
        """Test basic communication between agents."""
        state = clean_shared_state
        
        # Register agents
        for agent_id, agent in mock_agents.items():
            state.register_agent(agent_id, agent.capabilities)
        
        # Send message from orchestrator to implementation
        message_id = state.send_message(
            from_agent="orchestrator",
            to_agent="implementation",
            message_type=MessageType.TASK_REQUEST,
            content={
                "task_type": "create_feature",
                "feature_name": "user_authentication",
                "requirements": ["login", "registration", "password_reset"]
            },
            priority=5
        )
        
        assert message_id is not None
        
        # Check message was received
        messages = state.get_messages("implementation")
        assert len(messages) == 1
        
        message = messages[0]
        assert message.from_agent == "orchestrator"
        assert message.message_type == MessageType.TASK_REQUEST
        assert message.content["feature_name"] == "user_authentication"
        
    @pytest.mark.asyncio
    async def test_broadcast_communication(self, clean_shared_state, mock_agents):
        """Test broadcast communication to all agents."""
        state = clean_shared_state
        
        # Register agents
        for agent_id, agent in mock_agents.items():
            state.register_agent(agent_id, agent.capabilities)
        
        # Broadcast status update
        message_id = state.send_message(
            from_agent="orchestrator",
            to_agent=None,  # Broadcast
            message_type=MessageType.STATUS_UPDATE,
            content={
                "project_status": "in_progress",
                "current_phase": "implementation",
                "progress": 0.3
            }
        )
        
        assert message_id is not None
        
        # Check all agents (except sender) received the message
        for agent_id in mock_agents.keys():
            if agent_id != "orchestrator":
                messages = state.get_messages(agent_id)
                assert len(messages) == 1
                assert messages[0].content["project_status"] == "in_progress"
    
    @pytest.mark.asyncio
    async def test_multi_agent_workflow(self, clean_shared_state, mock_agents):
        """Test a complete multi-agent workflow."""
        state = clean_shared_state
        
        # Register agents
        for agent_id, agent in mock_agents.items():
            state.register_agent(agent_id, agent.capabilities)
        
        # Create a project
        project_id = state.create_project(
            name="Test App",
            description="A test application",
            requirements=["auth", "database", "ui"]
        )
        
        # Orchestrator assigns tasks to implementation agent
        task_message_id = state.send_message(
            from_agent="orchestrator",
            to_agent="implementation",
            message_type=MessageType.TASK_REQUEST,
            content={
                "task_type": "implement_feature",
                "feature": "authentication",
                "project_id": project_id
            }
        )
        
        # Implementation agent updates status
        state.update_agent_status(
            "implementation",
            AgentStatus.WORKING,
            "Implementing authentication feature",
            0.2
        )
        
        # Implementation agent completes task and notifies testing agent
        state.send_message(
            from_agent="implementation",
            to_agent="testing",
            message_type=MessageType.COLLABORATION_REQUEST,
            content={
                "request_type": "test_feature",
                "feature": "authentication",
                "files_created": ["lib/auth/login.dart", "lib/auth/register.dart"]
            }
        )
        
        # Testing agent receives collaboration request
        test_messages = state.get_messages("testing")
        assert len(test_messages) == 1
        assert test_messages[0].message_type == MessageType.COLLABORATION_REQUEST
        
        # Security agent can also be involved
        state.send_message(
            from_agent="implementation",
            to_agent="security",
            message_type=MessageType.COLLABORATION_REQUEST,
            content={
                "request_type": "security_review",
                "feature": "authentication",
                "files": ["lib/auth/login.dart"]
            }
        )
        
        security_messages = state.get_messages("security")
        assert len(security_messages) == 1
        
    @pytest.mark.asyncio
    async def test_error_handling_and_recovery(self, clean_shared_state, mock_agents):
        """Test error handling and recovery in agent collaboration."""
        state = clean_shared_state
        
        # Register agents
        for agent_id, agent in mock_agents.items():
            state.register_agent(agent_id, agent.capabilities)
        
        # Create project
        project_id = state.create_project(
            name="Error Test App",
            description="Testing error handling",
            requirements=["feature1"]
        )
        
        # Implementation agent encounters an error
        state.update_agent_status(
            "implementation",
            AgentStatus.ERROR,
            "Failed to implement feature",
            0.1,
            {"error": "Missing dependency"}
        )
        
        # Report the issue
        issue_id = state.report_issue(project_id, {
            "reporter_agent": "implementation",
            "type": "dependency",
            "severity": "high",
            "description": "Missing required dependency for authentication",
            "affected_files": ["lib/auth/login.dart"],
            "fix_suggestions": ["Add firebase_auth dependency"]
        })
        
        assert issue_id is not None
        
        # Orchestrator can query issues and reassign task
        issues = state.get_project_issues(project_id, status="open")
        assert len(issues) == 1
        assert issues[0].reporter_agent == "implementation"
        
        # Update issue status after resolution
        success = state.update_issue_status(
            project_id,
            issue_id,
            "resolved",
            assigned_agent="orchestrator",
            resolution_notes="Added missing dependency"
        )
        
        assert success is True
        
        # Agent can continue working
        state.update_agent_status(
            "implementation",
            AgentStatus.WORKING,
            "Retrying feature implementation",
            0.2
        )
    
    @pytest.mark.asyncio
    async def test_concurrent_agent_operations(self, clean_shared_state, mock_agents):
        """Test concurrent operations between multiple agents."""
        state = clean_shared_state
        
        # Register agents
        for agent_id, agent in mock_agents.items():
            state.register_agent(agent_id, agent.capabilities)
        
        # Create multiple concurrent tasks
        async def agent_work(agent_id, task_num):
            # Simulate agent doing work
            for i in range(3):
                state.update_agent_status(
                    agent_id,
                    AgentStatus.WORKING,
                    f"Task {task_num} - Step {i+1}",
                    (i + 1) / 3
                )
                await asyncio.sleep(0.1)
            
            # Send completion message
            state.send_message(
                from_agent=agent_id,
                to_agent="orchestrator",
                message_type=MessageType.TASK_COMPLETED,
                content={
                    "task_id": f"task_{task_num}",
                    "status": "completed",
                    "agent": agent_id
                }
            )
        
        # Run multiple agents concurrently
        tasks = []
        agent_list = list(mock_agents.keys())[:3]  # Use first 3 agents
        
        for i, agent_id in enumerate(agent_list):
            task = asyncio.create_task(agent_work(agent_id, i))
            tasks.append(task)
        
        await asyncio.gather(*tasks)
        
        # Check that orchestrator received all completion messages
        orchestrator_messages = state.get_messages("orchestrator")
        assert len(orchestrator_messages) == 3
        
        for message in orchestrator_messages:
            assert message.message_type == MessageType.TASK_COMPLETED
            assert message.content["status"] == "completed"
    
    @pytest.mark.asyncio
    async def test_agent_state_synchronization(self, clean_shared_state, mock_agents):
        """Test that agent states are properly synchronized."""
        state = clean_shared_state
        
        # Register agents
        for agent_id, agent in mock_agents.items():
            state.register_agent(agent_id, agent.capabilities)
        
        # Update multiple agents concurrently
        async def update_agent_status(agent_id, status, task, progress):
            state.update_agent_status(agent_id, status, task, progress)
        
        # Update all agents
        update_tasks = []
        for i, agent_id in enumerate(mock_agents.keys()):
            task = asyncio.create_task(
                update_agent_status(
                    agent_id,
                    AgentStatus.WORKING,
                    f"Task for {agent_id}",
                    (i + 1) * 0.25
                )
            )
            update_tasks.append(task)
        
        await asyncio.gather(*update_tasks)
        
        # Verify all states are consistent
        agent_states = state.get_agent_states()
        
        for i, agent_id in enumerate(mock_agents.keys()):
            agent_state = agent_states[agent_id]
            assert agent_state.status == AgentStatus.WORKING
            assert agent_state.current_task == f"Task for {agent_id}"
            assert agent_state.progress == (i + 1) * 0.25
    
    @pytest.mark.asyncio
    async def test_collaboration_context_sharing(self, clean_shared_state, mock_agents):
        """Test sharing collaboration context between agents."""
        state = clean_shared_state
        
        # Register agents
        for agent_id, agent in mock_agents.items():
            state.register_agent(agent_id, agent.capabilities)
        
        # Create project and add some files
        project_id = state.create_project(
            name="Context Test App",
            description="Testing context sharing",
            requirements=["feature1", "feature2"]
        )
        
        state.add_project_file(project_id, "lib/main.dart", "void main() {}")
        state.add_project_file(project_id, "lib/models/user.dart", "class User {}")
        
        # Send some messages to create history
        state.send_message(
            "orchestrator", "implementation",
            MessageType.TASK_REQUEST,
            {"task": "create_models"}
        )
        
        state.send_message(
            "implementation", "testing",
            MessageType.COLLABORATION_REQUEST,
            {"request": "review_models"}
        )
        
        # Get collaboration context
        context = state.get_collaboration_context("testing")
        
        assert "agents" in context
        assert "current_project" in context
        assert "recent_messages" in context
        assert context["requesting_agent"] == "testing"
        
        # Check project info is included
        assert context["current_project"]["name"] == "Context Test App"
        
        # Check agent info is included
        assert len(context["agents"]) == len(mock_agents)
        
        # Check recent messages are included
        assert len(context["recent_messages"]) == 2
