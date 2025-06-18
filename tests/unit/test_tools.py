"""
Unit tests for the tool system components.
"""

import pytest
import asyncio
import tempfile
import sys
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

# Mock tools modules before importing
mock_tool_status = MagicMock()
mock_tool_status.SUCCESS = "success"
mock_tool_status.ERROR = "error"
mock_tool_status.WARNING = "warning"

mock_tool_result = MagicMock()
mock_base_tool = MagicMock()

mock_tools = MagicMock()
mock_tools.base_tool = MagicMock()
mock_tools.base_tool.BaseTool = mock_base_tool
mock_tools.base_tool.ToolResult = mock_tool_result
mock_tools.base_tool.ToolStatus = mock_tool_status
mock_tools.terminal_tool = MagicMock()
mock_tools.file_tool = MagicMock()
mock_tools.flutter_tool = MagicMock()
mock_tools.git_tool = MagicMock()
mock_tools.tool_manager = MagicMock()

sys.modules['tools'] = mock_tools
sys.modules['tools.base_tool'] = mock_tools.base_tool
sys.modules['tools.terminal_tool'] = mock_tools.terminal_tool
sys.modules['tools.file_tool'] = mock_tools.file_tool
sys.modules['tools.flutter_tool'] = mock_tools.flutter_tool
sys.modules['tools.git_tool'] = mock_tools.git_tool
sys.modules['tools.tool_manager'] = mock_tools.tool_manager

from tools.base_tool import BaseTool, ToolResult, ToolStatus
from tools.terminal_tool import TerminalTool
from tools.file_tool import FileTool
from tools.flutter_tool import FlutterTool
from tools.git_tool import GitTool
from tools.tool_manager import ToolManager


# Mock tool for testing
class MockTool(BaseTool):
    def __init__(self):
        super().__init__("mock_tool", "A mock tool for testing", timeout=10)
        
    async def execute(self, operation: str = "default", **kwargs) -> ToolResult:
        if operation == "success":
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output="Mock successful execution",
                data={"operation": operation, "kwargs": kwargs}
            )
        elif operation == "error":
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Mock error occurred"
            )
        elif operation == "timeout":
            await asyncio.sleep(20)  # Will timeout
            return ToolResult(status=ToolStatus.SUCCESS, output="Should not reach here")
        else:
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Mock execution: {operation}",
                data=kwargs
            )


@pytest.mark.unit
class TestBaseTool:
    """Test suite for BaseTool class."""
    
    def test_initialization(self):
        """Test tool initialization."""
        tool = MockTool()
        
        assert tool.name == "mock_tool"
        assert tool.description == "A mock tool for testing"
        assert tool.timeout == 10
        assert tool.is_async is True
        
    @pytest.mark.asyncio
    async def test_successful_execution(self):
        """Test successful tool execution."""
        tool = MockTool()
        
        result = await tool.execute(operation="success", param1="value1")
        
        assert result.status == ToolStatus.SUCCESS
        assert result.output == "Mock successful execution"
        assert result.error is None
        assert result.data["operation"] == "success"
        assert result.data["kwargs"]["param1"] == "value1"
        
    @pytest.mark.asyncio
    async def test_error_execution(self):
        """Test tool execution with error."""
        tool = MockTool()
        
        result = await tool.execute(operation="error")
        
        assert result.status == ToolStatus.ERROR
        assert result.output == ""
        assert result.error == "Mock error occurred"
        
    @pytest.mark.asyncio
    async def test_timeout_execution(self):
        """Test tool execution timeout."""
        tool = MockTool()
        tool.timeout = 1  # Short timeout
        
        result = await tool.execute_with_timeout(operation="timeout")
        
        assert result.status == ToolStatus.TIMEOUT
        assert "timeout" in result.error.lower()
        
    @pytest.mark.asyncio
    async def test_parameter_validation(self):
        """Test parameter validation."""
        tool = MockTool()
        
        # Should not raise exception with valid parameters
        tool.validate_parameters(["operation"], operation="test")
        
        # Should raise exception with missing required parameters
        with pytest.raises(ValueError, match="Missing required parameter"):
            tool.validate_parameters(["required_param"])
            
    def test_tool_result_creation(self):
        """Test ToolResult creation and properties."""
        result = ToolResult(
            status=ToolStatus.SUCCESS,
            output="Test output",
            error=None,
            data={"key": "value"},
            execution_time=1.5
        )
        
        assert result.status == ToolStatus.SUCCESS
        assert result.output == "Test output"
        assert result.error is None
        assert result.data["key"] == "value"
        assert result.execution_time == 1.5


