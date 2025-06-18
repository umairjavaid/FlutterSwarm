"""
Unit tests for the BaseAgent class and agent infrastructure.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from agents.base_agent import BaseAgent
from shared.state import AgentStatus, MessageType


class TestAgentImpl(BaseAgent):
    """Test implementation of BaseAgent for testing."""
    
    async def process_message(self, message):
        """Test implementation of process_message."""
        return {"status": "processed", "message_id": message.id}
        
    async def execute_task(self, task_data):
        """Test implementation of execute_task."""
        await asyncio.sleep(0.1)  # Simulate work
        return {"status": "completed", "result": "test_result"}


@pytest.mark.unit
class TestBaseAgent:
    """Test suite for BaseAgent class."""
    
    @pytest.fixture
    def test_agent(self, mock_anthropic_client, mock_config, mock_tool_manager):
        """Create a test agent instance."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            agent = TestAgentImpl("test_agent")
            return agent
            
    def test_initialization(self, test_agent):
        """Test agent initialization."""
        assert test_agent.agent_id == "test_agent"
        assert test_agent.llm is not None
        assert test_agent.tool_manager is not None
        assert test_agent.tools is not None
        assert not test_agent.is_running
        assert test_agent.current_task is None
        
    @pytest.mark.asyncio
    async def test_start_agent(self, test_agent, clean_shared_state):
        """Test starting an agent."""
        # Mock the run method to avoid infinite loop
        test_agent._run = AsyncMock()
        
        await test_agent.start()
        
        assert test_agent.is_running
        test_agent._run.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_stop_agent(self, test_agent):
        """Test stopping an agent."""
        test_agent.is_running = True
        
        await test_agent.stop()
        
        assert not test_agent.is_running
        
    @pytest.mark.asyncio
    async def test_think_method(self, test_agent):
        """Test the think method (AI reasoning)."""
        prompt = "What is 2 + 2?"
        
        # Mock the LLM response
        mock_response = MagicMock()
        mock_response.content = "2 + 2 equals 4"
        test_agent.llm.ainvoke = AsyncMock(return_value=mock_response)
        
        result = await test_agent.think(prompt)
        
        assert result == "2 + 2 equals 4"
        test_agent.llm.ainvoke.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_execute_tool(self, test_agent):
        """Test tool execution through agent."""
        # Mock tool execution
        mock_result = MagicMock()
        mock_result.status = "SUCCESS"
        mock_result.output = "Tool executed successfully"
        test_agent.tools.execute_tool = AsyncMock(return_value=mock_result)
        
        result = await test_agent.execute_tool("test_tool", operation="test_op")
        
        assert result.status == "SUCCESS"
        assert result.output == "Tool executed successfully"
        test_agent.tools.execute_tool.assert_called_once_with("test_tool", operation="test_op")
        
    @pytest.mark.asyncio
    async def test_run_command(self, test_agent):
        """Test command execution through agent."""
        # Mock command execution
        mock_result = MagicMock()
        mock_result.status = "SUCCESS"
        mock_result.output = "Command output"
        test_agent.tools.execute_command = AsyncMock(return_value=mock_result)
        
        result = await test_agent.run_command("echo 'test'")
        
        assert result.status == "SUCCESS"
        assert result.output == "Command output"
        test_agent.tools.execute_command.assert_called_once_with("echo 'test'")
        
    @pytest.mark.asyncio
    async def test_read_file(self, test_agent):
        """Test file reading through agent."""
        # Mock file tool
        mock_result = MagicMock()
        mock_result.status = "SUCCESS"
        mock_result.output = "file content"
        test_agent.tools.execute_tool = AsyncMock(return_value=mock_result)
        
        result = await test_agent.read_file("test.txt")
        
        assert result.status == "SUCCESS"
        assert result.output == "file content"
        test_agent.tools.execute_tool.assert_called_once_with(
            "file", operation="read", file_path="test.txt"
        )
        
    @pytest.mark.asyncio
    async def test_write_file(self, test_agent):
        """Test file writing through agent."""
        # Mock file tool
        mock_result = MagicMock()
        mock_result.status = "SUCCESS"
        test_agent.tools.execute_tool = AsyncMock(return_value=mock_result)
        
        result = await test_agent.write_file("test.txt", "content")
        
        assert result.status == "SUCCESS"
        test_agent.tools.execute_tool.assert_called_once_with(
            "file", operation="write", file_path="test.txt", content="content"
        )
        
    def test_send_message_to_agent(self, test_agent, clean_shared_state):
        """Test sending messages to other agents."""
        # Register recipient agent
        clean_shared_state.register_agent("recipient", ["capability"])
        
        message_id = test_agent.send_message_to_agent(
            to_agent="recipient",
            message_type=MessageType.TASK_REQUEST,
            content={"task": "test_task"},
            priority=3
        )
        
        assert message_id is not None
        
        # Check message was queued
        messages = clean_shared_state.get_messages("recipient")
        assert len(messages) == 1
        assert messages[0].from_agent == "test_agent"
        assert messages[0].content["task"] == "test_task"
        
    def test_broadcast_message(self, test_agent, clean_shared_state):
        """Test broadcasting messages to all agents."""
        # Register multiple agents
        for i in range(3):
            clean_shared_state.register_agent(f"agent_{i}", ["capability"])
        
        message_id = test_agent.send_message_to_agent(
            to_agent=None,  # Broadcast
            message_type=MessageType.STATUS_UPDATE,
            content={"status": "active"}
        )
        
        assert message_id is not None
        
        # Check all agents received the message
        for i in range(3):
            messages = clean_shared_state.get_messages(f"agent_{i}")
            assert len(messages) == 1
            
    @pytest.mark.asyncio
    async def test_process_message_implementation(self, test_agent):
        """Test the process_message implementation."""
        from shared.state import AgentMessage
        
        message = AgentMessage(
            id="test_msg",
            from_agent="sender",
            to_agent="test_agent",
            message_type=MessageType.TASK_REQUEST,
            content={"task": "test"},
            timestamp=datetime.now()
        )
        
        result = await test_agent.process_message(message)
        
        assert result["status"] == "processed"
        assert result["message_id"] == "test_msg"
        
    @pytest.mark.asyncio
    async def test_execute_task_implementation(self, test_agent):
        """Test the execute_task implementation."""
        task_data = {"task_type": "test", "parameters": {}}
        
        result = await test_agent.execute_task(task_data)
        
        assert result["status"] == "completed"
        assert result["result"] == "test_result"
        
    @pytest.mark.asyncio
    async def test_agent_main_loop(self, test_agent, clean_shared_state):
        """Test the agent's main processing loop."""
        # Register the agent
        clean_shared_state.register_agent("test_agent", ["capability"])
        
        # Send a test message
        message_id = clean_shared_state.send_message(
            from_agent="sender",
            to_agent="test_agent",
            message_type=MessageType.TASK_REQUEST,
            content={"task": "test"}
        )
        
        # Mock the _run method to process one iteration
        original_run = test_agent._run
        
        async def mock_run():
            # Process messages once
            messages = clean_shared_state.get_messages("test_agent", limit=1)
            if messages:
                await test_agent.process_message(messages[0])
            test_agent.is_running = False  # Stop after one iteration
            
        test_agent._run = mock_run
        
        # Start and run the agent briefly
        await test_agent.start()
        
        # The message should have been processed
        # (In a real implementation, you'd check the result of message processing)
        
    def test_get_capabilities(self, test_agent):
        """Test getting agent capabilities."""
        # Capabilities are set in the mock config
        capabilities = test_agent.agent_config.get("capabilities", [])
        assert isinstance(capabilities, list)
        
    @pytest.mark.asyncio
    async def test_update_status(self, test_agent, clean_shared_state):
        """Test updating agent status."""
        clean_shared_state.register_agent("test_agent", ["capability"])
        
        # Update status should not raise errors
        test_agent._update_status(
            AgentStatus.WORKING,
            "Processing task",
            0.5,
            {"additional": "metadata"}
        )
        
        # Check status was updated
        agent_state = clean_shared_state.get_agent_state("test_agent")
        assert agent_state.status == AgentStatus.WORKING
        assert agent_state.current_task == "Processing task"
        assert agent_state.progress == 0.5
        
    @pytest.mark.asyncio
    async def test_error_handling_in_think(self, test_agent):
        """Test error handling in the think method."""
        # Mock LLM to raise an exception
        test_agent.llm.ainvoke = AsyncMock(side_effect=Exception("LLM Error"))
        
        with pytest.raises(Exception, match="LLM Error"):
            await test_agent.think("test prompt")
            
    @pytest.mark.asyncio
    async def test_error_handling_in_tool_execution(self, test_agent):
        """Test error handling in tool execution."""
        # Mock tool to raise an exception
        test_agent.tools.execute_tool = AsyncMock(side_effect=Exception("Tool Error"))
        
        with pytest.raises(Exception, match="Tool Error"):
            await test_agent.execute_tool("test_tool")
            
    def test_agent_configuration(self, test_agent):
        """Test agent configuration loading."""
        assert test_agent.agent_config is not None
        assert isinstance(test_agent.agent_config, dict)
        
    @pytest.mark.asyncio
    async def test_logging_setup(self, test_agent):
        """Test that logging is properly set up."""
        # The agent should have a logger
        assert hasattr(test_agent, 'logger') or hasattr(test_agent, '_logger')
        # This test ensures the _setup_logging method doesn't crash
        
    def test_agent_id_uniqueness(self, mock_anthropic_client, mock_config, mock_tool_manager):
        """Test that each agent has a unique ID."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            agent1 = TestAgentImpl("agent_1")
            agent2 = TestAgentImpl("agent_2")
            
            assert agent1.agent_id != agent2.agent_id
            assert agent1.agent_id == "agent_1"
            assert agent2.agent_id == "agent_2"
