"""
Tool manager for organizing and executing tools for FlutterSwarm agents.
"""

import asyncio
import os
from typing import Dict, List, Any, Optional, Type

# Import comprehensive logging support
from utils.function_logger import track_function, track_tool
from monitoring.agent_logger import agent_logger

from .base_tool import BaseTool, ToolResult, ToolStatus
from .terminal_tool import TerminalTool
from .file_tool import FileTool
from .flutter_tool import FlutterTool
from .git_tool import GitTool
from .analysis_tool import AnalysisTool
from .package_manager_tool import PackageManagerTool
from .testing_tool import TestingTool
from .security_tool import SecurityTool
from .code_generation_tool import CodeGenerationTool

class ToolManager:
    """
    Manages tools for FlutterSwarm agents.
    Provides a centralized way to register, discover, and execute tools.
    """
    
    @track_function(agent_id="system", log_args=True, log_return=False)
    def __init__(self, project_directory: Optional[str] = None):
        self.project_directory = project_directory
        self.tools: Dict[str, BaseTool] = {}
        self._initialize_default_tools()
        
        # Log tool manager initialization
        agent_logger.log_project_event("system", "tool_manager_init", 
                                     f"ToolManager initialized with {len(self.tools)} tools")
    
    @track_function(agent_id="system", log_args=False, log_return=False)
    def _initialize_default_tools(self):
        """Initialize default tools available to all agents."""
        self.tools = {
            "terminal": TerminalTool(self.project_directory),
            "file": FileTool(self.project_directory),
            "flutter": FlutterTool(self.project_directory),
            "git": GitTool(self.project_directory),
            "analysis": AnalysisTool(self.project_directory),
            "package_manager": PackageManagerTool(self.project_directory),
            "testing": TestingTool(self.project_directory),
            "security": SecurityTool(self.project_directory),
            "code_generation": CodeGenerationTool(self.project_directory)
        }
    
    def register_tool(self, tool: BaseTool, name: Optional[str] = None):
        """Register a new tool."""
        tool_name = name or tool.name
        self.tools[tool_name] = tool
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all available tool names."""
        return list(self.tools.keys())
    
    def get_tool_info(self, name: str) -> Optional[Dict[str, Any]]:
        """Get information about a tool."""
        tool = self.tools.get(name)
        if tool:
            return {
                "name": tool.name,
                "description": tool.description,
                "timeout": tool.timeout,
                "is_async": tool.is_async
            }
        return None
    
    @track_function(agent_id="system", log_args=True, log_return=True)
    async def execute_tool(self, tool_name: str, operation: str = None, **kwargs) -> ToolResult:
        """
        Execute a tool operation with comprehensive logging.
        
        Args:
            tool_name: Name of the tool to execute
            operation: Operation to perform (tool-specific)
            **kwargs: Additional parameters for the tool
            
        Returns:
            ToolResult with execution outcome
        """
        tool = self.tools.get(tool_name)
        
        if not tool:
            error_msg = f"Tool '{tool_name}' not found"
            agent_logger.log_tool_usage("system", tool_name, operation or "unknown", "error", 
                                       error=error_msg)
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=error_msg
            )
        
        import time
        start_time = time.time()
        
        try:
            # Log tool usage start
            agent_logger.log_tool_usage("system", tool_name, operation or "execute", "started",
                                       input_data=kwargs)
            
            if operation:
                result = await tool.execute_with_timeout(operation=operation, **kwargs)
            else:
                result = await tool.execute_with_timeout(**kwargs)
            
            # Log tool usage completion
            execution_time = time.time() - start_time
            agent_logger.log_tool_usage("system", tool_name, operation or "execute", 
                                       result.status.value, execution_time=execution_time,
                                       input_data=kwargs, output_data={"output": result.output})
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            agent_logger.log_tool_usage("system", tool_name, operation or "execute", "error",
                                       execution_time=execution_time, input_data=kwargs, 
                                       error=error_msg)
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Failed to execute tool '{tool_name}': {str(e)}"
            )
    
    async def execute_command(self, command: str, working_dir: Optional[str] = None, **kwargs) -> ToolResult:
        """
        Execute a shell command using the terminal tool.
        
        Args:
            command: Command to execute
            working_dir: Working directory (optional)
            **kwargs: Additional terminal parameters
            
        Returns:
            ToolResult with command output
        """
        return await self.execute_tool(
            "terminal", 
            command=command, 
            working_dir=working_dir,
            **kwargs
        )
    
    async def read_file(self, file_path: str, **kwargs) -> ToolResult:
        """Read a file using the file tool."""
        return await self.execute_tool("file", "read", file_path=file_path, **kwargs)
    
    async def write_file(self, file_path: str, content: str, **kwargs) -> ToolResult:
        """Write a file using the file tool."""
        return await self.execute_tool("file", "write", file_path=file_path, content=content, **kwargs)
    
    async def flutter_build(self, platform: str = "apk", **kwargs) -> ToolResult:
        """Build Flutter project - no code generation, only infrastructure."""
        return await self.execute_tool("flutter", "build", platform=platform, **kwargs)
    
    async def flutter_test(self, **kwargs) -> ToolResult:
        """Run Flutter tests - no test generation, only execution."""
        return await self.execute_tool("flutter", "test", **kwargs)
    
    async def git_commit(self, message: str, **kwargs) -> ToolResult:
        """Commit changes using git."""
        return await self.execute_tool("git", "commit", message=message, **kwargs)
    
    async def analyze_code(self, **kwargs) -> ToolResult:
        """Analyze code quality - no code generation."""
        return await self.execute_tool("analysis", "dart_analyze", **kwargs)
    
    async def security_scan(self, **kwargs) -> ToolResult:
        """Perform security scan - no code generation."""
        return await self.execute_tool("security", "scan", **kwargs)
    
    async def generate_code(self, component_type: str, name: str, **kwargs) -> ToolResult:
        """Generate code component."""
        return await self.execute_tool("code_generation", "generate", 
                                     component_type=component_type, name=name, **kwargs)
    
    async def run_tests(self, test_type: str = "all", **kwargs) -> ToolResult:
        """Run tests."""
        return await self.execute_tool("testing", "run", test_type=test_type, **kwargs)
    
    async def add_package(self, package_name: str, project_path: str = None, **kwargs) -> ToolResult:
        """Add package - infrastructure only, no code generation."""
        try:
            # Use flutter tool to add package
            flutter_tool = self.get_tool("flutter")
            if not flutter_tool:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error="Flutter tool not available"
                )
            
            # Determine the correct Flutter project directory
            if project_path:
                flutter_project_dir = project_path
            else:
                # Check if we're in a Flutter project directory
                current_dir = os.getcwd()
                flutter_projects_dir = None
                
                # Look for flutter_projects directory
                if "flutter_projects" in current_dir:
                    flutter_projects_dir = current_dir
                else:
                    # Look for flutter_projects in parent directories
                    parent_dir = os.path.dirname(current_dir)
                    potential_flutter_dir = os.path.join(parent_dir, "flutter_projects")
                    if os.path.exists(potential_flutter_dir):
                        flutter_projects_dir = potential_flutter_dir
                    else:
                        # Create flutter_projects directory if it doesn't exist
                        flutter_projects_dir = os.path.join(current_dir, "flutter_projects")
                        os.makedirs(flutter_projects_dir, exist_ok=True)
                
                flutter_project_dir = flutter_projects_dir
            
            # Verify that the target directory contains a Flutter project
            pubspec_path = os.path.join(flutter_project_dir, "pubspec.yaml")
            if not os.path.exists(pubspec_path):
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error=f"No Flutter project found at {flutter_project_dir}. Missing pubspec.yaml"
                )
            
            # Execute pub add in the Flutter project directory
            result = await flutter_tool.execute("pub_add", packages=[package_name], 
                                              working_dir=flutter_project_dir, **kwargs)
            
            if result.status == ToolStatus.SUCCESS:
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    output=f"Successfully added package: {package_name}",
                    data={"package": package_name, "result": result.data}
                )
            else:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output=result.output,
                    error=f"Failed to add package {package_name}: {result.error}"
                )
        
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Error adding package {package_name}: {str(e)}"
            )
    
    async def check_dependencies(self, **kwargs) -> ToolResult:
        """Check dependencies - analysis only, no code generation."""
        try:
            # Read pubspec.yaml
            file_tool = self.get_tool("file")
            if not file_tool:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error="File tool not available"
                )
            
            pubspec_result = await file_tool.execute("read", file_path="pubspec.yaml")
            if pubspec_result.status != ToolStatus.SUCCESS:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error=f"Could not read pubspec.yaml: {pubspec_result.error}"
                )
            
            # Parse dependencies
            try:
                import yaml
                pubspec_data = yaml.safe_load(pubspec_result.output)
                dependencies = pubspec_data.get("dependencies", {})
                dev_dependencies = pubspec_data.get("dev_dependencies", {})
            except Exception as e:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error=f"Failed to parse pubspec.yaml: {str(e)}"
                )
            
            # Check for outdated packages
            flutter_tool = self.get_tool("flutter")
            outdated_result = None
            if flutter_tool:
                outdated_result = await flutter_tool.execute("pub_outdated")
            
            # Analyze dependencies for security and compatibility
            analysis_tool = self.get_tool("analysis")
            analysis_result = None
            if analysis_tool:
                analysis_result = await analysis_tool.execute(
                    "analyze_dependencies",
                    dependencies=dependencies,
                    dev_dependencies=dev_dependencies
                )
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output="Dependencies checked successfully",
                data={
                    "dependencies": dependencies,
                    "dev_dependencies": dev_dependencies,
                    "dependency_count": len(dependencies),
                    "dev_dependency_count": len(dev_dependencies),
                    "outdated": outdated_result.output if outdated_result else "Unable to check",
                    "analysis": analysis_result.data if analysis_result and analysis_result.status == ToolStatus.SUCCESS else {},
                    "status": "healthy"
                }
            )
        
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Error checking dependencies: {str(e)}"
            )
    
    def get_tools_for_agent(self, agent_type: str) -> List[str]:
        """
        Get recommended tools for a specific agent type.
        
        Args:
            agent_type: Type of agent (e.g., 'implementation', 'testing', 'security')
            
        Returns:
            List of recommended tool names
        """
        tool_recommendations = {
            "implementation": ["terminal", "file", "flutter", "git", "analysis", "package_manager", "code_generation"],
            "testing": ["terminal", "file", "flutter", "analysis", "testing", "package_manager"],
            "security": ["terminal", "file", "analysis", "git", "security", "package_manager"],
            "architecture": ["terminal", "file", "analysis", "code_generation"],
            "devops": ["terminal", "file", "flutter", "git", "package_manager"],
            "documentation": ["terminal", "file", "git"],
            "performance": ["terminal", "file", "flutter", "analysis", "testing"],
            "quality_assurance": ["terminal", "file", "flutter", "analysis", "git", "testing", "security"],
            "orchestrator": ["terminal", "file", "flutter", "git", "analysis", "package_manager", "testing", "security", "code_generation"]
        }
        
        return tool_recommendations.get(agent_type, list(self.tools.keys()))
    
    async def batch_execute(self, operations: List[Dict[str, Any]]) -> List[ToolResult]:
        """
        Execute multiple tool operations in batch.
        
        Args:
            operations: List of operation dictionaries with 'tool', 'operation', and params
            
        Returns:
            List of ToolResults
        """
        results = []
        
        for op in operations:
            tool_name = op.get("tool")
            operation = op.get("operation")
            params = {k: v for k, v in op.items() if k not in ["tool", "operation"]}
            
            if tool_name:
                result = await self.execute_tool(tool_name, operation, **params)
                results.append(result)
            else:
                results.append(ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error="No tool specified in operation"
                ))
        
        return results
    
    async def parallel_execute(self, operations: List[Dict[str, Any]]) -> List[ToolResult]:
        """
        Execute multiple tool operations in parallel.
        
        Args:
            operations: List of operation dictionaries
            
        Returns:
            List of ToolResults in the same order as operations
        """
        tasks = []
        
        for op in operations:
            tool_name = op.get("tool")
            operation = op.get("operation")
            params = {k: v for k, v in op.items() if k not in ["tool", "operation"]}
            
            if tool_name:
                task = self.execute_tool(tool_name, operation, **params)
                tasks.append(task)
            else:
                # Create a failed result for invalid operations
                async def failed_op():
                    return ToolResult(
                        status=ToolStatus.ERROR,
                        output="",
                        error="No tool specified in operation"
                    )
                tasks.append(failed_op())
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Convert exceptions to error results
        final_results = []
        for result in results:
            if isinstance(result, Exception):
                final_results.append(ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error=f"Parallel execution failed: {str(result)}"
                ))
            else:
                final_results.append(result)
        
        return final_results
    
    def create_agent_toolbox(self, agent_type: str) -> "AgentToolbox":
        """Create a specialized toolbox for an agent type."""
        return AgentToolbox(self, agent_type)

class AgentToolbox:
    """
    Specialized toolbox for a specific agent type.
    Provides convenient methods for common operations.
    """
    
    def __init__(self, tool_manager: ToolManager, agent_type: str):
        self.tool_manager = tool_manager
        self.agent_type = agent_type
        self.available_tools = tool_manager.get_tools_for_agent(agent_type)
    
    async def execute(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool if it's available for this agent."""
        if tool_name not in self.available_tools:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Tool '{tool_name}' not available for {self.agent_type} agent"
            )
        
        return await self.tool_manager.execute_tool(tool_name, **kwargs)
    
    async def run_command(self, command: str, **kwargs) -> ToolResult:
        """Run a terminal command."""
        return await self.execute("terminal", command=command, **kwargs)
    
    async def read_file(self, file_path: str, **kwargs) -> ToolResult:
        """Read a file."""
        return await self.execute("file", operation="read", file_path=file_path, **kwargs)
    
    async def write_file(self, file_path: str, content: str, **kwargs) -> ToolResult:
        """Write a file."""
        return await self.execute("file", operation="write", file_path=file_path, content=content, **kwargs)
    
    def list_available_tools(self) -> List[str]:
        """List tools available for this agent."""
        return self.available_tools.copy()
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a tool if it's available."""
        if tool_name in self.available_tools:
            return self.tool_manager.get_tool_info(tool_name)
        return None
