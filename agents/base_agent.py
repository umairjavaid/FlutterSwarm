"""
Base agent class for FlutterSwarm.
All specialized agents inherit from this base class.
"""

import asyncio
import yaml
import time
import threading
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Callable, Awaitable
from datetime import datetime
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from shared.state import shared_state, AgentStatus, MessageType, AgentActivityEvent, AgentMessage
from config.config_manager import get_config
from tools import ToolManager, ToolResult, ToolStatus
from utils.path_utils import safe_join, ensure_absolute_path, get_absolute_project_path
from utils.exception_handler import with_exception_handling, log_and_suppress_exception, ensure_exception_handler_set
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
        
        # Initialize tools with proper toolbox
        self.tool_manager = ToolManager()
        # Create agent-specific toolbox
        self.toolbox = AgentToolbox(self.tool_manager, self.agent_id)
        # Keep backward compatibility with old code
        self.tools = self.toolbox
        
        # Initialize monitoring attributes first
        self.is_running = False
        self.current_task = None
        self._monitoring_task = None
        self._async_lock = asyncio.Lock()  # Use async lock instead of threading lock
        
        # Ensure exception handlers are set
        ensure_exception_handler_set()
        
        # Register with shared state
        shared_state.register_agent(
            agent_id=self.agent_id,
            capabilities=self.agent_config.get("capabilities", [])
        )
        
        # Enable real-time awareness (disabled to prevent endless loops)
        # self.enable_real_time_awareness()
        
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
        try:
            # Get LLM configuration (primary by default, with agent-specific overrides)
            llm_config = self._config_manager.get_llm_config()
            agent_llm_config = self.agent_config.get('llm', {})
            
            # Merge configurations (agent-specific overrides global)
            final_config = {**llm_config, **agent_llm_config}
            
            # Get API key from environment
            api_key_env = final_config.get('api_key_env', 'ANTHROPIC_API_KEY')
            api_key = final_config.get('api_key') or os.getenv(api_key_env)
            
            if not api_key:
                # Try fallback configuration
                try:
                    fallback_config = self._config_manager.get_llm_config(fallback=True)
                    fallback_api_key_env = fallback_config.get('api_key_env', 'OPENAI_API_KEY')
                    api_key = os.getenv(fallback_api_key_env)
                    
                    if not api_key:
                        raise ValueError(f"No API key found in environment variables: {api_key_env}, {fallback_api_key_env}")
                    
                    # Check if the fallback is trying to use a different provider
                    if "openai" in fallback_api_key_env.lower():
                        raise NotImplementedError("Fallback to OpenAI is not yet implemented. Please configure an Anthropic API key.")

                except ValueError as e:
                    raise e  # Re-raise the ValueError
                except NotImplementedError as e:
                    raise e # Re-raise the NotImplementedError
                except Exception:
                    self.logger.warning(f"Primary API key not found, and fallback configuration failed. Please check your environment variables and config files.")
                    raise ValueError(f"No valid API key found.")

            # Get default model from config
            default_model = self._config_manager.get('agents.llm.primary.model', 'claude-3-5-sonnet-20241022')
            default_temperature = self._config_manager.get('agents.llm.primary.temperature', 0.7)
            default_max_tokens = self._config_manager.get('agents.llm.primary.max_tokens', 4000)
            
            self.logger.debug(f"Initializing LLM for agent {self.agent_id} with model {final_config.get('model', default_model)}")
            
            # Create ChatAnthropic instance with appropriate configuration
            return ChatAnthropic(
                model=final_config.get("model", default_model),
                temperature=final_config.get("temperature", default_temperature),
                max_tokens=final_config.get("max_tokens", default_max_tokens),
                anthropic_api_key=api_key
            )
        except Exception as e:
            import traceback
            self.logger.error(f"Failed to initialize LLM: {e}\n{traceback.format_exc()}")
            # Raise a descriptive error with troubleshooting guidance
            raise ValueError(f"LLM initialization failed for agent {self.agent_id}: {e}. Please check your API key configuration and network connection.")
    
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
            # Monitoring not available, skip silently
            self.logger.debug("Monitoring system not available")
        except Exception as e:
            self.logger.warning(f"Failed to log status change: {e}")
    
    async def _update_status(self, status: AgentStatus, task: Optional[str] = None, 
                           metadata: Optional[Dict[str, Any]] = None):
        """Update agent status and log to monitoring."""
        try:
            # Update shared state
            shared_state.update_agent_status(self.agent_id, status, task, metadata=metadata)
            
            # Log to monitoring system
            self._log_status_change(status, task)
            
            # Broadcast status change as real-time activity
            await self.broadcast_activity(
                activity_type="status_change",
                activity_details={
                    "new_status": status.value,
                    "task": task,
                    "metadata": metadata or {}
                },
                impact_level="low" if status == AgentStatus.IDLE else "medium",
                collaboration_relevance=["all"]  # All agents might be interested in status changes
            )
        except Exception as e:
            self.logger.error(f"Failed to update status: {e}")
    
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
            from monitoring.agent_logger import agent_logger
            agent_logger.log_error(
                agent_id=getattr(self, 'agent_id', 'unknown'),
                error_type=type(e).__name__,
                error_message=str(e),
                context={"file": __file__},
                exception=e
            )
    
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
            
            # Send completion message with proper task_id
            task_id = task_data.get("task_id", message.id)  # Use custom task_id if provided
            shared_state.send_message(
                from_agent=self.agent_id,
                to_agent=message.from_agent,
                message_type=MessageType.TASK_COMPLETED,
                content={
                    "task_id": task_id,
                    "result": result,
                    "success": True
                }
            )
            
            self._update_status(AgentStatus.IDLE)
            
        except Exception as e:
            task_id = task_data.get("task_id", message.id)  # Use custom task_id if provided
            shared_state.send_message(
                from_agent=self.agent_id,
                to_agent=message.from_agent,
                message_type=MessageType.ERROR_REPORT,
                content={
                    "task_id": task_id,
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
    
    async def think(self, prompt: str, context: Dict[str, Any] = None, task_complexity: str = "normal") -> str:
        """
        Use LLM to think/reason about a problem.
        
        Args:
            prompt: The prompt to send to the LLM
            context: Optional additional context for the LLM
            task_complexity: Complexity of the task ("low", "normal", "high")
                             affects model selection and parameters
        
        Returns:
            Generated response from the LLM
        """
        # Import LLM logger
        from utils.llm_logger import llm_logger
        
        # Create combined context with shared state for better reasoning
        combined_context = self._build_combined_context(context)
        
        # Select appropriate model based on task complexity
        model_config = self._select_model_config(task_complexity)
        
        # Build comprehensive system prompt with role information and context
        system_prompt = self._build_system_prompt(combined_context)
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=prompt)
        ]
        
        # Get selected model config
        model = model_config.get('model')
        provider = model_config.get('provider', 'anthropic')
        temperature = model_config.get('temperature')
        max_tokens = model_config.get('max_tokens')
        
        # Log LLM request before sending
        interaction_id = llm_logger.log_llm_request(
            agent_id=self.agent_id,
            model=model,
            provider=provider,
            request_type="think",
            prompt=prompt,
            context=combined_context,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        self.logger.debug(f"🧠 Sending {task_complexity} complexity '{prompt[:50]}...' to {model}")
        
        # Use retry mechanism for resilience
        start_time = time.time()
        response = None
        error = None
        response_content = ""
        
        try:
            # Use safe_execute_with_retry for resilient LLM calls
            async def _llm_call():
                return await self.llm.ainvoke(messages)
            
            response = await self.safe_execute_with_retry(_llm_call, max_retries=3)
            response_content = response.content
            
            # Validate response (simple check)
            if not response_content or len(response_content.strip()) < 10:
                self.logger.warning(f"⚠️ LLM returned unusually short response: '{response_content}'")
            
        except Exception as e:
            error = str(e)
            self.logger.error(f"❌ LLM request failed in {self.agent_id}: {error}")
            # Return a fallback response if possible
            response_content = self._generate_fallback_response(prompt, combined_context, error)
            
        finally:
            duration = time.time() - start_time
            
            # Extract token usage if available
            token_usage = self._extract_token_usage(response)
            
            # Log LLM response
            llm_logger.log_llm_response(
                interaction_id=interaction_id,
                agent_id=self.agent_id,
                model=model,
                provider=provider,
                request_type="think",
                prompt=prompt,
                response=response_content,
                duration=duration,
                context=combined_context,
                token_usage=token_usage,
                temperature=temperature,
                max_tokens=max_tokens,
                error=error
            )
            
            self.logger.debug(f"🧠 LLM response received in {duration:.2f}s")
        
        # Post-process response if needed (filtering, formatting, etc.)
        processed_response = self._post_process_response(response_content)
        
        return processed_response
        
    def _build_combined_context(self, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Build a combined context with shared state and user context."""
        # Start with a basic context
        combined = {
            "agent_id": self.agent_id,
            "agent_role": self.agent_config.get("role", ""),
            "agent_capabilities": self.agent_config.get("capabilities", []),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add project state if available
        try:
            project_state = shared_state.get_project_state()
            if project_state:
                combined["project_state"] = {
                    "id": project_state.get("id", ""),
                    "name": project_state.get("name", ""),
                    "current_phase": project_state.get("current_phase", ""),
                    "files_created": len(project_state.get("files_created", [])),
                }
        except Exception:
            # Skip if project state can't be accessed
            pass
            
        # Add information about other agents
        try:
            other_agents = self.get_other_agents()
            if other_agents:
                combined["other_agents"] = {
                    agent_id: {
                        "status": state.get("status", "unknown"),
                        "current_task": state.get("current_task", None)
                    } for agent_id, state in other_agents.items()
                }
        except Exception:
            # Skip if agent info can't be accessed
            pass
            
        # Add user-provided context (overrides any conflicts)
        if user_context:
            combined.update(user_context)
            
        return combined
    
    def _select_model_config(self, task_complexity: str) -> Dict[str, Any]:
        """Select appropriate model configuration based on task complexity."""
        # Get agent-specific LLM config
        llm_config = self.agent_config.get('llm', {})
        
        # Get global config defaults
        default_model = self._config_manager.get('agents.llm.primary.model', 'claude-3-5-sonnet-20240620')
        default_temperature = self._config_manager.get('agents.llm.primary.temperature', 0.7)
        default_max_tokens = self._config_manager.get('agents.llm.primary.max_tokens', 4000)
        
        # Set up defaults based on task complexity
        if task_complexity == "high":
            # Use more powerful model with more careful thinking
            return {
                "model": llm_config.get("high_complexity_model", "claude-3-5-opus-20240229"),
                "temperature": llm_config.get("high_complexity_temperature", 0.5),
                "max_tokens": llm_config.get("high_complexity_max_tokens", 8000),
                "provider": llm_config.get("provider", "anthropic")
            }
        elif task_complexity == "low":
            # Use faster model with higher creativity for simple tasks
            return {
                "model": llm_config.get("low_complexity_model", "claude-3-5-sonnet-20240620"),
                "temperature": llm_config.get("low_complexity_temperature", 0.8),
                "max_tokens": llm_config.get("low_complexity_max_tokens", 2000),
                "provider": llm_config.get("provider", "anthropic")
            }
        else:  # "normal" complexity or any other value
            # Use standard configuration
            return {
                "model": llm_config.get("model", default_model),
                "temperature": llm_config.get("temperature", default_temperature),
                "max_tokens": llm_config.get("max_tokens", default_max_tokens),
                "provider": llm_config.get("provider", "anthropic")
            }
            
    def _build_system_prompt(self, context: Dict[str, Any]) -> str:
        """Build comprehensive system prompt with role information and context."""
        # Get agent-specific information
        agent_name = self.agent_config.get('name', self.agent_id)
        agent_role = self.agent_config.get('role', 'Generic Agent')
        agent_capabilities = self.agent_config.get('capabilities', [])
        agent_description = self.agent_config.get('description', '')
        
        # Format capabilities for better readability
        capabilities_formatted = '\n'.join([f"- {cap}" for cap in agent_capabilities])
        
        # Get project context
        project_id = shared_state.get_current_project_id() or "Unknown"
        project_state = context.get("project_state", {})
        project_name = project_state.get("name", "Unknown Project")
        current_phase = project_state.get("current_phase", "planning")
        
        # Build comprehensive system prompt
        system_prompt = f"""
You are {agent_name}, an AI agent specializing in Flutter application development.

ROLE AND RESPONSIBILITIES:
{agent_role}

CAPABILITIES:
{capabilities_formatted}

AGENT DESCRIPTION:
{agent_description}

PROJECT CONTEXT:
- Project Name: {project_name}
- Project ID: {project_id}
- Current Phase: {current_phase}
- You are part of a multi-agent system collaboratively building a Flutter application
- You can access shared state and collaborate with other specialized agents

GENERAL GUIDELINES:
1. Provide clear, actionable responses focused on Flutter development
2. When generating code, ensure it follows modern Flutter best practices
3. Consider potential edge cases and error handling
4. Think step-by-step when solving complex problems
5. Your responses should be helpful for building production-ready Flutter applications
6. Consider platform compatibility (iOS, Android, web) in your solutions

COLLABORATION CONTEXT:
You are collaborating with specialized agents, each with their own expertise.
Current collaboration state:
{self._format_collaboration_context(context)}

RESPONSE REQUIREMENTS:
- Be precise and specific in your responses
- Prioritize code quality and maintainability
- Consider performance implications of your recommendations
- When uncertain, acknowledge limitations rather than providing incorrect information
- Always consider the overall architecture and project requirements
"""
        
        return system_prompt
        
    def _format_collaboration_context(self, context: Dict[str, Any]) -> str:
        """Format collaboration context for the system prompt."""
        other_agents = context.get("other_agents", {})
        
        if not other_agents:
            return "No active collaborators at the moment."
            
        # Format information about other agents
        agent_info = []
        for agent_id, state in other_agents.items():
            status = state.get("status", "unknown")
            task = state.get("current_task", "none")
            agent_info.append(f"- {agent_id}: Status: {status}, Current Task: {task}")
            
        return "\n".join(agent_info)
    
    def _extract_token_usage(self, response) -> Dict[str, int]:
        """Extract token usage information from LLM response."""
        if not response:
            return {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
            
        token_usage = {}
        
        # Extract token usage if available
        if hasattr(response, 'usage_metadata') and response.usage_metadata:
            token_usage = {
                "input_tokens": getattr(response.usage_metadata, 'input_tokens', 0),
                "output_tokens": getattr(response.usage_metadata, 'output_tokens', 0),
                "total_tokens": getattr(response.usage_metadata, 'total_tokens', 0)
            }
        
        return token_usage
    
    def _generate_fallback_response(self, prompt: str, context: Dict[str, Any], error: str) -> str:
        """Generate a fallback response when LLM call fails."""
        self.logger.warning(f"⚠️ Generating fallback response for failed LLM call: {error}")
        
        # Basic fallback response that acknowledges the error
        return f"""
I apologize, but I encountered an issue while processing your request.

Error: {error}

As {self.agent_config.get('name', self.agent_id)}, I recommend:
1. Check if the request can be handled without LLM processing
2. Try again with a more specific prompt
3. Consult with other agents in the system for assistance
4. If the error persists, there might be an issue with the LLM service

Please contact the system administrator if this problem continues.
"""
    
    def _post_process_response(self, response: str) -> str:
        """
        Post-process the LLM response.
        This could include formatting, filtering, or other transformations.
        """
        # For now, just basic filtering of repetitive or irrelevant content
        if not response:
            return ""
            
        # Remove any "I'm Claude" or similar identification phrases
        response = self._remove_identity_phrases(response)
        
        return response.strip()
        
    def _remove_identity_phrases(self, text: str) -> str:
        """Remove LLM identity phrases from the response."""
        identity_phrases = [
            "I'm Claude, an AI assistant",
            "As Claude, I",
            "I'm an AI assistant",
            "I'm Claude",
            "As an AI assistant",
        ]
        
        result = text
        for phrase in identity_phrases:
            result = result.replace(phrase, f"As {self.agent_config.get('name', self.agent_id)}, I")
            
        return result
    
    async def execute_tool(self, tool_name: str, operation: str = None, **kwargs) -> ToolResult:
        """
        Execute a tool with the given parameters.
        
        Args:
            tool_name: Name of the tool to execute
            operation: The specific operation to perform with the tool
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult with execution outcome
        """
        start_time = time.time()
        self.logger.debug(f"🔧 Executing tool: {tool_name} (operation: {operation or 'default'})")
        
        # Add operation to kwargs if provided
        if operation:
            kwargs["operation"] = operation
            
        # Validate tool exists before attempting to use it
        if not self.toolbox.has_tool(tool_name):
            error_msg = f"Tool '{tool_name}' not found in the agent's toolbox"
            self.logger.error(f"⚠️ {error_msg}")
            return ToolResult(
                status=ToolStatus.ERROR, 
                error=error_msg,
                output=None,
                data=None
            )
            
        # Add timeout handling
        timeout = kwargs.pop("timeout", 60)  # Default 60 second timeout
        try:
            # Use asyncio.wait_for to implement timeout
            result = await asyncio.wait_for(
                self.toolbox.execute(tool_name, **kwargs),
                timeout=timeout
            )
            
            # Record execution time
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
            
            if result.status != ToolStatus.SUCCESS:
                self.logger.warning(f"⚠️ Tool '{tool_name}' failed: {result.error}")
            else:
                self.logger.debug(f"✅ Tool '{tool_name}' completed successfully in {execution_time:.2f}s")
                
            return result
            
        except asyncio.TimeoutError:
            error_msg = f"Tool '{tool_name}' execution timed out after {timeout} seconds"
            self.logger.error(f"⏱️ {error_msg}")
            
            # Log timeout to monitoring
            try:
                from monitoring import build_monitor
                build_monitor.log_tool_usage(
                    self.agent_id,
                    tool_name,
                    kwargs.get('operation', 'execute'),
                    "timeout",
                    timeout,
                    kwargs,
                    None,
                    error_msg
                )
            except ImportError:
                pass
            except Exception as e:
                self.logger.warning(f"Failed to log tool timeout: {e}")
                
            return ToolResult(
                status=ToolStatus.ERROR,
                error=error_msg,
                output=None,
                data=None
            )
        except Exception as e:
            error_msg = f"Tool '{tool_name}' execution failed with error: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            
            # Log error to monitoring
            try:
                from monitoring import build_monitor
                execution_time = time.time() - start_time
                build_monitor.log_tool_usage(
                    self.agent_id,
                    tool_name,
                    kwargs.get('operation', 'execute'),
                    "error",
                    execution_time,
                    kwargs,
                    None,
                    str(e)
                )
            except ImportError:
                pass
            except Exception as log_error:
                self.logger.warning(f"Failed to log tool error: {log_error}")
                
            return ToolResult(
                status=ToolStatus.ERROR,
                error=error_msg,
                output=None,
                data=None
            )
    
    async def run_command(self, command: str, timeout: int = 30, capture_output: bool = True) -> Dict[str, Any]:
        """
        Execute a shell command using the terminal tool.
        
        Args:
            command: Command to execute
            timeout: Maximum execution time in seconds
            capture_output: Whether to capture and return command output
            
        Returns:
            Dictionary with command execution results
        """
        try:
            self.logger.debug(f"⌨️ Executing command: {command}")
            
            result = await self.execute_tool(
                "terminal",
                operation="run_command",
                command=command,
                timeout=timeout,
                capture_output=capture_output
            )
            
            return {
                "success": result.status == ToolStatus.SUCCESS,
                "output": result.data.get("output", "") if result.data else "",
                "error": result.error if result.error else "",
                "exit_code": result.data.get("exit_code", -1) if result.data else -1
            }
        except Exception as e:
            self.logger.error(f"❌ Command execution failed: {str(e)}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "exit_code": -1
            }
    
    async def read_file(self, file_path: str, **kwargs) -> ToolResult:
        """
        Read a file using the file tool.
        
        Args:
            file_path: Path to the file to read
            **kwargs: Additional parameters for the file tool
            
        Returns:
            ToolResult with file contents
        """
        try:
            # Add timeout for file operations (default: 10 seconds)
            timeout = kwargs.pop('timeout', 10)
            
            result = await self.execute_tool(
                "file", 
                operation="read", 
                file_path=file_path, 
                timeout=timeout,
                **kwargs
            )
            
            # Log success or failure
            if result.status == ToolStatus.SUCCESS:
                self.logger.debug(f"📄 Successfully read file: {file_path}")
            else:
                self.logger.warning(f"⚠️ Failed to read file: {file_path} - {result.error}")
                
            return result
            
        except Exception as e:
            error_msg = f"Error reading file {file_path}: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            return ToolResult(status=ToolStatus.ERROR, error=error_msg, output=None, data=None)
    
    async def write_file(self, file_path: str, content: str, **kwargs) -> ToolResult:
        """
        Write a file using the file tool.
        
        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            **kwargs: Additional parameters for the file tool
            
        Returns:
            ToolResult with operation result
        """
        try:
            # Add timeout for file operations (default: 15 seconds)
            timeout = kwargs.pop('timeout', 15)
            
            # Create directory if it doesn't exist
            await self._ensure_directory_exists(file_path)
            
            result = await self.execute_tool(
                "file", 
                operation="write", 
                file_path=file_path, 
                content=content,
                timeout=timeout,
                **kwargs
            )
            
            # Log success or failure
            if result.status == ToolStatus.SUCCESS:
                self.logger.debug(f"💾 Successfully wrote file: {file_path}")
            else:
                self.logger.warning(f"⚠️ Failed to write file: {file_path} - {result.error}")
                
            return result
            
        except Exception as e:
            error_msg = f"Error writing file {file_path}: {str(e)}"
            self.logger.error(f"❌ {error_msg}")
            return ToolResult(status=ToolStatus.ERROR, error=error_msg, output=None, data=None)
            
    async def _ensure_directory_exists(self, file_path: str) -> None:
        """Ensure the directory for a file exists."""
        # Use path utilities for safe directory handling
        file_path = ensure_absolute_path(file_path)
        directory = os.path.dirname(file_path)
        
        if directory:
            try:
                # Use file tool to create directory if it doesn't exist
                await self.execute_tool(
                    "file",
                    operation="create_directory",
                    directory_path=directory
                )
            except Exception as e:
                log_and_suppress_exception(f"create_directory_{directory}", e)
                # Continue anyway, the write operation will fail if necessary
    
    async def safe_execute_with_retry(self, operation_func, max_retries=3):
        """Execute operation with exponential backoff retry."""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return await operation_func()
            except Exception as e:
                last_exception = e
                
                if attempt == max_retries - 1:
                    # Last attempt failed, re-raise the exception
                    self.logger.error(f"❌ All {max_retries} retry attempts failed: {str(e)}")
                    from monitoring.agent_logger import agent_logger
                    agent_logger.log_error(
                        agent_id=getattr(self, 'agent_id', 'unknown'),
                        error_type=type(e).__name__,
                        error_message=str(e),
                        context={"file": __file__},
                        exception=e
                    )
                    raise
                    
                # Calculate wait time with exponential backoff and small jitter
                wait_time = (2 ** attempt) + (random.random() * 0.5)
                self.logger.warning(f"Retry {attempt + 1}/{max_retries} after error: {str(e)}. Waiting {wait_time:.2f}s")
                
                # Wait before retrying
                await asyncio.sleep(wait_time)
        
        # This should never be reached due to the raise above, but adding as a safeguard
        raise last_exception
    
    async def execute_with_retry(self, operation, max_retries=3):
        """Execute operation with retry logic and exponential backoff."""
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                result = await operation()
                if attempt > 0:
                    self.logger.info(f"✅ Operation succeeded on attempt {attempt + 1}/{max_retries}")
                return result
            except Exception as e:
                last_exception = e
                
                if attempt == max_retries - 1:
                    # Last attempt failed, re-raise the exception
                    self.logger.error(f"❌ All {max_retries} retry attempts failed: {str(e)}")
                    try:
                        from monitoring.agent_logger import agent_logger
                        agent_logger.log_error(
                            agent_id=getattr(self, 'agent_id', 'unknown'),
                            error_type=type(e).__name__,
                            error_message=str(e),
                            context={"file": __file__, "operation": "execute_with_retry"},
                            exception=e
                        )
                    except ImportError:
                        # If agent_logger is not available, continue without logging
                        pass
                    raise
                    
                # Calculate wait time with exponential backoff and small jitter
                wait_time = (2 ** attempt) + (random.random() * 0.5)
                self.logger.warning(f"⚠️ Retry {attempt + 1}/{max_retries} after error: {str(e)}. Waiting {wait_time:.2f}s")
                
                # Wait before retrying
                await asyncio.sleep(wait_time)
        
        # This should never be reached due to the raise above, but adding as a safeguard
        raise last_exception

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

    # The run_command method is now implemented above

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

    # Real-time awareness methods
    def enable_real_time_awareness(self) -> None:
        """Enable real-time awareness for this agent."""
        # Subscribe to all other agents
        shared_state.subscribe_agent_to_all(self.agent_id)
        
        # DISABLED: Start continuous monitoring to prevent endless loops
        # if not hasattr(self, '_monitoring_enabled'):
        #     self._monitoring_enabled = True
        #     self.start_continuous_monitoring()
        
        self.logger.info(f"Real-time awareness enabled for {self.agent_id} (monitoring disabled to prevent loops)")
    
    async def broadcast_activity(self, activity_type: str, activity_details: Dict[str, Any], 
                          impact_level: str = "medium", 
                          collaboration_relevance: List[str] = None) -> None:
        """Broadcast an activity event to other agents."""
        try:
            if collaboration_relevance is None:
                collaboration_relevance = []
            
            event = AgentActivityEvent(
                agent_id=self.agent_id,
                activity_type=activity_type,
                activity_details=activity_details,
                timestamp=datetime.now(),
                project_id=shared_state.get_current_project_id(),
                impact_level=impact_level,
                collaboration_relevance=collaboration_relevance
            )
            
            shared_state.broadcast_agent_activity(event)
        except Exception as e:
            self.logger.error(f"Failed to broadcast activity: {e}")
    
    def handle_real_time_update(self, message: AgentMessage) -> None:
        """Handle real-time status updates from other agents."""
        if message.message_type == MessageType.REAL_TIME_STATUS_BROADCAST:
            event_data = message.content.get("event", {})
            consciousness_update = message.content.get("consciousness_update", {})
            
            # Process the real-time update
            self._process_peer_activity(event_data, consciousness_update)
        
        elif message.message_type == MessageType.PROACTIVE_ASSISTANCE_OFFER:
            # Handle proactive collaboration opportunity
            self._handle_proactive_opportunity(message.content)
    
    def _process_peer_activity(self, event_data: Dict[str, Any], consciousness_update: Dict[str, Any]) -> None:
        """Process activity from peer agents and react accordingly."""
        peer_agent = event_data.get("agent_id", "unknown")
        activity_type = event_data.get("activity_type", "")
        activity_details = event_data.get("activity_details", {})
        impact_level = event_data.get("impact_level", "low")
        
        # Log the awareness
        self.logger.debug(f"🔗 Real-time awareness: {peer_agent} -> {activity_type} ({impact_level})")
        
        # React based on agent type and activity
        self._react_to_peer_activity(peer_agent, activity_type, activity_details, consciousness_update)
    
    def _react_to_peer_activity(self, peer_agent: str, activity_type: str, 
                               activity_details: Dict[str, Any], consciousness_update: Dict[str, Any]) -> None:
        """React to specific peer activities (to be overridden by subclasses)."""
        # Base implementation - subclasses should override for specific behaviors
        pass
    
    def _handle_proactive_opportunity(self, opportunity: Dict[str, Any]) -> None:
        """Handle a proactive collaboration opportunity."""
        opportunity_type = opportunity.get("type", "")
        details = opportunity.get("details", {})
        
        self.logger.info(f"🤝 Proactive opportunity: {opportunity_type}")
        
        # Check if this agent wants to accept the opportunity
        should_accept = self._should_accept_opportunity(opportunity_type, details)
        
        if should_accept:
            opportunity_id = opportunity.get("id", "")
            shared_state.accept_collaboration_opportunity(self.agent_id, opportunity_id)
            
            # Execute the suggested action
            suggested_action = details.get("suggested_action", "")
            if suggested_action:
                self._execute_proactive_action(suggested_action, details)
    
    def _should_accept_opportunity(self, opportunity_type: str, details: Dict[str, Any]) -> bool:
        """Determine if this agent should accept a proactive collaboration opportunity."""
        # Default: accept medium and high priority opportunities
        priority = details.get("priority", "low")
        return priority in ["medium", "high"]
    
    def _execute_proactive_action(self, action: str, details: Dict[str, Any]) -> None:
        """Execute a proactive action (to be overridden by subclasses)."""
        self.logger.info(f"🎯 Executing proactive action: {action}")
        # Base implementation - subclasses should override for specific actions

    # Continuous monitoring methods
    def start_continuous_monitoring(self) -> None:
        """Start continuous monitoring loop."""
        import asyncio
        
        if self._monitoring_task is None or self._monitoring_task.done():
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # No running event loop, create one if needed
                try:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                except Exception:
                    self.logger.warning(f"Could not create event loop for {self.agent_id} monitoring")
                    return
            
            try:
                self._monitoring_task = loop.create_task(self._continuous_monitoring_loop())
                self.logger.debug(f"🔄 Started continuous monitoring for {self.agent_id}")
            except Exception as e:
                self.logger.error(f"Failed to start monitoring task for {self.agent_id}: {e}")

    async def _continuous_monitoring_loop(self) -> None:
        """Main continuous monitoring loop."""
        import asyncio
        
        # Get monitoring interval from config (default: 5 seconds)
        monitoring_interval = self._config_manager.get('application.monitoring.intervals.status_update', 5)
        
        try:
            while self._monitoring_enabled:
                try:
                    # Check for new messages
                    await self._check_for_messages()
                    
                    # Monitor system state
                    await self._monitor_system_state()
                    
                    # Check for collaboration opportunities
                    await self._check_collaboration_opportunities()
                    
                    # Update consciousness
                    await self._update_consciousness()
                    
                    # Sleep for monitoring interval
                    await asyncio.sleep(monitoring_interval)
                    
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    self.logger.error(f"❌ Error in continuous monitoring: {e}")
                    await asyncio.sleep(monitoring_interval)
                    
        except asyncio.CancelledError:
            self.logger.debug(f"🛑 Continuous monitoring stopped for {self.agent_id}")

    async def _check_for_messages(self) -> None:
        """Check for new real-time messages and process them."""
        try:
            # Get messages for this agent
            messages = shared_state.get_messages_for_agent(self.agent_id)
            
            for message in messages:
                if message.message_type in [
                    MessageType.REAL_TIME_STATUS_BROADCAST,
                    MessageType.PROACTIVE_ASSISTANCE_OFFER,
                    MessageType.CONSCIOUSNESS_UPDATE
                ]:
                    self.handle_real_time_update(message)
                    
        except Exception as e:
            self.logger.debug(f"Error checking messages: {e}")

    async def _monitor_system_state(self) -> None:
        """Monitor overall system state and react to changes."""
        try:
            # Get current project state
            current_project_id = shared_state.get_current_project_id()
            if current_project_id:
                project_state = shared_state.get_project_state(current_project_id)
                if project_state:
                    # Check for significant changes
                    await self._react_to_project_changes(project_state)
                    
            # Monitor peer agent activities
            peer_activities = self._get_relevant_peer_activities()
            if peer_activities:
                await self._analyze_peer_activities(peer_activities)
                
        except Exception as e:
            self.logger.debug(f"Error monitoring system state: {e}")

    async def _check_collaboration_opportunities(self) -> None:
        """Check for new collaboration opportunities."""
        try:
            opportunities = shared_state.get_collaboration_opportunities(self.agent_id)
            
            for opportunity in opportunities:
                if not self._has_seen_opportunity(opportunity):
                    await self._evaluate_collaboration_opportunity(opportunity)
                    
        except Exception as e:
            self.logger.debug(f"Error checking collaboration opportunities: {e}")

    async def _update_consciousness(self) -> None:
        """Update shared consciousness with current insights."""
        try:
            # Generate insights about current state
            insights = await self._generate_current_insights()
            
            if insights:
                for key, value in insights.items():
                    shared_state.update_shared_consciousness(f"{self.agent_id}_{key}", value)
            
            # Generate predictive insights
            predictive_insights = shared_state.generate_predictive_insights(self.agent_id)
            
            # Act on high-confidence insights
            await self._act_on_predictive_insights(predictive_insights)
                    
        except Exception as e:
            self.logger.debug(f"Error updating consciousness: {e}")

    def _get_relevant_peer_activities(self) -> List[Dict[str, Any]]:
        """Get activities from peer agents that are relevant to this agent."""
        relevant_activities = []
        
        try:
            # Get activity streams from subscribed agents
            subscriptions = shared_state._awareness_state.agent_subscriptions.get(self.agent_id, [])
            
            for peer_agent_id in subscriptions:
                recent_activities = shared_state.get_agent_activity_stream(peer_agent_id, limit=5)
                
                # Filter for relevant activities
                for activity in recent_activities:
                    if self._is_activity_relevant(activity):
                        relevant_activities.append(activity)
                        
        except Exception as e:
            self.logger.debug(f"Error getting peer activities: {e}")
            
        return relevant_activities

    def _is_activity_relevant(self, activity: Dict[str, Any]) -> bool:
        """Check if an activity is relevant to this agent."""
        # Check if this agent type is in collaboration relevance
        collaboration_relevance = activity.get("collaboration_relevance", [])
        agent_capabilities = self.agent_config.get("capabilities", [])
        
        if "all" in collaboration_relevance:
            return True
            
        # Check if any of our capabilities match the relevance
        return any(capability in collaboration_relevance for capability in agent_capabilities)

    async def _react_to_project_changes(self, project_state) -> None:
        """React to changes in project state (to be overridden by subclasses)."""
        # Base implementation - subclasses should override for specific reactions
        pass

    async def _analyze_peer_activities(self, activities: List[Dict[str, Any]]) -> None:
        """Analyze peer activities and potentially react (to be overridden by subclasses)."""
        # Base implementation - subclasses should override for specific analysis
        pass

    async def _evaluate_collaboration_opportunity(self, opportunity: Dict[str, Any]) -> None:
        """Evaluate a collaboration opportunity (to be overridden by subclasses)."""
        # Base implementation uses the existing opportunity handler
        self._handle_proactive_opportunity(opportunity)

    async def _generate_current_insights(self) -> Dict[str, Any]:
        """Generate insights about current state (to be overridden by subclasses)."""
        # Base implementation - subclasses should override for specific insights
        return {
            "last_activity": datetime.now().isoformat(),
            "status": self._last_status.value if hasattr(self, '_last_status') else "unknown"
        }

    def _has_seen_opportunity(self, opportunity: Dict[str, Any]) -> bool:
        """Check if this agent has already seen/processed this opportunity."""
        # Simple implementation - could be enhanced with persistent storage
        if not hasattr(self, '_seen_opportunities'):
            self._seen_opportunities = set()
            
        opportunity_id = opportunity.get("id", str(hash(str(opportunity))))
        
        if opportunity_id in self._seen_opportunities:
            return True
            
        self._seen_opportunities.add(opportunity_id)
        return False

    async def _act_on_predictive_insights(self, insights: List[Dict[str, Any]]) -> None:
        """Act on high-confidence predictive insights."""
        try:
            for insight in insights:
                confidence = insight.get("confidence", 0.0)
                priority = insight.get("priority", "low")
                suggested_action = insight.get("suggested_action", "")
                
                # Act on high-confidence, high-priority insights
                if confidence >= 0.7 and priority in ["high", "medium"] and suggested_action:
                    self.logger.info(f"🔮 Acting on predictive insight: {insight.get('description', '')}")
                    
                    # Execute the suggested action
                    await self._execute_predictive_action(suggested_action, insight)
                    
                    # Update real-time metrics
                    shared_state.update_real_time_metrics(
                        f"{self.agent_id}_predictive_actions",
                        shared_state.get_real_time_metrics().get(f"{self.agent_id}_predictive_actions", {}).get("value", 0) + 1
                    )
                    
        except Exception as e:
            self.logger.debug(f"Error acting on predictive insights: {e}")
    
    async def _execute_predictive_action(self, action: str, insight: Dict[str, Any]) -> None:
        """Execute a predictive action (to be overridden by subclasses)."""
        # Base implementation - log the action
        self.logger.debug(f"🎯 Predictive action: {action} based on {insight.get('type', 'unknown')} insight")

        # Only perform non-broadcasting predictive actions
        if action == "monitor_collaborator_activities":
            collaborator = insight.get("collaborator", "")
            if collaborator:
                # Subscribe to specific collaborator if not already subscribed
                self._add_targeted_subscription(collaborator)
        # All speculative predictive_preparation broadcasts are removed to prevent loops
        # Actual work broadcasts are handled elsewhere when real work is performed
    
    def _add_targeted_subscription(self, target_agent: str) -> None:
        """Add targeted subscription to a specific agent."""
        try:
            # Check if already subscribed
            current_subscriptions = shared_state._awareness_state.agent_subscriptions.get(self.agent_id, [])
            if target_agent not in current_subscriptions:
                current_subscriptions.append(target_agent)
                shared_state._awareness_state.agent_subscriptions[self.agent_id] = current_subscriptions
                self.logger.debug(f"🔗 Added targeted subscription: {self.agent_id} -> {target_agent}")
        except Exception as e:
            self.logger.debug(f"Error adding targeted subscription: {e}")

    def stop_continuous_monitoring(self) -> None:
        """Stop continuous monitoring loop."""
        self._monitoring_enabled = False
        if self._monitoring_task and not self._monitoring_task.done():
            self._monitoring_task.cancel()
            self.logger.debug(f"🛑 Stopped continuous monitoring for {self.agent_id}")
    
    async def cleanup(self) -> None:
        """Properly cleanup agent resources including async tasks."""
        try:
            # Stop monitoring
            self._monitoring_enabled = False
            
            # Cancel and await monitoring task
            if self._monitoring_task and not self._monitoring_task.done():
                self._monitoring_task.cancel()
                try:
                    await self._monitoring_task
                except asyncio.CancelledError:
                    pass  # Expected when cancelling
                except Exception as e:
                    self.logger.warning(f"Error cleaning up monitoring task: {e}")
            
            # Update status to indicate cleanup
            await self._update_status(AgentStatus.IDLE, None)
            
            self.logger.info(f"🧹 Agent {self.agent_id} cleaned up successfully")
            
        except Exception as e:
            self.logger.error(f"Error during agent cleanup: {e}")

class AgentToolbox:
    """Extension of the tool management for agents."""
    
    def __init__(self, tool_manager, agent_id):
        self.tool_manager = tool_manager
        self.agent_id = agent_id
        
    async def execute(self, tool_name, **kwargs):
        """Execute a tool with the given parameters."""
        return await self.tool_manager.execute_tool(tool_name, **kwargs)
        
    def list_available_tools(self):
        """List tools available to this agent."""
        # First try agent-specific method if available
        if hasattr(self.tool_manager, 'get_tools_for_agent'):
            return self.tool_manager.get_tools_for_agent(self.agent_id)
        # Fallback to general list
        return self.tool_manager.list_tools()
        
    def has_tool(self, tool_name):
        """Check if a specific tool is available to this agent."""
        available_tools = self.list_available_tools()
        return tool_name in available_tools
