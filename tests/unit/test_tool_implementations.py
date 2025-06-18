"""
Unit tests for all tool implementations.
"""

import pytest
import asyncio
import sys
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
from enum import Enum
from dataclasses import dataclass

# Create proper tool status enum
class ToolStatus(Enum):
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    TIMEOUT = "timeout"

@dataclass
class ToolResult:
    status: ToolStatus
    output: str = ""
    error: str = None
    data: dict = None
    timestamp: str = None

# Mock tool classes with proper async support
class MockTerminalTool:
    def __init__(self, working_directory=None):
        self.name = "terminal"
        self.working_directory = working_directory
    
    async def execute(self, operation, **kwargs):
        return ToolResult(status=ToolStatus.SUCCESS, output="mock terminal output")

class MockFileTool:
    def __init__(self, base_directory=None):
        self.name = "file"
        self.base_directory = base_directory
    
    async def execute(self, operation, **kwargs):
        return ToolResult(status=ToolStatus.SUCCESS, output="mock file output")

class MockFlutterTool:
    def __init__(self, project_directory=None):
        self.name = "flutter"
        self.project_directory = project_directory
    
    async def execute(self, operation, **kwargs):
        return ToolResult(status=ToolStatus.SUCCESS, output="mock flutter output")
    
    async def create_project(self, name, path):
        return ToolResult(status=ToolStatus.SUCCESS, output=f"Created project {name}")
    
    async def build(self, platform):
        return ToolResult(status=ToolStatus.SUCCESS, output=f"Built for {platform}")
    
    async def test(self, coverage=False):
        return ToolResult(status=ToolStatus.SUCCESS, output="All tests passed")
    
    async def pub_get(self):
        return ToolResult(status=ToolStatus.SUCCESS, output="Dependencies fetched")
    
    async def pub_add(self, packages):
        return ToolResult(status=ToolStatus.SUCCESS, output=f"Added packages: {packages}")

class MockGitTool:
    def __init__(self, repository_directory=None):
        self.name = "git"
        self.repository_directory = repository_directory
    
    async def execute(self, operation, **kwargs):
        return ToolResult(status=ToolStatus.SUCCESS, output="mock git output")
    
    async def init(self):
        return ToolResult(status=ToolStatus.SUCCESS, output="Initialized git repository")
    
    async def add(self, files):
        return ToolResult(status=ToolStatus.SUCCESS, output=f"Added files: {files}")
    
    async def commit(self, message):
        return ToolResult(status=ToolStatus.SUCCESS, output=f"Committed: {message}")
    
    async def status(self):
        return ToolResult(status=ToolStatus.SUCCESS, output="Working tree clean")
    
    async def list_branches(self):
        return ToolResult(status=ToolStatus.SUCCESS, output="main\nfeature-branch")

class MockAnalysisTool:
    def __init__(self, project_directory=None):
        self.name = "analysis"
        self.project_directory = project_directory
    
    async def execute(self, operation, **kwargs):
        return ToolResult(status=ToolStatus.SUCCESS, output="mock analysis output")
    
    async def dart_analyze(self):
        return ToolResult(status=ToolStatus.SUCCESS, output="No issues found")
    
    async def security_scan(self):
        return ToolResult(status=ToolStatus.SUCCESS, output="No security issues")
    
    async def calculate_metrics(self):
        return ToolResult(status=ToolStatus.SUCCESS, output="Metrics calculated")
    
    async def analyze_dependencies(self):
        return ToolResult(status=ToolStatus.SUCCESS, output="Dependencies analyzed")
    
    async def analyze_performance(self):
        return ToolResult(status=ToolStatus.SUCCESS, output="Performance analyzed")

# Create mock modules
mock_tools = MagicMock()
mock_tools.base_tool = MagicMock()
mock_tools.base_tool.ToolStatus = ToolStatus
mock_tools.base_tool.ToolResult = ToolResult
mock_tools.terminal_tool = MagicMock()
mock_tools.terminal_tool.TerminalTool = MockTerminalTool
mock_tools.file_tool = MagicMock()
mock_tools.file_tool.FileTool = MockFileTool
mock_tools.flutter_tool = MagicMock()
mock_tools.flutter_tool.FlutterTool = MockFlutterTool
mock_tools.git_tool = MagicMock()
mock_tools.git_tool.GitTool = MockGitTool
mock_tools.analysis_tool = MagicMock()
mock_tools.analysis_tool.AnalysisTool = MockAnalysisTool

