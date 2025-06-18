"""
Mock implementations for FlutterSwarm testing.
"""

import asyncio
from unittest.mock import MagicMock, AsyncMock
from typing import Dict, Any, List, Optional
from datetime import datetime

from shared.state import AgentStatus, MessageType, AgentMessage
from tools.base_tool import ToolResult, ToolStatus


class MockAgent:
    """Mock agent for testing agent interactions."""
    
    def __init__(self, agent_id: str, capabilities: List[str] = None):
        self.agent_id = agent_id
        self.capabilities = capabilities or []
        self.is_running = False
        self.current_task = None
        self.status = AgentStatus.IDLE
        self.progress = 0.0
        self.messages = []
        
    async def start(self):
        """Mock start method."""
        self.is_running = True
        self.status = AgentStatus.IDLE
        
    async def stop(self):
        """Mock stop method."""
        self.is_running = False
        self.status = AgentStatus.IDLE
        
    async def execute_task(self, task_data: Dict[str, Any]):
        """Mock task execution."""
        self.current_task = task_data.get("task_description")
        self.status = AgentStatus.WORKING
        
        # Simulate work with progress updates
        for i in range(5):
            self.progress = (i + 1) / 5
            await asyncio.sleep(0.02)  # Very short delay for testing
            
        self.status = AgentStatus.COMPLETED
        return {"status": "completed", "result": f"Mock result for {self.current_task}"}
        
    async def process_message(self, message: AgentMessage):
        """Mock message processing."""
        self.messages.append(message)
        return {"status": "processed", "response": "Mock response"}
        
    def send_message_to_agent(self, to_agent: str, message_type: MessageType, 
                             content: Dict[str, Any], priority: int = 3) -> str:
        """Mock message sending."""
        message_id = f"msg_{len(self.messages)}"
        return message_id


class MockToolManager:
    """Mock tool manager for testing."""
    
    def __init__(self):
        self.tools = {}
        self.execution_history = []
        
    async def execute_tool(self, tool_name: str, operation: str = None, **kwargs) -> ToolResult:
        """Mock tool execution."""
        self.execution_history.append({
            "tool": tool_name,
            "operation": operation,
            "kwargs": kwargs,
            "timestamp": datetime.now()
        })
        
        # Simulate different tool behaviors
        if tool_name == "terminal":
            return self._mock_terminal_tool(operation, **kwargs)
        elif tool_name == "file":
            return self._mock_file_tool(operation, **kwargs)
        elif tool_name == "flutter":
            return self._mock_flutter_tool(operation, **kwargs)
        elif tool_name == "git":
            return self._mock_git_tool(operation, **kwargs)
        elif tool_name == "analysis":
            return self._mock_analysis_tool(operation, **kwargs)
        else:
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Mock output for {tool_name}",
                execution_time=0.1
            )
            
    def _mock_terminal_tool(self, operation: str, **kwargs) -> ToolResult:
        """Mock terminal tool operations."""
        command = kwargs.get("command", "")
        
        if "error" in command or command.startswith("exit"):
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Command failed",
                execution_time=0.1
            )
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Mock terminal output for: {command}",
            execution_time=0.1
        )
        
    def _mock_file_tool(self, operation: str, **kwargs) -> ToolResult:
        """Mock file tool operations."""
        if operation == "read":
            file_path = kwargs.get("file_path", "")
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Mock file content from {file_path}",
                execution_time=0.05
            )
        elif operation == "write":
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output="File written successfully",
                execution_time=0.05
            )
        elif operation == "exists":
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output="true",
                data={"exists": True},
                execution_time=0.01
            )
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Mock file operation: {operation}",
            execution_time=0.05
        )
        
    def _mock_flutter_tool(self, operation: str, **kwargs) -> ToolResult:
        """Mock Flutter tool operations."""
        if operation == "doctor":
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output="Flutter (Channel stable, 3.0.0)",
                data={"flutter_version": "3.0.0"},
                execution_time=2.0
            )
        elif operation == "test":
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output="All tests passed: 20 passed, 0 failed",
                data={
                    "tests_passed": 20,
                    "tests_failed": 0,
                    "coverage": 85.5
                },
                execution_time=10.0
            )
        elif operation == "build":
            platform = kwargs.get("platform", "apk")
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Build completed for {platform}",
                data={"platform": platform, "build_time": 45.2},
                execution_time=30.0
            )
            
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Mock Flutter operation: {operation}",
            execution_time=1.0
        )
        
    def _mock_git_tool(self, operation: str, **kwargs) -> ToolResult:
        """Mock Git tool operations."""
        if operation == "init":
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output="Initialized empty Git repository",
                execution_time=0.5
            )
        elif operation == "status":
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output="On branch main\nnothing to commit, working tree clean",
                execution_time=0.2
            )
        elif operation == "commit":
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output="[main abc123] Test commit",
                execution_time=0.3
            )
            
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Mock Git operation: {operation}",
            execution_time=0.2
        )
        
    def _mock_analysis_tool(self, operation: str, **kwargs) -> ToolResult:
        """Mock analysis tool operations."""
        if operation == "security_scan":
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output="Security scan completed",
                data={
                    "issues_found": 0,
                    "scan_time": 15.3,
                    "severity_levels": {"high": 0, "medium": 0, "low": 0}
                },
                execution_time=15.0
            )
        elif operation == "code_metrics":
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output="Code metrics calculated",
                data={
                    "complexity": 2.3,
                    "maintainability": 85.2,
                    "lines_of_code": 1250,
                    "technical_debt": "2h 30m"
                },
                execution_time=5.0
            )
            
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Mock analysis operation: {operation}",
            execution_time=2.0
        )


