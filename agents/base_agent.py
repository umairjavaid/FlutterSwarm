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
import os
from dotenv import load_dotenv

load_dotenv()

class BaseAgent(ABC):
    """
    Base class for all FlutterSwarm agents.
    Provides common functionality and enforces the agent interface.
    """
    
    def __init__(self, agent_id: str, config_path: str = "config/agent_config.yaml"):
        self.agent_id = agent_id
        self.config = self._load_config(config_path)
        self.agent_config = self.config["agents"][agent_id]
        
        # Defer LLM initialization until needed
        self.llm = None
        
        # Register with shared state
        shared_state.register_agent(
            agent_id=self.agent_id,
            capabilities=self.agent_config["capabilities"]
        )
        
        self.is_running = False
        self.current_task = None
        
        print(f"🤖 {self.agent_config['name']} initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load agent configuration from YAML file."""
        try:
            with open(config_path, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    async def start(self) -> None:
        """Start the agent's main loop."""
        self.is_running = True
        shared_state.update_agent_status(self.agent_id, AgentStatus.IDLE)
        
        print(f"🚀 {self.agent_config['name']} started")
        
        while self.is_running:
            try:
                # Check for new messages
                messages = shared_state.get_messages(self.agent_id)
                for message in messages:
                    await self._handle_message(message)
                
                # Perform periodic tasks
                await self._periodic_task()
                
                # Small delay to prevent CPU spinning
                await asyncio.sleep(1)
                
            except Exception as e:
                print(f"❌ Error in {self.agent_id}: {str(e)}")
                shared_state.update_agent_status(
                    self.agent_id, 
                    AgentStatus.ERROR,
                    metadata={"error": str(e)}
                )
                await asyncio.sleep(5)  # Wait before retrying
    
    async def stop(self) -> None:
        """Stop the agent."""
        self.is_running = False
        shared_state.update_agent_status(self.agent_id, AgentStatus.IDLE)
        print(f"🛑 {self.agent_config['name']} stopped")
    
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
            print(f"❌ Error handling message in {self.agent_id}: {str(e)}")
    
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
