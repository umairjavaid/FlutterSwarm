"""
Base agent class for FlutterSwarm.
All specialized agents inherit from this base class.
"""

import asyncio
import yaml
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from shared.state import shared_state, AgentStatus, MessageType, AgentMessage
from config.config_manager import get_config
from tools import ToolManager, AgentToolbox, ToolResult
import os
from dotenv import load_dotenv
import logging

load_dotenv()

class BaseAgent(ABC):
    """
    Base class for all FlutterSwarm agents.
    Provides common functionality and enforces the agent interface.
    """
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self._config_manager = get_config()
        self.agent_config = self._config_manager.get_agent_config(agent_id)
        
        # Setup logging
        self._setup_logging()
        
        # Initialize LLM with configuration
        self.llm = self._initialize_llm()
        
        # Initialize tools
        self.tool_manager = ToolManager()
        self.tools = self.tool_manager.create_agent_toolbox(agent_id)
        
        # Register with shared state
        shared_state.register_agent(
            agent_id=self.agent_id,
            capabilities=self.agent_config.get("capabilities", [])
        )
        
        self.is_running = False
        self.current_task = None
        
        self.logger.info(f"🤖 {self.agent_config.get('name', agent_id)} initialized with {len(self.tools.list_available_tools())} tools")
    
    def _setup_logging(self) -> None:
        """Setup agent-specific logging."""
        log_config = self._config_manager.get_log_config()
        self.logger = logging.getLogger(f"flutterswarm.{self.agent_id}")
        
        if not self.logger.handlers:
            # Create console handler if enabled
            if log_config.get('console', True):
                console_handler = logging.StreamHandler()
                formatter = logging.Formatter(log_config.get('format', 
                    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                console_handler.setFormatter(formatter)
                self.logger.addHandler(console_handler)
            
            # Set log level
            level = getattr(logging, log_config.get('level', 'INFO').upper())
            self.logger.setLevel(level)
    
    def _initialize_llm(self) -> ChatAnthropic:
        """Initialize the LangChain LLM with agent-specific configuration."""
        # Get LLM configuration (primary by default, with agent-specific overrides)
        llm_config = self._config_manager.get_llm_config()
        agent_llm_config = self.agent_config.get('llm', {})
        
        # Merge configurations
        final_config = {**llm_config, **agent_llm_config}
        
        # Get API key from environment
        api_key_env = final_config.get('api_key_env', 'ANTHROPIC_API_KEY')
        api_key = final_config.get('api_key') or os.getenv(api_key_env)
        
        if not api_key:
            # Try fallback configuration
            fallback_config = self._config_manager.get_llm_config(fallback=True)
            fallback_api_key_env = fallback_config.get('api_key_env', 'OPENAI_API_KEY')
            api_key = os.getenv(fallback_api_key_env)
            
            if not api_key:
                raise ValueError(f"No API key found in environment variables: {api_key_env}, {fallback_api_key_env}")
        
        # Get default model from config
        default_model = self._config_manager.get('agents.llm.primary.model', 'claude-3-5-sonnet-20241022')
        default_temperature = self._config_manager.get('agents.llm.primary.temperature', 0.7)
        default_max_tokens = self._config_manager.get('agents.llm.primary.max_tokens', 4000)
        
        return ChatAnthropic(
            model=final_config.get("model", default_model),
            temperature=final_config.get("temperature", default_temperature),
            max_tokens=final_config.get("max_tokens", default_max_tokens),
            anthropic_api_key=api_key
        )
    
    async def start(self) -> None:
        """Start the agent's main loop."""
        self.is_running = True
        shared_state.update_agent_status(self.agent_id, AgentStatus.IDLE)
        
        self.logger.info(f"🚀 {self.agent_config.get('name', self.agent_id)} started")
        
        # Get performance configuration
        perf_config = self._config_manager.get_performance_config()
        heartbeat_interval = perf_config.get('heartbeat_interval', 30)
        
        while self.is_running:
            try:
                # Check for new messages
                messages = shared_state.get_messages(self.agent_id)
                for message in messages:
                    await self._handle_message(message)
                
                # Perform periodic tasks
                await self._periodic_task()
                
                # Use configurable sync interval
                sync_interval = self._config_manager.get('system.performance.state_sync_interval', 2)
                await asyncio.sleep(sync_interval)
                
            except Exception as e:
                self.logger.error(f"❌ Error in {self.agent_id}: {str(e)}")
                shared_state.update_agent_status(
                    self.agent_id, 
                    AgentStatus.ERROR,
                    metadata={"error": str(e)}
                )
                
                # Get retry configuration
                error_config = self._config_manager.get('system.error_handling', {})
                retry_delay = error_config.get('retry_delay', 5)
                await asyncio.sleep(retry_delay)
    
    async def stop(self) -> None:
        """Stop the agent."""
        self.is_running = False
        shared_state.update_agent_status(self.agent_id, AgentStatus.IDLE)
        self.logger.info(f"🛑 {self.agent_config.get('name', self.agent_id)} stopped")
    
    async def _handle_message(self, message: AgentMessage) -> None:
        """Handle incoming messages."""
        try:
            if message.message_type == MessageType.TASK_REQUEST:
                await self._handle_task_request(message)
            elif message.message_type == MessageType.COLLABORATION_REQUEST:
                await self._handle_collaboration_request(message)
            elif message.message_type == MessageType.STATE_SYNC:
                await self._handle_state_sync(message)
            else:
                await self._handle_custom_message(message)
        except Exception as e:
            self.logger.error(f"❌ Error handling message in {self.agent_id}: {str(e)}")
    
    async def _handle_task_request(self, message: AgentMessage) -> None:
        """Handle task requests."""
        task_description = message.content.get("task_description", "")
        task_data = message.content.get("task_data", {})
        
        shared_state.update_agent_status(
            self.agent_id,
            AgentStatus.WORKING,
            current_task=task_description
        )
        
        try:
            result = await self.execute_task(task_description, task_data)
            
            # Send completion message
            shared_state.send_message(
                from_agent=self.agent_id,
                to_agent=message.from_agent,
                message_type=MessageType.TASK_COMPLETED,
                content={
                    "task_id": message.id,
                    "result": result,
                    "success": True
                }
            )
            
            shared_state.update_agent_status(self.agent_id, AgentStatus.IDLE)
            
        except Exception as e:
            shared_state.send_message(
                from_agent=self.agent_id,
                to_agent=message.from_agent,
                message_type=MessageType.ERROR_REPORT,
                content={
                    "task_id": message.id,
                    "error": str(e),
                    "success": False
                }
            )
            shared_state.update_agent_status(self.agent_id, AgentStatus.ERROR)
    
    async def _handle_collaboration_request(self, message: AgentMessage) -> None:
        """Handle collaboration requests from other agents."""
        collaboration_type = message.content.get("type", "")
        data = message.content.get("data", {})
        
        response = await self.collaborate(collaboration_type, data)
        
        shared_state.send_message(
            from_agent=self.agent_id,
            to_agent=message.from_agent,
            message_type=MessageType.STATUS_UPDATE,
            content={
                "collaboration_response": response,
                "collaboration_id": message.id
            }
        )
    
    async def _handle_state_sync(self, message: AgentMessage) -> None:
        """Handle state synchronization messages."""
        await self.on_state_change(message.content)
    
    async def _handle_custom_message(self, message: AgentMessage) -> None:
        """Handle custom message types. Override in subclasses."""
        pass
    
    async def _periodic_task(self) -> None:
        """Periodic task execution. Override in subclasses."""
        pass
    
    def send_message_to_agent(self, to_agent: str, message_type: MessageType, 
                             content: Dict[str, Any], priority: int = 1) -> str:
        """Send a message to another agent."""
        return shared_state.send_message(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            priority=priority
        )
    
    def broadcast_message(self, message_type: MessageType, content: Dict[str, Any]) -> str:
        """Broadcast a message to all agents."""
        return shared_state.send_message(
            from_agent=self.agent_id,
            to_agent=None,
            message_type=message_type,
            content=content
        )
    
    def get_collaboration_context(self) -> Dict[str, Any]:
        """Get full collaboration context."""
        return shared_state.get_collaboration_context(self.agent_id)
    
    def get_project_state(self):
        """Get current project state."""
        return shared_state.get_project_state()
    
    def get_other_agents(self) -> Dict[str, Any]:
        """Get information about other agents."""
        all_agents = shared_state.get_agent_states()
        return {aid: state for aid, state in all_agents.items() if aid != self.agent_id}
    
    async def think(self, prompt: str, context: Dict[str, Any] = None) -> str:
        """Use LLM to think/reason about a problem."""
        system_prompt = f"""
        You are the {self.agent_config['name']}.
        Role: {self.agent_config['role']}
        Capabilities: {', '.join(self.agent_config['capabilities'])}
        
        You are part of a multi-agent system building Flutter applications.
        You have access to shared state and can collaborate with other agents.
        
        Current context: {context or 'No additional context'}
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        response = await self.llm.ainvoke(messages)
        return response.content
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """
        Execute a tool with the given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult with execution outcome
        """
        self.logger.debug(f"🔧 Executing tool: {tool_name}")
        result = await self.tools.execute(tool_name, **kwargs)
        
        if result.status.value != "success":
            self.logger.warning(f"⚠️ Tool '{tool_name}' failed: {result.error}")
        else:
            self.logger.debug(f"✅ Tool '{tool_name}' completed successfully")
            
        return result
    
    async def run_command(self, command: str, **kwargs) -> ToolResult:
        """
        Execute a shell command using the terminal tool.
        
        Args:
            command: Command to execute
            **kwargs: Additional parameters
            
        Returns:
            ToolResult with command output
        """
        return await self.execute_tool("terminal", command=command, **kwargs)
    
    async def read_file(self, file_path: str, **kwargs) -> ToolResult:
        """Read a file using the file tool."""
        return await self.execute_tool("file", operation="read", file_path=file_path, **kwargs)
    
    async def write_file(self, file_path: str, content: str, **kwargs) -> ToolResult:
        """Write a file using the file tool."""
        return await self.execute_tool("file", operation="write", file_path=file_path, content=content, **kwargs)

    # Abstract methods that must be implemented by subclasses
    
    @abstractmethod
    async def execute_task(self, task_description: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific task. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def collaborate(self, collaboration_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collaboration with other agents. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    async def on_state_change(self, change_data: Dict[str, Any]) -> None:
        """React to state changes. Must be implemented by subclasses."""
        pass