@pytest.mark.unit
class TestTerminalTool:
    """Test suite for TerminalTool."""
    
    def test_initialization(self, temp_directory):
        """Test terminal tool initialization."""
        tool = TerminalTool(temp_directory)
        
        assert tool.name == "terminal"
        assert tool.project_directory == temp_directory
        
    @pytest.mark.asyncio
    async def test_execute_command(self, temp_directory):
        """Test command execution."""
        tool = TerminalTool(temp_directory)
        
        result = await tool.execute("execute", command="echo 'hello'")
        
        assert result.status == ToolStatus.SUCCESS
        assert "hello" in result.output
        
    @pytest.mark.asyncio
    async def test_check_command_exists(self, temp_directory):
        """Test checking if command exists."""
        tool = TerminalTool(temp_directory)
        
        # Test with a command that should exist
        result = await tool.execute("check_command_exists", command="echo")
        
        assert result.status == ToolStatus.SUCCESS
        assert result.data["exists"] is True
        
    @pytest.mark.asyncio
    async def test_execute_script(self, temp_directory):
        """Test script execution."""
        tool = TerminalTool(temp_directory)
        
        script_content = "echo 'Hello from script'"
        result = await tool.execute(
            "execute_script",
            script_content=script_content,
            script_type="bash"
        )
        
        assert result.status == ToolStatus.SUCCESS
        assert "Hello from script" in result.output


@pytest.mark.unit
class TestFileTool:
    """Test suite for FileTool."""
    
    def test_initialization(self, temp_directory):
        """Test file tool initialization."""
        tool = FileTool(temp_directory)
        
        assert tool.name == "file"
        assert tool.project_directory == temp_directory
        
    @pytest.mark.asyncio
    async def test_write_and_read_file(self, temp_directory):
        """Test writing and reading files."""
        tool = FileTool(temp_directory)
        
        file_path = "test.txt"
        content = "Hello, World!"
        
        # Write file
        write_result = await tool.execute(
            "write",
            file_path=file_path,
            content=content
        )
        
        assert write_result.status == ToolStatus.SUCCESS
        
        # Read file
        read_result = await tool.execute("read", file_path=file_path)
        
        assert read_result.status == ToolStatus.SUCCESS
        assert read_result.output == content
        
    @pytest.mark.asyncio
    async def test_create_directory(self, temp_directory):
        """Test directory creation."""
        tool = FileTool(temp_directory)
        
        dir_path = "test_dir/nested_dir"
        result = await tool.execute("create_directory", directory=dir_path)
        
        assert result.status == ToolStatus.SUCCESS
        
        # Check directory was created
        full_path = Path(temp_directory) / dir_path
        assert full_path.exists()
        assert full_path.is_dir()
        
    @pytest.mark.asyncio
    async def test_file_exists(self, temp_directory):
        """Test checking file existence."""
        tool = FileTool(temp_directory)
        
        # Test non-existent file
        result = await tool.execute("exists", path="nonexistent.txt")
        assert result.status == ToolStatus.SUCCESS
        assert result.data["exists"] is False
        
        # Create file and test again
        file_path = Path(temp_directory) / "existing.txt"
        file_path.write_text("content")
        
        result = await tool.execute("exists", path="existing.txt")
        assert result.status == ToolStatus.SUCCESS
        assert result.data["exists"] is True
        
    @pytest.mark.asyncio
    async def test_search_files(self, temp_directory):
        """Test file searching."""
        tool = FileTool(temp_directory)
        
        # Create some test files
        test_files = ["test1.txt", "test2.py", "other.txt"]
        for file_name in test_files:
            file_path = Path(temp_directory) / file_name
            file_path.write_text("content")
        
        # Search for .txt files
        result = await tool.execute("search", pattern="*.txt")
        
        assert result.status == ToolStatus.SUCCESS
        found_files = result.data["files"]
        assert "test1.txt" in found_files
        assert "other.txt" in found_files
        assert "test2.py" not in found_files


@pytest.mark.unit
class TestFlutterTool:
    """Test suite for FlutterTool."""
    
    def test_initialization(self, temp_directory):
        """Test Flutter tool initialization."""
        tool = FlutterTool(temp_directory)
        
        assert tool.name == "flutter"
        assert tool.project_directory == temp_directory
        
    @pytest.mark.asyncio
    async def test_flutter_doctor(self, temp_directory):
        """Test Flutter doctor command."""
        tool = FlutterTool(temp_directory)
        
        with patch.object(tool.terminal, 'execute') as mock_execute:
            mock_result = ToolResult(
                status=ToolStatus.SUCCESS,
                output="Flutter doctor output"
            )
            mock_execute.return_value = mock_result
            
            result = await tool.execute("doctor")
            
            assert result.status == ToolStatus.SUCCESS
            mock_execute.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_create_project(self, temp_directory):
        """Test Flutter project creation."""
        tool = FlutterTool(temp_directory)
        
        with patch.object(tool.terminal, 'execute') as mock_execute:
            mock_result = ToolResult(
                status=ToolStatus.SUCCESS,
                output="Created Flutter project"
            )
            mock_execute.return_value = mock_result
            
            result = await tool.execute(
                "create",
                project_name="test_app",
                template="app"
            )
            
            assert result.status == ToolStatus.SUCCESS
            mock_execute.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_pub_get(self, temp_directory):
        """Test pub get command."""
        tool = FlutterTool(temp_directory)
        
        with patch.object(tool.terminal, 'execute') as mock_execute:
            mock_result = ToolResult(
                status=ToolStatus.SUCCESS,
                output="Running pub get..."
            )
            mock_execute.return_value = mock_result
            
            result = await tool.execute("pub_get")
            
            assert result.status == ToolStatus.SUCCESS
            mock_execute.assert_called_once()


