"""
Base agent class for FlutterSwarm.
All specialized agents inherit from this base class.
"""

import asyncio
import yaml
import time
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
        
        # Track last status for monitoring
        self._last_status = AgentStatus.IDLE
        
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
    
    def _log_status_change(self, new_status: AgentStatus, task: Optional[str] = None):
        """Log status change to monitoring system."""
        try:
            # Import here to avoid circular imports
            from monitoring import build_monitor
            
            # Log status change to monitoring system
            build_monitor.log_agent_status_change(
                self.agent_id, self._last_status, new_status, task
            )
            self._last_status = new_status
        except ImportError:
            # Monitoring not available, skip
            pass
        except Exception as e:
            self.logger.warning(f"Failed to log status change: {e}")
    
    def _update_status(self, status: AgentStatus, task: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """Update agent status and log to monitoring."""
        # Update shared state
        shared_state.update_agent_status(self.agent_id, status, task, metadata)
        
        # Log to monitoring system
        self._log_status_change(status, task)
    
    async def start(self) -> None:
        """
        Start the agent (deprecated for LangGraph implementation).
        This method is kept for backward compatibility but is no longer used in LangGraph mode.
        """
        self.logger.info(f"🚀 {self.agent_config.get('name', self.agent_id)} initialized (LangGraph mode)")
        # In LangGraph mode, agents are stateless and invoked by the graph
    
    async def stop(self) -> None:
        """
        Stop the agent (deprecated for LangGraph implementation).
        This method is kept for backward compatibility.
        """
        self.is_running = False
        self.logger.info(f"🛑 {self.agent_config.get('name', self.agent_id)} stopped")
    
    async def _handle_message(self, message: AgentMessage) -> None:
        """Handle incoming messages."""
        try:
            # Log message to monitoring system
            self._log_message_received(message)
            
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
    
    def _log_message_received(self, message: AgentMessage):
        """Log received message to monitoring system."""
        try:
            from monitoring import build_monitor
            build_monitor.log_message(
                message.from_agent,
                self.agent_id,
                message.message_type,
                message.content,
                message.priority
            )
        except ImportError:
            pass
        except Exception as e:
            self.logger.warning(f"Failed to log message: {e}")
    
    async def _handle_task_request(self, message: AgentMessage) -> None:
        """Handle task requests."""
        task_description = message.content.get("task_description", "")
        task_data = message.content.get("task_data", {})
        
        self._update_status(
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
            
            self._update_status(AgentStatus.IDLE)
            
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
            self._update_status(AgentStatus.ERROR)
    
    async def _handle_collaboration_request(self, message: AgentMessage) -> None:
        """Handle collaboration requests from other agents."""
        collaboration_type = message.content.get("type", "")
        data = message.content.get("data", {})
        
        # Log collaboration to monitoring
        try:
            from monitoring import build_monitor
            build_monitor.log_agent_collaboration(
                message.from_agent, self.agent_id, collaboration_type, data
            )
        except ImportError:
            pass
        
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
        message_id = shared_state.send_message(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            priority=priority
        )
        
        # Log outgoing message
        try:
            from monitoring import build_monitor
            build_monitor.log_message(
                self.agent_id, to_agent, message_type, content, priority
            )
        except ImportError:
            pass
        
        return message_id
    
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
        start_time = time.time()
        self.logger.debug(f"🔧 Executing tool: {tool_name}")
        
        result = await self.tools.execute(tool_name, **kwargs)
        execution_time = time.time() - start_time
        
        # Log tool usage to monitoring system
        try:
            from monitoring import build_monitor
            build_monitor.log_tool_usage(
                self.agent_id,
                tool_name,
                kwargs.get('operation', 'execute'),
                result.status.value,
                execution_time,
                kwargs,
                {"output": result.output} if result.output else None,
                result.error
            )
        except ImportError:
            pass
        except Exception as e:
            self.logger.warning(f"Failed to log tool usage: {e}")
        
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
    
    async def collaborate(self, collaboration_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle collaboration requests. Override in subclasses."""
        return {"status": "not_implemented", "message": "Collaboration not implemented"}
    
    async def on_state_change(self, state_data: Dict[str, Any]) -> None:
        """Handle state changes. Override in subclasses."""
        pass

    async def run_command(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Run a shell command using the terminal tool."""
        try:
            result = await self.execute_tool(
                "terminal",
                operation="run_command",
                command=command,
                timeout=timeout
            )
            
            return {
                "success": result.status.value == "success",
                "output": result.data if result.data else "",
                "error": result.error if hasattr(result, 'error') else ""
            }
        except Exception as e:
            return {
                "success": False,
                "output": "",
                "error": str(e)
            }

    async def collaborate_with_agent(self, target_agent: str, collaboration_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Collaborate with another agent (simplified implementation)."""
        try:
            # Send a collaboration message
            self.send_message_to_agent(
                to_agent=target_agent,
                message_type=MessageType.COLLABORATION_REQUEST,
                content={
                    "collaboration_type": collaboration_type,
                    "data": data,
                    "from_agent": self.agent_id
                }
            )
            
            return {
                "status": "collaboration_request_sent",
                "target_agent": target_agent,
                "collaboration_type": collaboration_type
            }
        except Exception as e:
            return {
                "status": "collaboration_failed",
                "error": str(e)
            }