class MockAnthropicClient:
    """Mock Anthropic client for testing."""
    
    def __init__(self):
        self.call_count = 0
        self.responses = []
        
    def invoke(self, messages):
        """Mock synchronous invoke."""
        self.call_count += 1
        response = MagicMock()
        response.content = f"Mock AI response {self.call_count}"
        self.responses.append(response.content)
        return response
        
    async def ainvoke(self, messages):
        """Mock asynchronous invoke."""
        self.call_count += 1
        response = MagicMock()
        response.content = f"Mock AI response {self.call_count}"
        self.responses.append(response.content)
        return response


class MockConfigManager:
    """Mock configuration manager for testing."""
    
    def __init__(self, config_data: Dict[str, Any] = None):
        self.config_data = config_data or {}
        
    def get(self, key: str, default=None):
        """Get configuration value."""
        keys = key.split('.')
        current = self.config_data
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
                
        return current
        
    def get_agent_config(self, agent_id: str = None):
        """Get agent configuration."""
        if agent_id:
            return self.config_data.get('agents', {}).get(agent_id, {})
        return self.config_data.get('agents', {})
        
    def get_cli_config(self):
        """Get CLI configuration."""
        return self.config_data.get('cli', {})
        
    def get_display_config(self):
        """Get display configuration."""
        return self.config_data.get('display', {})
        
    def get_messages_config(self):
        """Get messages configuration."""
        return self.config_data.get('messages', {})
        
    def get_tool_config(self, tool_name: str = None):
        """Get tool configuration."""
        if tool_name:
            return self.config_data.get('tools', {}).get(tool_name, {})
        return self.config_data.get('tools', {})


class MockFileSystem:
    """Mock file system for testing file operations."""
    
    def __init__(self):
        self.files = {}
        self.directories = set()
        
    def write_file(self, path: str, content: str):
        """Mock file writing."""
        self.files[path] = content
        # Add directory to set
        dir_path = '/'.join(path.split('/')[:-1])
        if dir_path:
            self.directories.add(dir_path)
            
    def read_file(self, path: str) -> str:
        """Mock file reading."""
        return self.files.get(path, "")
        
    def file_exists(self, path: str) -> bool:
        """Check if file exists."""
        return path in self.files
        
    def create_directory(self, path: str):
        """Create directory."""
        self.directories.add(path)
        
    def directory_exists(self, path: str) -> bool:
        """Check if directory exists."""
        return path in self.directories
        
    def list_files(self, pattern: str = "*") -> List[str]:
        """List files matching pattern."""
        # Simple implementation - return all files
        return list(self.files.keys())


class MockProjectManager:
    """Mock project manager for testing project operations."""
    
    def __init__(self):
        self.projects = {}
        
    def create_project_structure(self, project_id: str, name: str) -> Dict[str, Any]:
        """Mock project structure creation."""
        structure = {
            "lib/main.dart": "Flutter main file",
            "lib/models/": "Models directory",
            "lib/services/": "Services directory",
            "test/": "Test directory",
            "pubspec.yaml": "Flutter configuration"
        }
        
        self.projects[project_id] = {
            "name": name,
            "structure": structure,
            "created_at": datetime.now()
        }
        
        return structure
        
    def get_project_files(self, project_id: str) -> List[str]:
        """Get project files."""
        project = self.projects.get(project_id, {})
        return list(project.get("structure", {}).keys())
        
    def validate_project_structure(self, project_id: str) -> Dict[str, Any]:
        """Validate project structure."""
        if project_id in self.projects:
            return {
                "valid": True,
                "issues": [],
                "recommendations": ["Add integration tests"]
            }
        return {
            "valid": False,
            "issues": ["Project not found"],
            "recommendations": []
        }


# Helper functions for test mocks

def create_mock_build_result(status: str = "completed", 
                           files_created: int = 15,
                           has_issues: bool = False) -> Dict[str, Any]:
    """Create a mock build result."""
    result = {
        "status": status,
        "files_created": files_created,
        "architecture_decisions": 3,
        "test_results": {
            "unit": {"status": "passed", "count": 20},
            "widget": {"status": "passed", "count": 8}
        },
        "security_findings": [],
        "performance_metrics": {
            "build_time": 45.2,
            "app_size": "12.5MB"
        },
        "documentation": ["README.md"],
        "deployment_config": {"platform": "firebase"}
    }
    
    if has_issues:
        result["security_findings"] = [
            {
                "severity": "medium",
                "type": "insecure_storage",
                "description": "Test security issue"
            }
        ]
        result["test_results"]["unit"]["status"] = "failed"
        result["test_results"]["unit"]["failures"] = 2
        
    return result


def create_mock_agent_state(agent_id: str, 
                          status: AgentStatus = AgentStatus.IDLE,
                          current_task: str = None,
                          progress: float = 0.0) -> Dict[str, Any]:
    """Create mock agent state."""
    return {
        "agent_id": agent_id,
        "status": status.value,
        "current_task": current_task,
        "progress": progress,
        "capabilities": ["test_capability"],
        "last_update": datetime.now().isoformat()
    }