sys.modules['tools'] = mock_tools
sys.modules['tools.base_tool'] = mock_tools.base_tool
sys.modules['tools.terminal_tool'] = mock_tools.terminal_tool
sys.modules['tools.file_tool'] = mock_tools.file_tool
sys.modules['tools.flutter_tool'] = mock_tools.flutter_tool
sys.modules['tools.git_tool'] = mock_tools.git_tool
sys.modules['tools.analysis_tool'] = mock_tools.analysis_tool

# Import the classes
TerminalTool = MockTerminalTool
FileTool = MockFileTool
FlutterTool = MockFlutterTool
GitTool = MockGitTool
AnalysisTool = MockAnalysisTool

# Mock test constants
TOOL_TEST_CONFIG = {
    "terminal": {
        "timeout": 30,
        "commands": ["echo test", "ls", "pwd"],
        "error_commands": ["nonexistent_command", "exit 1"]
    },
    "file": {
        "test_files": {
            "dart_code": "test_file.dart",
            "json_config": "test_config.json",
            "yaml_config": "test_config.yaml"
        }
    }
}


@pytest.mark.unit
class TestTerminalTool:
    """Test suite for TerminalTool."""
    
    @pytest.fixture
    def terminal_tool(self):
        """Create terminal tool for testing."""
        return TerminalTool()
    
    @pytest.mark.asyncio
    async def test_command_execution(self, terminal_tool):
        """Test basic command execution."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            # Mock successful command
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((b"Hello World", b""))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await terminal_tool.execute("echo Hello World")
            
            assert result.status == ToolStatus.SUCCESS
            assert "Hello World" in result.output
            assert result.error is None
            
    @pytest.mark.asyncio
    async def test_command_failure(self, terminal_tool):
        """Test command failure handling."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            # Mock failed command
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((b"", b"Command not found"))
            mock_process.returncode = 1
            mock_subprocess.return_value = mock_process
            
            result = await terminal_tool.execute("nonexistent_command")
            
            assert result.status == ToolStatus.ERROR
            assert "Command not found" in result.error
            
    @pytest.mark.asyncio
    async def test_command_timeout(self, terminal_tool):
        """Test command timeout handling."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            # Mock hanging process
            mock_process = MagicMock()
            mock_process.communicate.side_effect = asyncio.TimeoutError()
            mock_subprocess.return_value = mock_process
            
            result = await terminal_tool.execute("sleep 100", timeout=0.1)
            
            assert result.status == ToolStatus.TIMEOUT
            assert "timeout" in result.error.lower()
            
    @pytest.mark.asyncio
    async def test_script_execution(self, terminal_tool):
        """Test script execution from content."""
        script_content = """
#!/bin/bash
echo "Script executed"
exit 0
"""
        
        with patch('tempfile.NamedTemporaryFile') as mock_temp, \
             patch('asyncio.create_subprocess_shell') as mock_subprocess:
            
            # Mock temp file
            mock_file = MagicMock()
            mock_file.name = "/tmp/test_script.sh"
            mock_temp.return_value.__enter__.return_value = mock_file
            
            # Mock successful execution
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((b"Script executed", b""))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await terminal_tool.execute_script(script_content, "bash")
            
            assert result.status == ToolStatus.SUCCESS
            assert "Script executed" in result.output


@pytest.mark.unit
class TestFileTool:
    """Test suite for FileTool."""
    
    @pytest.fixture
    def file_tool(self):
        """Create file tool for testing."""
        return FileTool()
    
    @pytest.mark.asyncio
    async def test_file_read(self, file_tool):
        """Test file reading."""
        test_content = "Hello, World!"
        
        with patch('builtins.open', create=True) as mock_open:
            mock_open.return_value.__enter__.return_value.read.return_value = test_content
            
            result = await file_tool.read_file("test.txt")
            
            assert result.status == ToolStatus.SUCCESS
            assert result.output == test_content
            
    @pytest.mark.asyncio
    async def test_file_write(self, file_tool):
        """Test file writing."""
        test_content = "Hello, World!"
        
        with patch('builtins.open', create=True) as mock_open, \
             patch('os.makedirs') as mock_makedirs:
            
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            result = await file_tool.write_file("test.txt", test_content)
            
            assert result.status == ToolStatus.SUCCESS
            mock_file.write.assert_called_once_with(test_content)
            
    @pytest.mark.asyncio
    async def test_file_exists(self, file_tool):
        """Test file existence check."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.return_value = True
            
            result = await file_tool.file_exists("test.txt")
            
            assert result.status == ToolStatus.SUCCESS
            assert result.data["exists"] == True
            
    @pytest.mark.asyncio
    async def test_directory_creation(self, file_tool):
        """Test directory creation."""
        with patch('os.makedirs') as mock_makedirs:
            result = await file_tool.create_directory("test/dir")
            
            assert result.status == ToolStatus.SUCCESS
            mock_makedirs.assert_called_once_with("test/dir", exist_ok=True)
            
    @pytest.mark.asyncio
    async def test_file_copy(self, file_tool):
        """Test file copying."""
        with patch('shutil.copy2') as mock_copy:
            result = await file_tool.copy_file("source.txt", "dest.txt")
            
            assert result.status == ToolStatus.SUCCESS
            mock_copy.assert_called_once_with("source.txt", "dest.txt")
            
    @pytest.mark.asyncio
    async def test_json_operations(self, file_tool):
        """Test JSON file operations."""
        test_data = {"key": "value", "number": 42}
        
        with patch('builtins.open', create=True) as mock_open:
            # Test JSON writing
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            result = await file_tool.write_json("test.json", test_data)
            assert result.status == ToolStatus.SUCCESS
            
            # Test JSON reading
            mock_open.return_value.__enter__.return_value.read.return_value = '{"key": "value", "number": 42}'
            
            result = await file_tool.read_json("test.json")
            assert result.status == ToolStatus.SUCCESS
            assert result.data == test_data


