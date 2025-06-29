"""
LLM Logger - Centralized logging for all LLM interactions in FlutterSwarm.
Tracks requests, responses, token usage, and performance metrics.
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass, asdict
from threading import Lock
import asyncio
import uuid

@dataclass
class LLMInteraction:
    """Represents a single LLM interaction."""
    interaction_id: str
    agent_id: str
    timestamp: str
    model: str
    provider: str
    request_type: str  # "think", "execute_task", "collaborate", etc.
    prompt: str
    context: Dict[str, Any]
    response: str
    token_usage: Optional[Dict[str, Any]] = None
    duration_seconds: float = 0.0
    success: bool = True
    error: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4000

class LLMLogger:
    """
    Centralized logger for all LLM interactions.
    Provides detailed tracking of AI requests and responses.
    """
    
    def __init__(self, log_dir: str = "logs", enable_file_logging: bool = True):
        self.log_dir = Path(log_dir)
        self.enable_file_logging = enable_file_logging
        self.interactions: List[LLMInteraction] = []
        self._lock = Lock()
        self._async_lock = asyncio.Lock()  # Add async lock
        
        # Create log directory
        if self.enable_file_logging:
            self.log_dir.mkdir(exist_ok=True)
        
        # Session tracking - MUST be set before _setup_logging()
        self.session_start = datetime.now()
        self.session_id = self.session_start.strftime("%Y%m%d_%H%M%S")
        
        # Setup logging (depends on session_id)
        self.logger = logging.getLogger('FlutterSwarm.LLM')
        self._setup_logging()
        
        # Metrics
        self.total_requests = 0
        self.total_tokens = 0
        self.total_duration = 0.0
        self.error_count = 0
        
        self.logger.info(f"🤖 LLM Logger initialized - Session: {self.session_id}")
    
    def _setup_logging(self):
        """Setup LLM-specific logging."""
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # File handler for LLM interactions
            if self.enable_file_logging:
                llm_log_file = self.log_dir / f"llm_interactions_{self.session_id}.log"
                file_handler = logging.FileHandler(llm_log_file)
                file_handler.setLevel(logging.DEBUG)
                
                # Detailed formatter for LLM logs
                formatter = logging.Formatter(
                    '%(asctime)s | LLM | %(levelname)-8s | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(formatter)
                console_handler.setFormatter(formatter)
                
                self.logger.addHandler(file_handler)
            
            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.DEBUG)
    
    def log_llm_request(self, agent_id: str, model: str, provider: str, request_type: str,
                       prompt: str, context: Dict[str, Any] = None, 
                       temperature: float = 0.7, max_tokens: int = 4000) -> str:
        """
        Log the start of an LLM request.
        
        Returns:
            interaction_id for tracking the response
        """
        interaction_id = f"{agent_id}_{int(time.time() * 1000)}"
        
        with self._lock:
            self.total_requests += 1
        
        # Log full prompt details
        self.logger.info(f"🚀 LLM Request [{interaction_id}]")
        self.logger.info(f"   Agent: {agent_id}")
        self.logger.info(f"   Model: {model} ({provider})")
        self.logger.info(f"   Type: {request_type}")
        self.logger.info(f"   Temperature: {temperature}, Max Tokens: {max_tokens}")
        
        # Log FULL prompt for visibility
        self.logger.info(f"   FULL PROMPT:")
        self.logger.info(f"   {'-'*60}")
        self.logger.info(f"{prompt}")
        self.logger.info(f"   {'-'*60}")
        
        if context:
            self.logger.info(f"   Context: {json.dumps(context, default=str, indent=2)}")
        
        return interaction_id
    
    def log_llm_response(self, interaction_id: str, agent_id: str, model: str, provider: str,
                        request_type: str, prompt: str, response: str, 
                        duration: float, context: Dict[str, Any] = None,
                        token_usage: Dict[str, Any] = None, temperature: float = 0.7,
                        max_tokens: int = 4000, error: str = None) -> None:
        """Log the completion of an LLM request with FULL response details."""
        
        success = error is None
        
        # Create interaction record
        interaction = LLMInteraction(
            interaction_id=interaction_id,
            agent_id=agent_id,
            timestamp=datetime.now().isoformat(),
            model=model,
            provider=provider,
            request_type=request_type,
            prompt=prompt,
            context=context or {},
            response=response or "",
            token_usage=token_usage,
            duration_seconds=duration,
            success=success,
            error=error,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        with self._lock:
            self.interactions.append(interaction)
            self.total_duration += duration
            if token_usage:
                self.total_tokens += token_usage.get('total_tokens', 0)
            if error:
                self.error_count += 1
        
        # Log response with COMPLETE details
        if success:
            self.logger.info(f"✅ LLM Response [{interaction_id}] - {duration:.2f}s")
            
            # Log COMPLETE RESPONSE for debugging
            self.logger.info(f"   === COMPLETE LLM RESPONSE ===")
            self.logger.info(f"   Agent: {agent_id}")
            self.logger.info(f"   Model: {model} ({provider})")
            self.logger.info(f"   Request Type: {request_type}")
            self.logger.info(f"   Duration: {duration:.4f}s")
            self.logger.info(f"   Temperature: {temperature}")
            self.logger.info(f"   Max Tokens: {max_tokens}")
            
            if token_usage:
                self.logger.info(f"   Token Usage: {json.dumps(token_usage, indent=2)}")
            
            if context:
                self.logger.info(f"   Context: {json.dumps(context, default=str, indent=2)}")
            
            self.logger.info(f"   FULL PROMPT:")
            self.logger.info(f"   {'-'*80}")
            self.logger.info(f"{prompt}")
            self.logger.info(f"   {'-'*80}")
            
            self.logger.info(f"   FULL RESPONSE:")
            self.logger.info(f"   {'-'*80}")
            self.logger.info(f"{response}")
            self.logger.info(f"   {'-'*80}")
            self.logger.info(f"   === END LLM RESPONSE ===")
            
        else:
            self.logger.error(f"❌ LLM Error [{interaction_id}] - {duration:.2f}s")
            self.logger.error(f"   === LLM ERROR DETAILS ===")
            self.logger.error(f"   Agent: {agent_id}")
            self.logger.error(f"   Model: {model} ({provider})")
            self.logger.error(f"   Request Type: {request_type}")
            self.logger.error(f"   Duration: {duration:.4f}s")
            self.logger.error(f"   Error: {error}")
            
            if context:
                self.logger.error(f"   Context: {json.dumps(context, default=str, indent=2)}")
            
            self.logger.error(f"   FAILED PROMPT:")
            self.logger.error(f"   {'-'*80}")
            self.logger.error(f"{prompt}")
            self.logger.error(f"   {'-'*80}")
            
            # Still log partial response if available
            if response:
                self.logger.error(f"   PARTIAL RESPONSE:")
                self.logger.error(f"   {'-'*80}")
                self.logger.error(f"{response}")
                self.logger.error(f"   {'-'*80}")
            
            self.logger.error(f"   === END LLM ERROR ===")
        
        # Log to monitoring system if available
        try:
            from monitoring import build_monitor
            build_monitor.log_tool_usage(
                agent_id, "llm", request_type, 
                "success" if success else "error",
                duration, 
                {
                    "prompt_length": len(prompt), 
                    "model": model,
                    "provider": provider,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "context": context
                },
                {
                    "response_length": len(response) if response else 0, 
                    "tokens": token_usage,
                    "response": response[:500] + "..." if response and len(response) > 500 else response
                },
                error
            )
        except ImportError:
            pass
        except Exception as e:
            self.logger.debug(f"Failed to log to monitoring: {e}")
        
        # Also log to function logger if available
        try:
            from utils.function_logger import function_logger, ToolUsage
            function_logger.log_tool_usage(ToolUsage(
                usage_id=interaction_id,
                timestamp=datetime.now().isoformat(),
                agent_id=agent_id,
                tool_name="llm",
                operation=request_type,
                input_params={
                    "prompt": prompt,
                    "model": model,
                    "provider": provider,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "context": context
                },
                output_result=response,
                status="success" if success else "error",
                duration_seconds=duration,
                error=error,
                metadata={"token_usage": token_usage}
            ))
        except ImportError:
            pass
        except Exception as e:
            self.logger.debug(f"Failed to log to function logger: {e}")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get a summary of the current LLM session."""
        with self._lock:
            agent_usage = {}
            model_usage = {}
            request_type_usage = {}
            
            for interaction in self.interactions:
                # Agent usage
                agent_usage[interaction.agent_id] = agent_usage.get(interaction.agent_id, 0) + 1
                
                # Model usage
                model_usage[interaction.model] = model_usage.get(interaction.model, 0) + 1
                
                # Request type usage
                request_type_usage[interaction.request_type] = request_type_usage.get(interaction.request_type, 0) + 1
            
            return {
                "session_id": self.session_id,
                "session_duration": str(datetime.now() - self.session_start),
                "total_requests": self.total_requests,
                "total_interactions": len(self.interactions),
                "total_tokens": self.total_tokens,
                "total_duration": self.total_duration,
                "error_count": self.error_count,
                "success_rate": (self.total_requests - self.error_count) / max(self.total_requests, 1),
                "average_duration": self.total_duration / max(len(self.interactions), 1),
                "agent_usage": agent_usage,
                "model_usage": model_usage,
                "request_type_usage": request_type_usage
            }
    
    def get_interactions_for_agent(self, agent_id: str, limit: int = 50) -> List[LLMInteraction]:
        """Get recent interactions for a specific agent."""
        with self._lock:
            agent_interactions = [i for i in self.interactions if i.agent_id == agent_id]
            return agent_interactions[-limit:]
    
    def get_recent_interactions(self, limit: int = 50) -> List[LLMInteraction]:
        """Get recent interactions across all agents."""
        with self._lock:
            return self.interactions[-limit:]
    
    def export_interactions_to_json(self, filename: Optional[str] = None) -> str:
        """Export all LLM interactions to JSON file."""
        if not filename:
            filename = f"llm_interactions_{self.session_id}.json"
        
        filepath = self.log_dir / filename
        
        # Convert interactions to dictionaries
        interactions_data = {
            "session_info": {
                "session_id": self.session_id,
                "session_start": self.session_start.isoformat(),
                "export_time": datetime.now().isoformat()
            },
            "summary": self.get_session_summary(),
            "interactions": [asdict(interaction) for interaction in self.interactions]
        }
        
        with open(filepath, 'w') as f:
            json.dump(interactions_data, f, indent=2, default=str)
        
        self.logger.info(f"📄 LLM interactions exported to {filepath}")
        return str(filepath)
    
    def get_token_usage_by_agent(self) -> Dict[str, Dict[str, Any]]:
        """Get token usage statistics by agent."""
        with self._lock:
            agent_tokens = {}
            
            for interaction in self.interactions:
                if interaction.agent_id not in agent_tokens:
                    agent_tokens[interaction.agent_id] = {
                        "total_tokens": 0,
                        "total_requests": 0,
                        "total_duration": 0.0,
                        "models_used": set()
                    }
                
                if interaction.token_usage:
                    agent_tokens[interaction.agent_id]["total_tokens"] += interaction.token_usage.get("total_tokens", 0)
                
                agent_tokens[interaction.agent_id]["total_requests"] += 1
                agent_tokens[interaction.agent_id]["total_duration"] += interaction.duration_seconds
                agent_tokens[interaction.agent_id]["models_used"].add(interaction.model)
            
            # Convert sets to lists for JSON serialization
            for agent_data in agent_tokens.values():
                agent_data["models_used"] = list(agent_data["models_used"])
            
            return agent_tokens
    
    def get_error_analysis(self) -> Dict[str, Any]:
        """Get analysis of LLM errors."""
        with self._lock:
            error_interactions = [i for i in self.interactions if not i.success]
            
            error_by_agent = {}
            error_by_model = {}
            error_types = {}
            
            for interaction in error_interactions:
                # Errors by agent
                error_by_agent[interaction.agent_id] = error_by_agent.get(interaction.agent_id, 0) + 1
                
                # Errors by model
                error_by_model[interaction.model] = error_by_model.get(interaction.model, 0) + 1
                
                # Error types
                error_type = "unknown"
                if interaction.error:
                    if "timeout" in interaction.error.lower():
                        error_type = "timeout"
                    elif "rate limit" in interaction.error.lower():
                        error_type = "rate_limit"
                    elif "api key" in interaction.error.lower():
                        error_type = "authentication"
                    elif "token" in interaction.error.lower():
                        error_type = "token_limit"
                    else:
                        error_type = "other"
                
                error_types[error_type] = error_types.get(error_type, 0) + 1
            
            return {
                "total_errors": len(error_interactions),
                "error_rate": len(error_interactions) / max(len(self.interactions), 1),
                "errors_by_agent": error_by_agent,
                "errors_by_model": error_by_model,
                "error_types": error_types,
                "recent_errors": [
                    {
                        "timestamp": i.timestamp,
                        "agent": i.agent_id,
                        "model": i.model,
                        "error": i.error
                    }
                    for i in error_interactions[-10:]  # Last 10 errors
                ]
            }
    
    async def log_llm_request_async(self, agent_id: str, model: str, provider: str, 
                                  request_type: str, prompt: str, context: Optional[Dict[str, Any]] = None,
                                  temperature: Optional[float] = None, max_tokens: Optional[int] = None) -> str:
        """Async version of log_llm_request."""
        request_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        async with self._async_lock:
            log_entry = {
                "id": request_id,
                "agent_id": agent_id,
                "type": "request",
                "model": model,
                "provider": provider,
                "request_type": request_type,
                "prompt": prompt,
                "context": context,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "timestamp": timestamp
            }
            self.interactions.append(log_entry)
        
        return request_id
    
    async def log_llm_response_async(self, interaction_id: str, agent_id: str, model: str, 
                                   provider: str, request_type: str, prompt: str, response: str,
                                   duration: float, context: Optional[Dict[str, Any]] = None,
                                   token_usage: Optional[Dict[str, int]] = None,
                                   temperature: Optional[float] = None, max_tokens: Optional[int] = None,
                                   error: Optional[str] = None) -> None:
        """Async version of log_llm_response."""
        timestamp = datetime.now().isoformat()
        
        async with self._async_lock:
            log_entry = {
                "id": str(uuid.uuid4()),
                "interaction_id": interaction_id,
                "agent_id": agent_id,
                "type": "response",
                "model": model,
                "provider": provider,
                "request_type": request_type,
                "prompt": prompt,
                "response": response,
                "duration": duration,
                "context": context,
                "token_usage": token_usage,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "error": error,
                "timestamp": timestamp
            }
            self.interactions.append(log_entry)

# Global LLM logger instance
llm_logger = LLMLogger()
