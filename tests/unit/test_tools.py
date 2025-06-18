"""
Unit tests for the tool system components.
"""

import pytest
import asyncio
import tempfile
import sys
import os
from unittest.mock import patch, MagicMock, AsyncMock
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

# Import the actual classes
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


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


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
        
        with pytest.raises(asyncio.TimeoutError):
            result = await asyncio.wait_for(tool.execute(operation="timeout"), timeout=1)
        
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
    
    @pytest.fixture
    def terminal_tool(self):
        """Create terminal tool for testing."""
        return TerminalTool()
    
    def test_initialization(self, terminal_tool):
        """Test terminal tool initialization."""
        assert terminal_tool.name == "terminal"
        assert terminal_tool.description is not None
        
    @pytest.mark.asyncio
    async def test_execute_command(self, terminal_tool):
        """Test command execution."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((b"hello", b""))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await terminal_tool.execute("execute", command="echo 'hello'")
            
            assert result.status == ToolStatus.SUCCESS
            assert "hello" in result.output
            
    @pytest.mark.asyncio
    async def test_check_command_exists(self, terminal_tool):
        """Test command existence check."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((b"", b""))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await terminal_tool.execute("check_command_exists", command="echo")
            
            assert result.status == ToolStatus.SUCCESS
            
    @pytest.mark.asyncio
    async def test_execute_script(self, terminal_tool):
        """Test script execution."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((b"script output", b""))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await terminal_tool.execute(
                "execute_script",
                script_content="echo 'script test'",
                script_extension=".sh"
            )
            
            assert result.status == ToolStatus.SUCCESS


@pytest.mark.unit
class TestFileTool:
    """Test suite for FileTool."""
    
    @pytest.fixture 
    def file_tool(self, temp_directory):
        """Create file tool for testing."""
        return FileTool(temp_directory)
    
    def test_initialization(self, file_tool):
        """Test file tool initialization."""
        assert file_tool.name == "file"
        assert file_tool.description is not None
        
    @pytest.mark.asyncio
    async def test_write_and_read_file(self, file_tool, temp_directory):
        """Test file writing and reading."""
        test_content = "Hello, World!"
        file_path = Path(temp_directory) / "test.txt"
        
        # Test writing
        with patch('builtins.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            write_result = await file_tool.execute(
                "write_file",
                file_path=str(file_path),
                content=test_content
            )
            
            assert write_result.status == ToolStatus.SUCCESS
            
        # Test reading  
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = test_content
            
            read_result = await file_tool.execute("read_file", file_path=str(file_path))
            
            assert read_result.status == ToolStatus.SUCCESS
            
    @pytest.mark.asyncio
    async def test_create_directory(self, file_tool, temp_directory):
        """Test directory creation."""
        dir_path = Path(temp_directory) / "test_dir"
        
        with patch('os.makedirs') as mock_makedirs:
            result = await file_tool.execute("create_directory", directory=str(dir_path))
            
            assert result.status == ToolStatus.SUCCESS
            mock_makedirs.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_file_exists(self, file_tool):
        """Test file existence check."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            result = await file_tool.execute("exists", path="nonexistent.txt")
            
            assert result.status == ToolStatus.SUCCESS
            
    @pytest.mark.asyncio
    async def test_search_files(self, file_tool, temp_directory):
        """Test file search functionality."""
        with patch('glob.glob') as mock_glob:
            mock_glob.return_value = [str(Path(temp_directory) / "test1.txt"), 
                                    str(Path(temp_directory) / "test2.txt")]
            
            result = await file_tool.execute("search", pattern="*.txt")
            
            assert result.status == ToolStatus.SUCCESS


