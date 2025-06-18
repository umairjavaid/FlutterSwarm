"""
Base tool class for FlutterSwarm agents.
"""

import asyncio
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

class ToolStatus(Enum):
    """Tool execution status."""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    TIMEOUT = "timeout"

@dataclass
class ToolResult:
    """Result of tool execution."""
    status: ToolStatus
    output: str
    error: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    execution_time: Optional[float] = None

class BaseTool(ABC):
    """
    Base class for all agent tools.
    """
    
    def __init__(self, name: str, description: str, timeout: int = 30):
        self.name = name
        self.description = description
        self.timeout = timeout
        self.is_async = True
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with given parameters.
        
        Args:
            **kwargs: Tool-specific parameters
            
        Returns:
            ToolResult with execution outcome
        """
        pass
    
    async def execute_with_timeout(self, **kwargs) -> ToolResult:
        """Execute tool with timeout handling."""
        try:
            result = await asyncio.wait_for(
                self.execute(**kwargs), 
                timeout=self.timeout
            )
            return result
        except asyncio.TimeoutError:
            return ToolResult(
                status=ToolStatus.TIMEOUT,
                output="",
                error=f"Tool '{self.name}' timed out after {self.timeout} seconds"
            )
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Tool '{self.name}' failed: {str(e)}"
            )
    
    def validate_parameters(self, required_params: List[str], **kwargs) -> bool:
        """Validate that required parameters are provided."""
        missing_params = [param for param in required_params if param not in kwargs]
        if missing_params:
            raise ValueError(f"Missing required parameters: {missing_params}")
        return True
    
    def __str__(self) -> str:
        return f"{self.name}: {self.description}"
