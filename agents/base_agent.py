"""
Base agent class for FlutterSwarm.
All specialized agents inherit from this base class.
"""

import asyncio
import yaml
import time
import threading
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from shared.state import shared_state, AgentStatus, MessageType, AgentActivityEvent, AgentMessage
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
        
        # Initialize monitoring attributes first
        self.is_running = False
        self.current_task = None
        self._monitoring_task = None
        self._async_lock = asyncio.Lock()  # Use async lock instead of threading lock
        
        # Register with shared state
        shared_state.register_agent(
            agent_id=self.agent_id,
            capabilities=self.agent_config.get("capabilities", [])
        )
        
        # Enable real-time awareness
        self.enable_real_time_awareness()
        
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
        except Exception as e:
            self.logger.error(f"Failed to initialize LLM: {e}")
            # Return a mock LLM or raise a more descriptive error
            raise ValueError(f"LLM initialization failed: {e}. Please check your API key configuration.")
    
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

    # Real-time awareness methods
    def enable_real_time_awareness(self) -> None:
        """Enable real-time awareness for this agent."""
        # Subscribe to all other agents
        shared_state.subscribe_agent_to_all(self.agent_id)
        
        # Start continuous monitoring (if not already running)
        if not hasattr(self, '_monitoring_enabled'):
            self._monitoring_enabled = True
            self.start_continuous_monitoring()
    
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
            loop = asyncio.get_event_loop()
            self._monitoring_task = loop.create_task(self._continuous_monitoring_loop())
            self.logger.debug(f"🔄 Started continuous monitoring for {self.agent_id}")

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
        
        # Common predictive actions
        if action == "monitor_collaborator_activities":
            collaborator = insight.get("collaborator", "")
            if collaborator:
                # Subscribe to specific collaborator if not already subscribed
                self._add_targeted_subscription(collaborator)
        
        elif action == "prepare_architecture_analysis":
            # Broadcast readiness for architecture work
            await self.broadcast_activity(
                activity_type="predictive_preparation",
                activity_details={
                    "preparation_type": "architecture_analysis",
                    "trigger": "predictive_insight",
                    "insight_confidence": insight.get("confidence", 0.0)
                },
                impact_level="low",
                collaboration_relevance=["architecture", "planning"]
            )
        
        elif action == "prepare_implementation_structure":
            # Broadcast readiness for implementation work
            await self.broadcast_activity(
                activity_type="predictive_preparation", 
                activity_details={
                    "preparation_type": "implementation_structure",
                    "trigger": "predictive_insight",
                    "insight_confidence": insight.get("confidence", 0.0)
                },
                impact_level="low",
                collaboration_relevance=["implementation", "architecture"]
            )
        
        elif action == "prepare_test_infrastructure":
            # Broadcast readiness for testing work
            await self.broadcast_activity(
                activity_type="predictive_preparation",
                activity_details={
                    "preparation_type": "test_infrastructure",
                    "trigger": "predictive_insight", 
                    "insight_confidence": insight.get("confidence", 0.0)
                },
                impact_level="low",
                collaboration_relevance=["testing", "qa"]
            )
    
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