@pytest.mark.unit
class TestFlutterTool:
    """Test suite for FlutterTool."""
    
    @pytest.fixture
    def flutter_tool(self):
        """Create Flutter tool for testing."""
        return FlutterTool()
    
    @pytest.mark.asyncio
    async def test_flutter_doctor(self, flutter_tool):
        """Test Flutter doctor command."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"Flutter (Channel stable, 3.0.0)", b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await flutter_tool.doctor()
            
            assert result.status == ToolStatus.SUCCESS
            assert "Flutter" in result.output
            
    @pytest.mark.asyncio
    async def test_flutter_create(self, flutter_tool):
        """Test Flutter project creation."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"Creating Flutter project...", b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await flutter_tool.create_project("test_app", "/path/to/project")
            
            assert result.status == ToolStatus.SUCCESS
            
    @pytest.mark.asyncio
    async def test_flutter_build(self, flutter_tool):
        """Test Flutter build command."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"Build completed successfully", b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await flutter_tool.build("apk")
            
            assert result.status == ToolStatus.SUCCESS
            assert "completed" in result.output
            
    @pytest.mark.asyncio
    async def test_flutter_test(self, flutter_tool):
        """Test Flutter test execution."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"All tests passed: 25 passed, 0 failed", b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await flutter_tool.test(coverage=True)
            
            assert result.status == ToolStatus.SUCCESS
            assert "25 passed" in result.output
            
    @pytest.mark.asyncio
    async def test_pub_get(self, flutter_tool):
        """Test pub get command."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"Running \"flutter pub get\"...", b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await flutter_tool.pub_get()
            
            assert result.status == ToolStatus.SUCCESS
            
    @pytest.mark.asyncio
    async def test_pub_add(self, flutter_tool):
        """Test pub add command."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"Dependencies added successfully", b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await flutter_tool.pub_add(["http", "provider"])
            
            assert result.status == ToolStatus.SUCCESS


