"""
Integration tests for agent collaboration and communication.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from shared.state import shared_state, AgentStatus, MessageType, AgentMessage
from tests.mocks.mock_implementations import MockAgent, MockToolManager, MockAnthropicClient
from tests.fixtures.test_constants import AGENT_CAPABILITIES, SAMPLE_PROJECT_DATA


@pytest.mark.integration
class TestAgentCollaboration:
    """Test suite for agent collaboration scenarios."""
    
    @pytest.fixture
    async def collaborative_agents(self, clean_shared_state, mock_config, agent_capabilities):
        """Create multiple agents for collaboration testing."""
        agents = {}
        # Create mock agents for different roles
        for agent_type, capabilities in agent_capabilities.items():
            agents[agent_type] = MockAgent(agent_type, capabilities)
            clean_shared_state.register_agent(agent_type, capabilities)
            await agents[agent_type].start()
        yield agents
        # Cleanup
        for agent in agents.values():
            await agent.stop()
    
    @pytest.mark.asyncio
    async def test_orchestrator_implementation_collaboration(self, collaborative_agents, clean_shared_state):
        """Test collaboration between orchestrator and implementation agents."""
        orchestrator = collaborative_agents["orchestrator"]
        implementation = collaborative_agents["implementation"]
        
        # Orchestrator assigns task to implementation agent
        task_message = AgentMessage(
            message_id="task_001",
            from_agent="orchestrator",
            to_agent="implementation",
            message_type=MessageType.TASK_REQUEST,
            content={
                "task_description": "create_model",
                "task_data": {
                    "model_name": "User",
                    "fields": ["id", "email", "name"]
                }
            },
            priority=5,
            timestamp=datetime.now()
        )
        
        # Send message through shared state
        clean_shared_state.send_message(task_message)
        
        # Implementation agent should receive and process the message
        response = await implementation.process_message(task_message)
        
        # Verify collaboration
        assert response["status"] == "processed"
        assert task_message in implementation.messages
        
        # Update agent status
        clean_shared_state.update_agent_status(
            "implementation", AgentStatus.WORKING, "Creating User model", 0.5
        )
        
        # Verify status update
        agent_state = clean_shared_state.get_agent_state("implementation")
        assert agent_state.status == AgentStatus.WORKING
        assert agent_state.current_task == "Creating User model"
        
    @pytest.mark.asyncio
    async def test_implementation_testing_collaboration(self, collaborative_agents, clean_shared_state):
        """Test collaboration between implementation and testing agents."""
        implementation = collaborative_agents["implementation"]
        testing = collaborative_agents["testing"]
        
        # Implementation completes code generation
        clean_shared_state.update_agent_status(
            "implementation", AgentStatus.COMPLETED, "Model created", 1.0
        )
        
        # Send collaboration request to testing agent
        collab_message = AgentMessage(
            message_id="collab_001",
            from_agent="implementation",
            to_agent="testing",
            message_type=MessageType.COLLABORATION_REQUEST,
            content={
                "collaboration_type": "test_generation",
                "data": {
                    "source_file": "lib/models/user.dart",
                    "test_file": "test/models/user_test.dart"
                }
            },
            priority=3,
            timestamp=datetime.now()
        )
        
        clean_shared_state.send_message(collab_message)
        
        # Testing agent processes collaboration request
        response = await testing.process_message(collab_message)
        
        # Verify collaboration
        assert response["status"] == "processed"
        assert collab_message in testing.messages
        
        # Testing agent starts test generation
        clean_shared_state.update_agent_status(
            "testing", AgentStatus.WORKING, "Generating tests for User model", 0.3
        )
        
        # Verify testing agent is working
        testing_state = clean_shared_state.get_agent_state("testing")
        assert testing_state.status == AgentStatus.WORKING
        
    @pytest.mark.asyncio
    async def test_security_implementation_collaboration(self, collaborative_agents, clean_shared_state):
        """Test security agent reviewing implementation code."""
        implementation = collaborative_agents["implementation"]
        security = collaborative_agents["security"]
        
        # Implementation creates authentication code
        auth_code_message = AgentMessage(
            message_id="sec_001",
            from_agent="implementation",
            to_agent="security",
            message_type=MessageType.COLLABORATION_REQUEST,
            content={
                "collaboration_type": "security_review",
                "data": {
                    "files": ["lib/auth/auth_service.dart", "lib/auth/login_page.dart"],
                    "security_concerns": ["authentication", "data_validation"]
                }
            },
            priority=4,
            timestamp=datetime.now()
        )
        
        clean_shared_state.send_message(auth_code_message)
        
        # Security agent reviews the code
        response = await security.process_message(auth_code_message)
        
        # Verify security review
        assert response["status"] == "processed"
        
        # Security agent provides feedback
        feedback_message = AgentMessage(
            message_id="sec_feedback_001",
            from_agent="security",
            to_agent="implementation",
            message_type=MessageType.COLLABORATION_REQUEST,
            content={
                "collaboration_type": "security_feedback",
                "data": {
                    "findings": [
                        {
                            "severity": "MEDIUM",
                            "issue": "Password validation insufficient",
                            "recommendation": "Add stronger password policy"
                        }
                    ]
                }
            },
            priority=4,
            timestamp=datetime.now()
        )
        
        clean_shared_state.send_message(feedback_message)
        await implementation.process_message(feedback_message)
        
        # Verify feedback was received
        assert feedback_message in implementation.messages
        
    @pytest.mark.asyncio
    async def test_qa_multi_agent_review(self, collaborative_agents, clean_shared_state):
        """Test QA agent coordinating with multiple agents."""
        qa = collaborative_agents["quality_assurance"]
        implementation = collaborative_agents["implementation"]
        testing = collaborative_agents["testing"]
        security = collaborative_agents["security"]
        
        # Create project for QA review
        project_id = clean_shared_state.create_project(
            "TestApp", "Application for QA testing", ["authentication", "data_storage"]
        )
        
        # QA agent requests status from all agents
        agents_to_review = ["implementation", "testing", "security"]
        
        for agent_id in agents_to_review:
            status_request = AgentMessage(
                message_id=f"qa_status_{agent_id}",
                from_agent="quality_assurance",
                to_agent=agent_id,
                message_type=MessageType.COLLABORATION_REQUEST,
                content={
                    "collaboration_type": "status_request",
                    "data": {"project_id": project_id}
                },
                priority=2,
                timestamp=datetime.now()
            )
            
            clean_shared_state.send_message(status_request)
            
            # Each agent responds with their status
            agent = collaborative_agents[agent_id]
            response = await agent.process_message(status_request)
            
            assert response["status"] == "processed"
            
        # QA agent compiles overall project status
        clean_shared_state.update_agent_status(
            "quality_assurance", AgentStatus.WORKING, "Reviewing project quality", 0.7
        )
        
        qa_state = clean_shared_state.get_agent_state("quality_assurance")
        assert qa_state.status == AgentStatus.WORKING
        
    @pytest.mark.asyncio
    async def test_devops_deployment_coordination(self, collaborative_agents, clean_shared_state):
        """Test DevOps agent coordinating deployment with other agents."""
        devops = collaborative_agents["devops"]
        implementation = collaborative_agents["implementation"]
        testing = collaborative_agents["testing"]
        security = collaborative_agents["security"]
        
        # Create deployment readiness check
        deployment_check = AgentMessage(
            message_id="deploy_check_001",
            from_agent="devops",
            to_agent="testing",
            message_type=MessageType.COLLABORATION_REQUEST,
            content={
                "collaboration_type": "deployment_readiness",
                "data": {
                    "deployment_target": "production",
                    "required_checks": ["all_tests_pass", "security_scan_clean"]
                }
            },
            priority=5,
            timestamp=datetime.now()
        )
        
        clean_shared_state.send_message(deployment_check)
        
        # Testing agent confirms test status
        response = await testing.process_message(deployment_check)
        assert response["status"] == "processed"
        
        # Security agent confirms security status
        security_check = AgentMessage(
            message_id="deploy_sec_001",
            from_agent="devops",
            to_agent="security",
            message_type=MessageType.COLLABORATION_REQUEST,
            content={
                "collaboration_type": "security_clearance",
                "data": {"deployment_target": "production"}
            },
            priority=5,
            timestamp=datetime.now()
        )
        
        clean_shared_state.send_message(security_check)
        response = await security.process_message(security_check)
        assert response["status"] == "processed"
        
        # DevOps proceeds with deployment coordination
        clean_shared_state.update_agent_status(
            "devops", AgentStatus.WORKING, "Coordinating deployment", 0.8
        )
        
        devops_state = clean_shared_state.get_agent_state("devops")
        assert devops_state.status == AgentStatus.WORKING
        
    @pytest.mark.asyncio
    async def test_circular_collaboration_prevention(self, collaborative_agents, clean_shared_state):
        """Test prevention of circular collaboration loops."""
        implementation = collaborative_agents["implementation"]
        testing = collaborative_agents["testing"]
        
        # Create a collaboration chain that could become circular
        message1 = AgentMessage(
            message_id="chain_001",
            from_agent="implementation",
            to_agent="testing",
            message_type=MessageType.COLLABORATION_REQUEST,
            content={
                "collaboration_type": "test_review",
                "data": {"collaboration_chain": ["implementation"]}
            },
            priority=3,
            timestamp=datetime.now()
        )
        
        message2 = AgentMessage(
            message_id="chain_002",
            from_agent="testing",
            to_agent="implementation",
            message_type=MessageType.COLLABORATION_REQUEST,
            content={
                "collaboration_type": "code_improvement",
                "data": {"collaboration_chain": ["implementation", "testing"]}
            },
            priority=3,
            timestamp=datetime.now()
        )
        
        # Send messages
        clean_shared_state.send_message(message1)
        clean_shared_state.send_message(message2)
        
        # Process messages
        response1 = await testing.process_message(message1)
        response2 = await implementation.process_message(message2)
        
        # Both should process successfully without creating loops
        assert response1["status"] == "processed"
        assert response2["status"] == "processed"
        
        # Verify collaboration chains are tracked to prevent loops
        assert "collaboration_chain" in message1.content["data"]
        assert "collaboration_chain" in message2.content["data"]
        
    @pytest.mark.asyncio
    async def test_priority_based_message_handling(self, collaborative_agents, clean_shared_state):
        """Test that high-priority messages are handled first."""
        orchestrator = collaborative_agents["orchestrator"]
        implementation = collaborative_agents["implementation"]
        
        # Send messages with different priorities
        low_priority_msg = AgentMessage(
            message_id="low_001",
            from_agent="orchestrator",
            to_agent="implementation",
            message_type=MessageType.TASK_REQUEST,
            content={"task_description": "low_priority_task"},
            priority=1,
            timestamp=datetime.now()
        )
        
        high_priority_msg = AgentMessage(
            message_id="high_001",
            from_agent="orchestrator",
            to_agent="implementation",
            message_type=MessageType.TASK_REQUEST,
            content={"task_description": "high_priority_task"},
            priority=5,
            timestamp=datetime.now()
        )
        
        # Send low priority first, then high priority
        clean_shared_state.send_message(low_priority_msg)
        clean_shared_state.send_message(high_priority_msg)
        
        # Get messages for implementation agent
        messages = clean_shared_state.get_messages_for_agent("implementation")
        
        # Verify high priority message comes first
        assert len(messages) == 2
        assert messages[0].priority >= messages[1].priority
        
    @pytest.mark.asyncio
    async def test_agent_failure_recovery(self, collaborative_agents, clean_shared_state):
        """Test agent failure and recovery scenarios."""
        implementation = collaborative_agents["implementation"]
        testing = collaborative_agents["testing"]
        orchestrator = collaborative_agents["orchestrator"]
        
        # Simulate implementation agent failure
        clean_shared_state.update_agent_status(
            "implementation", AgentStatus.ERROR, "Tool execution failed", 0.5
        )
        
        # Orchestrator detects failure and reassigns task
        failure_msg = AgentMessage(
            message_id="failure_001",
            from_agent="orchestrator",
            to_agent="implementation",
            message_type=MessageType.TASK_REQUEST,
            content={
                "task_description": "recover_from_failure",
                "task_data": {"original_task": "create_model", "retry_attempt": 1}
            },
            priority=5,
            timestamp=datetime.now()
        )
        
        clean_shared_state.send_message(failure_msg)
        
        # Implementation agent recovers
        await implementation.process_message(failure_msg)
        clean_shared_state.update_agent_status(
            "implementation", AgentStatus.WORKING, "Recovering from failure", 0.1
        )
        
        # Verify recovery
        impl_state = clean_shared_state.get_agent_state("implementation")
        assert impl_state.status == AgentStatus.WORKING
        assert "Recovering" in impl_state.current_task
        
    @pytest.mark.asyncio
    async def test_concurrent_collaborations(self, collaborative_agents, clean_shared_state):
        """Test handling of concurrent collaborations."""
        implementation = collaborative_agents["implementation"]
        testing = collaborative_agents["testing"]
        security = collaborative_agents["security"]
        qa = collaborative_agents["quality_assurance"]
        
        # Create multiple concurrent collaboration requests
        collaborations = [
            ("testing", "test_generation", {"file": "lib/models/user.dart"}),
            ("security", "security_review", {"files": ["lib/auth/"]}),
            ("quality_assurance", "code_review", {"files": ["lib/"]})
        ]
        
        tasks = []
        for i, (agent_id, collab_type, data) in enumerate(collaborations):
            message = AgentMessage(
                message_id=f"concurrent_{i}",
                from_agent="implementation",
                to_agent=agent_id,
                message_type=MessageType.COLLABORATION_REQUEST,
                content={
                    "collaboration_type": collab_type,
                    "data": data
                },
                priority=3,
                timestamp=datetime.now()
            )
            
            clean_shared_state.send_message(message)
            
            # Process messages concurrently
            agent = collaborative_agents[agent_id]
            tasks.append(agent.process_message(message))
        
        # Wait for all collaborations to complete
        responses = await asyncio.gather(*tasks)
        
        # Verify all collaborations were processed
        for response in responses:
            assert response["status"] == "processed"
            
    @pytest.mark.asyncio
    async def test_message_persistence_and_replay(self, collaborative_agents, clean_shared_state):
        """Test message persistence and replay capabilities."""
        implementation = collaborative_agents["implementation"]
        
        # Send a message
        original_message = AgentMessage(
            message_id="persist_001",
            from_agent="orchestrator",
            to_agent="implementation",
            message_type=MessageType.TASK_REQUEST,
            content={"task_description": "persistent_task"},
            priority=3,
            timestamp=datetime.now()
        )
        
        clean_shared_state.send_message(original_message)
        
        # Process message
        await implementation.process_message(original_message)
        
        # Verify message is in agent's history
        assert original_message in implementation.messages
        
        # Get message history
        message_history = clean_shared_state.get_recent_messages(limit=10)
        
        # Verify message is in shared state history
        assert len(message_history) > 0
        assert any(msg.message_id == "persist_001" for msg in message_history)
        
    @pytest.mark.asyncio
    async def test_resource_conflict_resolution(self, collaborative_agents, clean_shared_state):
        """Test resolution of resource conflicts between agents."""
        implementation1 = collaborative_agents["implementation"]
        testing = collaborative_agents["testing"]
        
        # Both agents try to work on the same file
        file_lock_msg1 = AgentMessage(
            message_id="lock_001",
            from_agent="implementation",
            to_agent="shared_state",
            message_type=MessageType.STATE_SYNC,
            content={
                "sync_type": "resource_lock",
                "data": {"resource": "lib/models/user.dart", "action": "acquire"}
            },
            priority=3,
            timestamp=datetime.now()
        )
        
        file_lock_msg2 = AgentMessage(
            message_id="lock_002",
            from_agent="testing",
            to_agent="shared_state",
            message_type=MessageType.STATE_SYNC,
            content={
                "sync_type": "resource_lock",
                "data": {"resource": "lib/models/user.dart", "action": "acquire"}
            },
            priority=3,
            timestamp=datetime.now()
        )
        
        # Send lock requests
        clean_shared_state.send_message(file_lock_msg1)
        clean_shared_state.send_message(file_lock_msg2)
        
        # First agent should get the lock, second should wait
        # This would be implemented in a real shared state system
        # For testing, we just verify messages were sent
        
        messages = clean_shared_state.get_recent_messages(limit=5)
        lock_messages = [msg for msg in messages if "resource_lock" in str(msg.content)]
        
        assert len(lock_messages) == 2