@pytest.mark.unit
class TestGitTool:
    """Test suite for GitTool."""
    
    def test_initialization(self, temp_directory):
        """Test Git tool initialization."""
        tool = GitTool(temp_directory)
        
        assert tool.name == "git"
        assert tool.project_directory == temp_directory
        
    @pytest.mark.asyncio
    async def test_init_repository(self, temp_directory):
        """Test Git repository initialization."""
        tool = GitTool(temp_directory)
        
        with patch.object(tool.terminal, 'execute') as mock_execute:
            mock_result = ToolResult(
                status=ToolStatus.SUCCESS,
                output="Initialized empty Git repository"
            )
            mock_execute.return_value = mock_result
            
            result = await tool.execute("init")
            
            assert result.status == ToolStatus.SUCCESS
            mock_execute.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_add_files(self, temp_directory):
        """Test adding files to Git."""
        tool = GitTool(temp_directory)
        
        with patch.object(tool.terminal, 'execute') as mock_execute:
            mock_result = ToolResult(
                status=ToolStatus.SUCCESS,
                output="Files added"
            )
            mock_execute.return_value = mock_result
            
            result = await tool.execute("add", files=["file1.txt", "file2.txt"])
            
            assert result.status == ToolStatus.SUCCESS
            mock_execute.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_commit(self, temp_directory):
        """Test Git commit."""
        tool = GitTool(temp_directory)
        
        with patch.object(tool.terminal, 'execute') as mock_execute:
            mock_result = ToolResult(
                status=ToolStatus.SUCCESS,
                output="Commit created"
            )
            mock_execute.return_value = mock_result
            
            result = await tool.execute("commit", message="Test commit")
            
            assert result.status == ToolStatus.SUCCESS
            mock_execute.assert_called_once()


@pytest.mark.unit
class TestToolManager:
    """Test suite for ToolManager."""
    
    def test_initialization(self, temp_directory):
        """Test tool manager initialization."""
        manager = ToolManager(temp_directory)
        
        assert manager.project_directory == temp_directory
        assert len(manager.tools) > 0
        
        # Check default tools are loaded
        expected_tools = ["terminal", "file", "flutter", "git", "analysis"]
        for tool_name in expected_tools:
            assert tool_name in manager.tools
            
    def test_register_tool(self, temp_directory):
        """Test registering a custom tool."""
        manager = ToolManager(temp_directory)
        custom_tool = MockTool()
        
        manager.register_tool(custom_tool, "custom_mock")
        
        assert "custom_mock" in manager.tools
        assert manager.get_tool("custom_mock") == custom_tool
        
    def test_get_tool(self, temp_directory):
        """Test getting tools by name."""
        manager = ToolManager(temp_directory)
        
        # Get existing tool
        terminal_tool = manager.get_tool("terminal")
        assert terminal_tool is not None
        assert terminal_tool.name == "terminal"
        
        # Get non-existent tool
        nonexistent = manager.get_tool("nonexistent")
        assert nonexistent is None
        
    def test_list_tools(self, temp_directory):
        """Test listing all tools."""
        manager = ToolManager(temp_directory)
        
        tools = manager.list_tools()
        assert isinstance(tools, list)
        assert len(tools) > 0
        assert "terminal" in tools
        assert "file" in tools
        
    def test_get_tool_info(self, temp_directory):
        """Test getting tool information."""
        manager = ToolManager(temp_directory)
        
        # Get info for existing tool
        info = manager.get_tool_info("terminal")
        assert info is not None
        assert info["name"] == "terminal"
        assert "description" in info
        assert "timeout" in info
        
        # Get info for non-existent tool
        info = manager.get_tool_info("nonexistent")
        assert info is None
        
    @pytest.mark.asyncio
    async def test_execute_tool(self, temp_directory):
        """Test executing tools through manager."""
        manager = ToolManager(temp_directory)
        
        # Register mock tool
        mock_tool = MockTool()
        manager.register_tool(mock_tool)
        
        # Execute tool
        result = await manager.execute_tool("mock_tool", operation="success")
        
        assert result.status == ToolStatus.SUCCESS
        assert result.output == "Mock successful execution"
        
    @pytest.mark.asyncio
    async def test_execute_nonexistent_tool(self, temp_directory):
        """Test executing non-existent tool."""
        manager = ToolManager(temp_directory)
        
        result = await manager.execute_tool("nonexistent")
        
        assert result.status == ToolStatus.ERROR
        assert "not found" in result.error
        
    @pytest.mark.asyncio
    async def test_execute_command(self, temp_directory):
        """Test executing commands through manager."""
        manager = ToolManager(temp_directory)
        
        result = await manager.execute_command("echo 'test'")
        
        assert result.status == ToolStatus.SUCCESS
        assert "test" in result.output