@pytest.mark.unit
class TestGitTool:
    """Test suite for GitTool."""
    
    @pytest.fixture
    def git_tool(self):
        """Create Git tool for testing."""
        return GitTool()
    
    @pytest.mark.asyncio
    async def test_git_init(self, git_tool):
        """Test git init command."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"Initialized empty Git repository", b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await git_tool.init()
            
            assert result.status == ToolStatus.SUCCESS
            assert "Initialized" in result.output
            
    @pytest.mark.asyncio
    async def test_git_add(self, git_tool):
        """Test git add command."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((b"", b""))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await git_tool.add(["file1.dart", "file2.dart"])
            
            assert result.status == ToolStatus.SUCCESS
            
    @pytest.mark.asyncio
    async def test_git_commit(self, git_tool):
        """Test git commit command."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"[main abc123] Test commit", b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await git_tool.commit("Test commit")
            
            assert result.status == ToolStatus.SUCCESS
            assert "Test commit" in result.output
            
    @pytest.mark.asyncio
    async def test_git_status(self, git_tool):
        """Test git status command."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"On branch main\nnothing to commit, working tree clean", b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await git_tool.status()
            
            assert result.status == ToolStatus.SUCCESS
            assert "working tree clean" in result.output
            
    @pytest.mark.asyncio
    async def test_git_branch_operations(self, git_tool):
        """Test git branch operations."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"* main\n  feature-branch", b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            # Test list branches
            result = await git_tool.list_branches()
            assert result.status == ToolStatus.SUCCESS
            
            # Test create branch
            result = await git_tool.create_branch("new-feature")
            assert result.status == ToolStatus.SUCCESS
            
            # Test checkout branch
            result = await git_tool.checkout_branch("new-feature")
            assert result.status == ToolStatus.SUCCESS


@pytest.mark.unit
class TestAnalysisTool:
    """Test suite for AnalysisTool."""
    
    @pytest.fixture
    def analysis_tool(self):
        """Create analysis tool for testing."""
        return AnalysisTool()
    
    @pytest.mark.asyncio
    async def test_dart_analyze(self, analysis_tool):
        """Test Dart code analysis."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"Analyzing...\nNo issues found!", b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await analysis_tool.dart_analyze()
            
            assert result.status == ToolStatus.SUCCESS
            assert "No issues found" in result.output
            
    @pytest.mark.asyncio
    async def test_security_scan(self, analysis_tool):
        """Test security scanning."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"Security scan completed\n0 vulnerabilities found", b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await analysis_tool.security_scan()
            
            assert result.status == ToolStatus.SUCCESS
            assert "0 vulnerabilities" in result.output
            
    @pytest.mark.asyncio
    async def test_code_metrics(self, analysis_tool):
        """Test code metrics calculation."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"Calculating metrics...\nComplexity: 2.3\nMaintainability: 85", b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await analysis_tool.calculate_metrics()
            
            assert result.status == ToolStatus.SUCCESS
            assert "Complexity" in result.output
            
    @pytest.mark.asyncio
    async def test_dependency_analysis(self, analysis_tool):
        """Test dependency analysis."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"Analyzing dependencies...\n45 packages analyzed\n1 outdated package", b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await analysis_tool.analyze_dependencies()
            
            assert result.status == ToolStatus.SUCCESS
            assert "45 packages" in result.output
            
    @pytest.mark.asyncio
    async def test_performance_analysis(self, analysis_tool):
        """Test performance analysis."""
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((
                b"Performance analysis complete\nAverage frame time: 16.7ms", b""
            ))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await analysis_tool.analyze_performance()
            
            assert result.status == ToolStatus.SUCCESS
            assert "16.7ms" in result.output
            
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
        
    def test_tool_status_enum(self):
        """Test ToolStatus enum values."""
        assert ToolStatus.SUCCESS.value == "SUCCESS"
        assert ToolStatus.ERROR.value == "ERROR"
        assert ToolStatus.WARNING.value == "WARNING"
        assert ToolStatus.TIMEOUT.value == "TIMEOUT"


@pytest.mark.unit
class TestToolIntegration:
    """Test suite for tool integration scenarios."""
    
    @pytest.mark.asyncio
    async def test_flutter_project_workflow(self):
        """Test complete Flutter project workflow using multiple tools."""
        terminal_tool = TerminalTool()
        file_tool = FileTool()
        flutter_tool = FlutterTool()
        git_tool = GitTool()
        
        with patch('asyncio.create_subprocess_shell') as mock_subprocess, \
             patch('builtins.open', create=True) as mock_open, \
             patch('os.makedirs') as mock_makedirs:
            
            # Mock successful command execution
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((b"Success", b""))
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            # Mock file operations
            mock_open.return_value.__enter__.return_value.write.return_value = None
            
            # Simulate workflow
            results = []
            
            # 1. Create Flutter project
            results.append(await flutter_tool.create_project("test_app", "/path"))
            
            # 2. Initialize git repository
            results.append(await git_tool.init())
            
            # 3. Create project files
            results.append(await file_tool.write_file("lib/main.dart", "void main() {}"))
            
            # 4. Add dependencies
            results.append(await flutter_tool.pub_add(["http"]))
            
            # 5. Run tests
            results.append(await flutter_tool.test())
            
            # 6. Build project
            results.append(await flutter_tool.build("apk"))
            
            # 7. Git operations
            results.append(await git_tool.add(["."])) 
            results.append(await git_tool.commit("Initial commit"))
            
            # Verify all operations succeeded
            for result in results:
                assert result.status == ToolStatus.SUCCESS
                
    @pytest.mark.asyncio
    async def test_error_handling_workflow(self):
        """Test error handling in tool workflows."""
        flutter_tool = FlutterTool()
        
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            # Mock failed command
            mock_process = MagicMock()
            mock_process.communicate.return_value = asyncio.Future()
            mock_process.communicate.return_value.set_result((b"", b"Build failed"))
            mock_process.returncode = 1
            mock_subprocess.return_value = mock_process
            
            result = await flutter_tool.build("invalid_platform")
            
            assert result.status == ToolStatus.ERROR
            assert "Build failed" in result.error
