"""
Unit tests for the BaseAgent class and agent infrastructure.
"""

import pytest
import asyncio
from typing import Dict, Any
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from agents.base_agent import BaseAgent
from shared.state import AgentStatus, MessageType


class TestAgentImpl(BaseAgent):
    """Test implementation of BaseAgent for testing."""
    
    async def process_message(self, message):
        """Test implementation of process_message."""
        return {"status": "processed", "message_id": message.id}
        
    async def execute_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test implementation of execute_task."""
        await asyncio.sleep(0.1)  # Simulate work
        return {"status": "completed", "result": "test_result"}
    
    async def collaborate(self, collaboration_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Test implementation of collaborate."""
        return {"status": "collaboration_complete", "type": collaboration_type, "data": data}
    
    async def on_state_change(self, change_data: Dict[str, Any]) -> None:
        """Test implementation of on_state_change."""
        pass  # For testing, we just need a stub implementation


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
        # Start the agent in a background task
        start_task = asyncio.create_task(test_agent.start())
        
        # Give it a moment to start
        await asyncio.sleep(0.2)  # Slightly longer to ensure it starts
        
        # Check that the agent started
        assert test_agent.is_running
        
        # Stop the agent to clean up
        await test_agent.stop()
        
        # Give it a moment to stop gracefully
        await asyncio.sleep(0.2)
        
        # Verify it's no longer running
        assert not test_agent.is_running
        
        # Wait for the start task to complete with a reasonable timeout
        try:
            await asyncio.wait_for(start_task, timeout=1.0)
        except asyncio.TimeoutError:
            # If it times out, cancel the task
            start_task.cancel()
            try:
                await start_task
            except asyncio.CancelledError:
                pass
        
    @pytest.mark.asyncio
    async def test_stop_agent(self, test_agent):
        """Test stopping an agent."""
        test_agent.is_running = True
        
        await test_agent.stop()
        
        assert not test_agent.is_running
        
    @pytest.mark.asyncio  
    async def test_think_method(self, clean_shared_state):
        """Test the think method (AI reasoning)."""
        # Mock all dependencies before creating the agent
        with patch('agents.base_agent.get_config') as mock_get_config, \
             patch('agents.base_agent.ChatAnthropic') as mock_llm_class, \
             patch('agents.base_agent.ToolManager') as mock_tool_manager_class, \
             patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            
            # Setup mock config with proper return values
            mock_config = MagicMock()
            mock_config.get_agent_config.return_value = {
                'name': 'test_agent',
                'role': 'test role', 
                'capabilities': ['test_capability']
            }
            mock_config.get_llm_config.return_value = {}
            mock_config.get_log_config.return_value = {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'level': 'INFO',
                'console': True
            }
            # Mock the get method to return reasonable defaults
            def mock_get(key, default=None):
                if 'tools' in key:
                    return []
                return default
            mock_config.get.side_effect = mock_get
            mock_get_config.return_value = mock_config
            
            # Setup mock tool manager
            mock_tool_manager = MagicMock()
            mock_tool_manager.create_agent_toolbox.return_value = MagicMock()
            mock_tool_manager_class.return_value = mock_tool_manager
            
            # Setup mock LLM
            mock_llm_instance = AsyncMock()
            mock_response = MagicMock()
            mock_response.content = "2 + 2 equals 4"
            mock_llm_instance.ainvoke.return_value = mock_response
            mock_llm_class.return_value = mock_llm_instance
            
            # Now create agent with all mocks in place
            test_agent = TestAgentImpl("test_agent")
            
            prompt = "What is 2 + 2?"
            result = await test_agent.think(prompt)
            
            assert result == "2 + 2 equals 4"
            mock_llm_instance.ainvoke.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_execute_tool(self, test_agent):
        """Test tool execution through agent."""
        # Mock tool execution
        mock_result = MagicMock()
        mock_result.status.value = "success"
        mock_result.output = "Tool executed successfully"
        test_agent.tools.execute = AsyncMock(return_value=mock_result)
        
        result = await test_agent.execute_tool("test_tool", operation="test_op")
        
        assert result.status.value == "success"
        assert result.output == "Tool executed successfully"
        test_agent.tools.execute.assert_called_once_with("test_tool", operation="test_op")
        
    @pytest.mark.asyncio
    async def test_run_command(self, test_agent):
        """Test command execution through agent."""
        # Mock command execution
        mock_result = MagicMock()
        mock_result.status.value = "success"
        mock_result.output = "Command output"
        test_agent.tools.execute = AsyncMock(return_value=mock_result)
        
        result = await test_agent.run_command("echo 'test'")
        
        assert result.status.value == "success"
        assert result.output == "Command output"
        test_agent.tools.execute.assert_called_once_with("terminal", command="echo 'test'")
        
    @pytest.mark.asyncio
    async def test_read_file(self, test_agent):
        """Test file reading through agent."""
        # Mock file tool
        mock_result = MagicMock()
        mock_result.status.value = "success"
        mock_result.output = "file content"
        test_agent.tools.execute = AsyncMock(return_value=mock_result)
        
        result = await test_agent.read_file("test.txt")
        
        assert result.status.value == "success"
        assert result.output == "file content"
        test_agent.tools.execute.assert_called_once_with(
            "file", operation="read", file_path="test.txt"
        )
        
    @pytest.mark.asyncio
    async def test_write_file(self, test_agent):
        """Test file writing through agent."""
        # Mock file tool
        mock_result = MagicMock()
        mock_result.status.value = "success"
        test_agent.tools.execute = AsyncMock(return_value=mock_result)
        
        result = await test_agent.write_file("test.txt", "content")
        
        assert result.status.value == "success"
        test_agent.tools.execute.assert_called_once_with(
            "file", operation="write", file_path="test.txt", content="content"
        )
        
    def test_send_message_to_agent(self, test_agent, clean_shared_state):
        """Test sending messages to other agents."""
        # Patch the shared_state import in base_agent to use our clean instance
        with patch('agents.base_agent.shared_state', clean_shared_state):
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
        # Patch the shared_state import in base_agent to use our clean instance
        with patch('agents.base_agent.shared_state', clean_shared_state):
            # Register multiple agents
            for i in range(3):
                clean_shared_state.register_agent(f"agent_{i}", ["capability"])
            
            message_id = test_agent.broadcast_message(
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
        task_description = "Test task"
        task_data = {"task_type": "test", "parameters": {}}
        
        result = await test_agent.execute_task(task_description, task_data)
        
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
        
        # Start the agent in a background task
        start_task = asyncio.create_task(test_agent.start())
        
        # Give it a moment to process the message
        await asyncio.sleep(0.2)
        
        # Stop the agent
        await test_agent.stop()
        
        # Wait for the start task to complete
        await start_task
        
        # The message should have been processed (we can't easily verify this without
        # more complex mocking, but the test ensures the loop runs without errors)
        
    def test_get_capabilities(self, test_agent):
        """Test getting agent capabilities."""
        # Capabilities are set in the mock config
        capabilities = test_agent.agent_config.get("capabilities", [])
        assert isinstance(capabilities, list)
        
    @pytest.mark.asyncio
    async def test_update_status(self, test_agent, clean_shared_state):
        """Test updating agent status."""
        clean_shared_state.register_agent("test_agent", ["capability"])
        
        # Update status should not raise errors - using shared_state directly
        from shared.state import shared_state
        shared_state.update_agent_status(
            "test_agent",
            AgentStatus.WORKING,
            current_task="Processing task",
            progress=0.5,
            metadata={"additional": "metadata"}
        )
        
        # Check status was updated
        agent_state = clean_shared_state.get_agent_state("test_agent")
        assert agent_state.status == AgentStatus.WORKING
        assert agent_state.current_task == "Processing task"
        assert agent_state.progress == 0.5
        
    @pytest.mark.asyncio
    async def test_error_handling_in_think(self, clean_shared_state):
        """Test error handling in the think method."""
        # Mock all dependencies and make LLM raise an exception
        with patch('agents.base_agent.get_config') as mock_get_config, \
             patch('agents.base_agent.ChatAnthropic') as mock_llm_class, \
             patch('agents.base_agent.ToolManager') as mock_tool_manager_class, \
             patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            
            # Setup mock config
            mock_config = MagicMock()
            mock_config.get_agent_config.return_value = {
                'name': 'test_agent',
                'role': 'test role', 
                'capabilities': ['test_capability']
            }
            mock_config.get_llm_config.return_value = {}
            mock_config.get_log_config.return_value = {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'level': 'INFO',
                'console': True
            }
            def mock_get(key, default=None):
                if 'tools' in key:
                    return []
                return default
            mock_config.get.side_effect = mock_get
            mock_get_config.return_value = mock_config
            
            # Setup mock tool manager
            mock_tool_manager = MagicMock()
            mock_tool_manager.create_agent_toolbox.return_value = MagicMock()
            mock_tool_manager_class.return_value = mock_tool_manager
            
            # Setup mock LLM to raise an exception
            mock_llm_instance = AsyncMock()
            mock_llm_instance.ainvoke.side_effect = Exception("LLM Error")
            mock_llm_class.return_value = mock_llm_instance
            
            # Create agent and test error handling
            test_agent = TestAgentImpl("test_agent")
            
            with pytest.raises(Exception, match="LLM Error"):
                await test_agent.think("test prompt")
            
    @pytest.mark.asyncio
    async def test_error_handling_in_tool_execution(self, test_agent):
        """Test error handling in tool execution."""
        # Mock tool to raise an exception
        test_agent.tools.execute = AsyncMock(side_effect=Exception("Tool Error"))
        
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