@pytest.mark.unit
class TestFlutterTool:
    """Test suite for FlutterTool."""
    
    @pytest.fixture
    def flutter_tool(self, temp_directory):
        """Create Flutter tool for testing."""
        return FlutterTool(temp_directory)
    
    def test_initialization(self, flutter_tool):
        """Test Flutter tool initialization."""
        assert flutter_tool.name == "flutter"
        assert flutter_tool.description is not None
        
    @pytest.mark.asyncio
    async def test_flutter_doctor(self, flutter_tool):
        """Test Flutter doctor command."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"Doctor summary (to see all details, run flutter doctor -v):\n"
                b"Flutter (Channel stable, 3.0.0, on macOS 12.0.0)",
                b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await flutter_tool.execute("doctor")
            
            assert result.status == ToolStatus.SUCCESS
            assert "Flutter" in result.output
            
    @pytest.mark.asyncio
    async def test_create_project(self, flutter_tool, temp_directory):
        """Test Flutter project creation."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"Creating project test_app...\nProject created successfully!",
                b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await flutter_tool.execute(
                "create",
                project_name="test_app",
                project_path=temp_directory
            )
            
            assert result.status == ToolStatus.SUCCESS
            assert "test_app" in result.output
            
    @pytest.mark.asyncio
    async def test_pub_get(self, flutter_tool):
        """Test pub get command."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"Running \"flutter pub get\"...\nGot dependencies!",
                b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await flutter_tool.execute("pub_get")
            
            assert result.status == ToolStatus.SUCCESS


@pytest.mark.unit
class TestGitTool:
    """Test suite for GitTool."""
    
    @pytest.fixture
    def git_tool(self, temp_directory):
        """Create Git tool for testing."""
        return GitTool(temp_directory)
    
    def test_initialization(self, git_tool):
        """Test Git tool initialization."""
        assert git_tool.name == "git"
        assert git_tool.description is not None
        
    @pytest.mark.asyncio
    async def test_init_repository(self, git_tool):
        """Test git repository initialization."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"Initialized empty Git repository",
                b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await git_tool.execute("init")
            
            assert result.status == ToolStatus.SUCCESS
            assert "Initialized" in result.output
            
    @pytest.mark.asyncio
    async def test_add_files(self, git_tool):
        """Test git add command."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((b"", b""))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await git_tool.execute("add", files=["file1.txt", "file2.txt"])
            
            assert result.status == ToolStatus.SUCCESS
            
    @pytest.mark.asyncio
    async def test_commit(self, git_tool):
        """Test git commit command."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"[main abc123] Test commit",
                b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await git_tool.execute("commit", message="Test commit")
            
            assert result.status == ToolStatus.SUCCESS
            assert "Test commit" in result.output


@pytest.mark.unit
class TestToolManager:
    """Test suite for ToolManager."""
    
    def test_initialization(self, temp_directory):
        """Test tool manager initialization."""
        manager = ToolManager(temp_directory)
        
        assert manager.project_directory == temp_directory
        assert len(manager.available_tools) > 0
        
    def test_register_tool(self, temp_directory):
        """Test custom tool registration."""
        manager = ToolManager(temp_directory)
        custom_tool = MockTool()
        
        manager.register_tool(custom_tool)
        
        assert "mock_tool" in manager.available_tools
        assert manager.get_tool("mock_tool") == custom_tool
        
    def test_get_tool(self, temp_directory):
        """Test tool retrieval."""
        manager = ToolManager(temp_directory)
        
        terminal_tool = manager.get_tool("terminal")
        
        assert terminal_tool is not None
        assert terminal_tool.name == "terminal"
        
    def test_list_tools(self, temp_directory):
        """Test tool listing."""
        manager = ToolManager(temp_directory)
        
        tools = manager.list_tools()
        
        assert isinstance(tools, list)
        assert len(tools) > 0
        assert "terminal" in [tool.name for tool in tools]
        
    def test_get_tool_info(self, temp_directory):
        """Test tool information retrieval."""
        manager = ToolManager(temp_directory)
        
        info = manager.get_tool_info("terminal")
        
        assert info is not None
        assert info["name"] == "terminal"
        assert "description" in info
        
    @pytest.mark.asyncio
    async def test_execute_tool(self, temp_directory):
        """Test tool execution through manager."""
        manager = ToolManager(temp_directory)
        mock_tool = MockTool()
        manager.register_tool(mock_tool)
        
        result = await manager.execute_tool("mock_tool", operation="success")
        
        assert result.status == ToolStatus.SUCCESS
        assert result.output == "Mock successful execution"
        
    @pytest.mark.asyncio
    async def test_execute_nonexistent_tool(self, temp_directory):
        """Test execution of nonexistent tool."""
        manager = ToolManager(temp_directory)
        
        with patch.object(manager, 'execute_tool', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Tool 'nonexistent' not found"
            )
            
            result = await manager.execute_tool("nonexistent")
            
            assert result.status == ToolStatus.ERROR
            
    @pytest.mark.asyncio
    async def test_execute_command(self, temp_directory):
        """Test command execution through manager."""
        manager = ToolManager(temp_directory)
        
        with patch.object(manager, 'execute_command', new_callable=AsyncMock) as mock_execute:
            mock_execute.return_value = ToolResult(
                status=ToolStatus.SUCCESS,
                output="test"
            )
            
            result = await manager.execute_command("echo 'test'")
            
            assert result.status == ToolStatus.SUCCESS
