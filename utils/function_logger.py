"""
Function Logger - Comprehensive logging for function calls, inputs, and outputs.
Provides decorators to track all function executions throughout the codebase.
"""

import json
import time
import logging
import traceback
import inspect
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from functools import wraps
import asyncio
from threading import Lock
import uuid

@dataclass
class FunctionCall:
    """Represents a single function call with full context."""
    call_id: str
    timestamp: str
    agent_id: Optional[str]
    module: str
    function_name: str
    class_name: Optional[str]
    args: List[Any]
    kwargs: Dict[str, Any]
    return_value: Any
    exception: Optional[str] = None
    duration_seconds: float = 0.0
    stack_trace: Optional[List[str]] = None
    file_path: str = ""
    line_number: int = 0
    is_async: bool = False
    success: bool = True

@dataclass
class ToolUsage:
    """Represents tool usage with complete input/output tracking."""
    usage_id: str
    timestamp: str
    agent_id: str
    tool_name: str
    operation: str
    input_params: Dict[str, Any]
    output_result: Any
    status: str
    duration_seconds: float
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class FunctionLogger:
    """
    Comprehensive function call logger with detailed tracking capabilities.
    """
    
    def __init__(self, log_dir: str = "logs", enable_file_logging: bool = True):
        self.log_dir = Path(log_dir)
        self.enable_file_logging = enable_file_logging
        self.function_calls: List[FunctionCall] = []
        self.tool_usages: List[ToolUsage] = []
        self._lock = Lock()
        self._async_lock = asyncio.Lock()
        
        # Create log directory
        if self.enable_file_logging:
            self.log_dir.mkdir(exist_ok=True)
        
        # Session tracking
        self.session_start = datetime.now()
        self.session_id = self.session_start.strftime("%Y%m%d_%H%M%S")
        
        # Setup logging
        self.logger = logging.getLogger('FlutterSwarm.FunctionLogger')
        self._setup_logging()
        
        # Statistics
        self.total_calls = 0
        self.total_duration = 0.0
        self.error_count = 0
        
        self.logger.info(f"📊 Function Logger initialized - Session: {self.session_id}")
    
    def _setup_logging(self):
        """Setup function call logging."""
        if not self.logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(logging.INFO)
            
            # File handler for function calls
            if self.enable_file_logging:
                function_log_file = self.log_dir / f"function_calls_{self.session_id}.log"
                file_handler = logging.FileHandler(function_log_file)
                file_handler.setLevel(logging.DEBUG)
                
                # Detailed formatter
                formatter = logging.Formatter(
                    '%(asctime)s | FUNC | %(levelname)-8s | %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S'
                )
                file_handler.setFormatter(formatter)
                console_handler.setFormatter(formatter)
                
                self.logger.addHandler(file_handler)
            
            self.logger.addHandler(console_handler)
            self.logger.setLevel(logging.DEBUG)
    
    def log_function_call(self, func_call: FunctionCall):
        """Log a function call with complete details."""
        with self._lock:
            self.function_calls.append(func_call)
            self.total_calls += 1
            self.total_duration += func_call.duration_seconds
            if not func_call.success:
                self.error_count += 1
        
        # Log to file with full details
        if func_call.success:
            self.logger.info(f"✅ FUNCTION CALL [{func_call.call_id}]")
        else:
            self.logger.error(f"❌ FUNCTION ERROR [{func_call.call_id}]")
        
        self.logger.info(f"   Module: {func_call.module}")
        self.logger.info(f"   Function: {func_call.function_name}")
        if func_call.class_name:
            self.logger.info(f"   Class: {func_call.class_name}")
        if func_call.agent_id:
            self.logger.info(f"   Agent: {func_call.agent_id}")
        self.logger.info(f"   Duration: {func_call.duration_seconds:.4f}s")
        self.logger.info(f"   File: {func_call.file_path}:{func_call.line_number}")
        
        # Log function arguments (sanitized)
        if func_call.args:
            sanitized_args = self._sanitize_for_logging(func_call.args)
            self.logger.info(f"   Args: {sanitized_args}")
        
        if func_call.kwargs:
            sanitized_kwargs = self._sanitize_for_logging(func_call.kwargs)
            self.logger.info(f"   Kwargs: {sanitized_kwargs}")
        
        # Log return value (sanitized)
        if func_call.return_value is not None:
            sanitized_return = self._sanitize_for_logging(func_call.return_value)
            self.logger.info(f"   Return: {sanitized_return}")
        
        # Log exception if present
        if func_call.exception:
            self.logger.error(f"   Exception: {func_call.exception}")
            if func_call.stack_trace:
                self.logger.error("   Stack Trace:")
                for line in func_call.stack_trace[-10:]:  # Last 10 lines
                    self.logger.error(f"     {line}")
    
    def log_tool_usage(self, tool_usage: ToolUsage):
        """Log tool usage with complete input/output tracking."""
        with self._lock:
            self.tool_usages.append(tool_usage)
        
        if tool_usage.status == "success":
            self.logger.info(f"🔧 TOOL USAGE [{tool_usage.usage_id}]")
        else:
            self.logger.error(f"🔧 TOOL ERROR [{tool_usage.usage_id}]")
        
        self.logger.info(f"   Agent: {tool_usage.agent_id}")
        self.logger.info(f"   Tool: {tool_usage.tool_name}")
        self.logger.info(f"   Operation: {tool_usage.operation}")
        self.logger.info(f"   Status: {tool_usage.status}")
        self.logger.info(f"   Duration: {tool_usage.duration_seconds:.4f}s")
        
        # Log input parameters (sanitized)
        if tool_usage.input_params:
            sanitized_input = self._sanitize_for_logging(tool_usage.input_params)
            self.logger.info(f"   Input: {sanitized_input}")
        
        # Log output result (sanitized)
        if tool_usage.output_result is not None:
            sanitized_output = self._sanitize_for_logging(tool_usage.output_result)
            self.logger.info(f"   Output: {sanitized_output}")
        
        # Log error if present
        if tool_usage.error:
            self.logger.error(f"   Error: {tool_usage.error}")
    
    def _sanitize_for_logging(self, data: Any, max_length: int = 500) -> str:
        """Sanitize data for safe logging."""
        try:
            if data is None:
                return "None"
            elif isinstance(data, (str, int, float, bool)):
                str_data = str(data)
                if len(str_data) > max_length:
                    return str_data[:max_length] + "..."
                return str_data
            elif isinstance(data, (list, tuple)):
                if len(data) > 10:
                    return f"[List/Tuple with {len(data)} items] {str(data[:3])}..."
                return str(data)[:max_length]
            elif isinstance(data, dict):
                if len(data) > 20:
                    keys = list(data.keys())[:5]
                    return f"{{Dict with {len(data)} keys: {keys}...}}"
                return str(data)[:max_length]
            else:
                return f"<{type(data).__name__}: {str(data)[:max_length]}>"
        except Exception:
            return f"<{type(data).__name__}: [unable to serialize]>"
    
    def function_tracker(self, agent_id: Optional[str] = None, 
                        log_args: bool = True, log_return: bool = True):
        """
        Decorator to track function calls with complete input/output logging.
        
        Args:
            agent_id: Optional agent ID for context
            log_args: Whether to log function arguments
            log_return: Whether to log return values
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self._track_sync_function(func, args, kwargs, agent_id, log_args, log_return)
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._track_async_function(func, args, kwargs, agent_id, log_args, log_return)
            
            # Return appropriate wrapper based on function type
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return wrapper
        return decorator
    
    def _track_sync_function(self, func: Callable, args: tuple, kwargs: dict, 
                           agent_id: Optional[str], log_args: bool, log_return: bool):
        """Track synchronous function execution."""
        call_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Get function metadata
        frame = inspect.currentframe().f_back
        file_path = frame.f_code.co_filename
        line_number = frame.f_lineno
        
        func_call = FunctionCall(
            call_id=call_id,
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            module=func.__module__,
            function_name=func.__name__,
            class_name=getattr(func, '__qualname__', '').split('.')[-2] if '.' in getattr(func, '__qualname__', '') else None,
            args=list(args) if log_args else [],
            kwargs=dict(kwargs) if log_args else {},
            return_value=None,
            duration_seconds=0.0,
            stack_trace=None,
            file_path=file_path,
            line_number=line_number,
            is_async=False,
            success=True
        )
        
        try:
            result = func(*args, **kwargs)
            func_call.return_value = result if log_return else "<return value not logged>"
            func_call.duration_seconds = time.time() - start_time
            self.log_function_call(func_call)
            return result
        except Exception as e:
            func_call.duration_seconds = time.time() - start_time
            func_call.success = False
            func_call.exception = str(e)
            func_call.stack_trace = traceback.format_tb(e.__traceback__)
            self.log_function_call(func_call)
            raise
    
    async def _track_async_function(self, func: Callable, args: tuple, kwargs: dict, 
                                  agent_id: Optional[str], log_args: bool, log_return: bool):
        """Track asynchronous function execution."""
        call_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Get function metadata
        frame = inspect.currentframe().f_back
        file_path = frame.f_code.co_filename
        line_number = frame.f_lineno
        
        func_call = FunctionCall(
            call_id=call_id,
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            module=func.__module__,
            function_name=func.__name__,
            class_name=getattr(func, '__qualname__', '').split('.')[-2] if '.' in getattr(func, '__qualname__', '') else None,
            args=list(args) if log_args else [],
            kwargs=dict(kwargs) if log_args else {},
            return_value=None,
            duration_seconds=0.0,
            stack_trace=None,
            file_path=file_path,
            line_number=line_number,
            is_async=True,
            success=True
        )
        
        try:
            result = await func(*args, **kwargs)
            func_call.return_value = result if log_return else "<return value not logged>"
            func_call.duration_seconds = time.time() - start_time
            self.log_function_call(func_call)
            return result
        except Exception as e:
            func_call.duration_seconds = time.time() - start_time
            func_call.success = False
            func_call.exception = str(e)
            func_call.stack_trace = traceback.format_tb(e.__traceback__)
            self.log_function_call(func_call)
            raise
    
    def tool_tracker(self, agent_id: str, tool_name: str):
        """
        Decorator to track tool usage with complete input/output logging.
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                return self._track_tool_usage(func, args, kwargs, agent_id, tool_name)
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                return await self._track_async_tool_usage(func, args, kwargs, agent_id, tool_name)
            
            if asyncio.iscoroutinefunction(func):
                return async_wrapper
            else:
                return wrapper
        return decorator
    
    def _track_tool_usage(self, func: Callable, args: tuple, kwargs: dict, 
                         agent_id: str, tool_name: str):
        """Track synchronous tool usage."""
        usage_id = str(uuid.uuid4())
        start_time = time.time()
        
        tool_usage = ToolUsage(
            usage_id=usage_id,
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            tool_name=tool_name,
            operation=func.__name__,
            input_params={"args": list(args), "kwargs": dict(kwargs)},
            output_result=None,
            status="pending",
            duration_seconds=0.0
        )
        
        try:
            result = func(*args, **kwargs)
            tool_usage.output_result = result
            tool_usage.status = "success"
            tool_usage.duration_seconds = time.time() - start_time
            self.log_tool_usage(tool_usage)
            return result
        except Exception as e:
            tool_usage.status = "error"
            tool_usage.error = str(e)
            tool_usage.duration_seconds = time.time() - start_time
            self.log_tool_usage(tool_usage)
            raise
    
    async def _track_async_tool_usage(self, func: Callable, args: tuple, kwargs: dict, 
                                    agent_id: str, tool_name: str):
        """Track asynchronous tool usage."""
        usage_id = str(uuid.uuid4())
        start_time = time.time()
        
        tool_usage = ToolUsage(
            usage_id=usage_id,
            timestamp=datetime.now().isoformat(),
            agent_id=agent_id,
            tool_name=tool_name,
            operation=func.__name__,
            input_params={"args": list(args), "kwargs": dict(kwargs)},
            output_result=None,
            status="pending",
            duration_seconds=0.0
        )
        
        try:
            result = await func(*args, **kwargs)
            tool_usage.output_result = result
            tool_usage.status = "success"
            tool_usage.duration_seconds = time.time() - start_time
            self.log_tool_usage(tool_usage)
            return result
        except Exception as e:
            tool_usage.status = "error"
            tool_usage.error = str(e)
            tool_usage.duration_seconds = time.time() - start_time
            self.log_tool_usage(tool_usage)
            raise
    
    def export_function_calls_to_json(self, filename: Optional[str] = None) -> str:
        """Export all function calls to JSON file."""
        if not filename:
            filename = f"function_calls_{self.session_id}.json"
        
        filepath = self.log_dir / filename
        
        export_data = {
            "session_info": {
                "session_id": self.session_id,
                "session_start": self.session_start.isoformat(),
                "export_time": datetime.now().isoformat()
            },
            "summary": self.get_session_summary(),
            "function_calls": [asdict(call) for call in self.function_calls],
            "tool_usages": [asdict(usage) for usage in self.tool_usages]
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        self.logger.info(f"📄 Function calls exported to {filepath}")
        return str(filepath)
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get comprehensive session summary."""
        with self._lock:
            # Function call analysis
            function_stats = {}
            agent_stats = {}
            module_stats = {}
            
            for call in self.function_calls:
                # Function statistics
                func_key = f"{call.module}.{call.function_name}"
                if func_key not in function_stats:
                    function_stats[func_key] = {"count": 0, "total_duration": 0.0, "errors": 0}
                function_stats[func_key]["count"] += 1
                function_stats[func_key]["total_duration"] += call.duration_seconds
                if not call.success:
                    function_stats[func_key]["errors"] += 1
                
                # Agent statistics
                if call.agent_id:
                    if call.agent_id not in agent_stats:
                        agent_stats[call.agent_id] = {"count": 0, "total_duration": 0.0, "errors": 0}
                    agent_stats[call.agent_id]["count"] += 1
                    agent_stats[call.agent_id]["total_duration"] += call.duration_seconds
                    if not call.success:
                        agent_stats[call.agent_id]["errors"] += 1
                
                # Module statistics
                if call.module not in module_stats:
                    module_stats[call.module] = {"count": 0, "total_duration": 0.0, "errors": 0}
                module_stats[call.module]["count"] += 1
                module_stats[call.module]["total_duration"] += call.duration_seconds
                if not call.success:
                    module_stats[call.module]["errors"] += 1
            
            # Tool usage analysis
            tool_stats = {}
            for usage in self.tool_usages:
                if usage.tool_name not in tool_stats:
                    tool_stats[usage.tool_name] = {"count": 0, "total_duration": 0.0, "errors": 0}
                tool_stats[usage.tool_name]["count"] += 1
                tool_stats[usage.tool_name]["total_duration"] += usage.duration_seconds
                if usage.status != "success":
                    tool_stats[usage.tool_name]["errors"] += 1
            
            return {
                "session_id": self.session_id,
                "session_duration": str(datetime.now() - self.session_start),
                "total_function_calls": self.total_calls,
                "total_tool_usages": len(self.tool_usages),
                "total_duration": self.total_duration,
                "error_count": self.error_count,
                "success_rate": (self.total_calls - self.error_count) / max(self.total_calls, 1),
                "average_duration": self.total_duration / max(self.total_calls, 1),
                "function_statistics": function_stats,
                "agent_statistics": agent_stats,
                "module_statistics": module_stats,
                "tool_statistics": tool_stats
            }

# Global function logger instance
function_logger = FunctionLogger()

# Convenience decorators
def track_function(agent_id: Optional[str] = None, log_args: bool = True, log_return: bool = True):
    """Convenience decorator for tracking function calls."""
    return function_logger.function_tracker(agent_id, log_args, log_return)

def track_tool(agent_id: str, tool_name: str):
    """Convenience decorator for tracking tool usage."""
    return function_logger.tool_tracker(agent_id, tool_name)
