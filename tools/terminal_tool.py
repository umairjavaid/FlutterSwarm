"""
Terminal tool for executing shell commands.
"""

import asyncio
import os
import time
from typing import Dict, Any, Optional, List
from .base_tool import BaseTool, ToolResult, ToolStatus
from utils.function_logger import track_function

class TerminalTool(BaseTool):
    """
    Tool for executing shell commands in a terminal.
    """
    
    def __init__(self, working_directory: Optional[str] = None):
        super().__init__(
            name="terminal",
            description="Execute shell commands in terminal",
            timeout=60
        )
        self.working_directory = working_directory or os.getcwd()
    
    @track_function(log_args=True, log_return=True)
    async def execute(self, command: str = None, **kwargs) -> ToolResult:
        """
        Execute a shell command or handle specific operations.
        
        Args:
            command: Shell command to execute
            operation: Specific operation (check_deps, install_flutter, etc.)
            working_dir: Optional working directory (overrides default)
            env: Optional environment variables
            capture_output: Whether to capture stdout/stderr (default: True)
            shell: Whether to run in shell mode (default: True)
            timeout: Override default timeout for this command
            
        Returns:
            ToolResult with command output
        """
        # Handle operation-based calls
        operation = kwargs.get("operation")
        if operation:
            return await self._handle_operation(operation, **kwargs)
        
        if not command:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="No command or operation specified"
            )
        
        self.validate_parameters(["command"], command=command, **kwargs)
        
        working_dir = kwargs.get("working_dir", self.working_directory)
        env = kwargs.get("env", None)
        capture_output = kwargs.get("capture_output", True)
        shell = kwargs.get("shell", True)
        command_timeout = kwargs.get("timeout", self.timeout)
        
        start_time = time.time()
        
        try:
            # Create subprocess with timeout support
            if capture_output:
                process = await asyncio.wait_for(
                    asyncio.create_subprocess_shell(
                        command,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                        cwd=working_dir,
                        env=env,
                        shell=shell
                    ),
                    timeout=command_timeout
                )
                
                stdout, stderr = await process.communicate()
                stdout_str = stdout.decode('utf-8') if stdout else ""
                stderr_str = stderr.decode('utf-8') if stderr else ""
                
                execution_time = time.time() - start_time
                
                if process.returncode == 0:
                    return ToolResult(
                        status=ToolStatus.SUCCESS,
                        output=stdout_str,
                        error=stderr_str if stderr_str else None,
                        data={
                            "return_code": process.returncode,
                            "command": command,
                            "working_dir": working_dir
                        },
                        execution_time=execution_time
                    )
                else:
                    return ToolResult(
                        status=ToolStatus.ERROR,
                        output=stdout_str,
                        error=stderr_str,
                        data={
                            "return_code": process.returncode,
                            "command": command,
                            "working_dir": working_dir
                        },
                        execution_time=execution_time
                    )
            else:
                # Fire and forget mode
                process = await asyncio.create_subprocess_shell(
                    command,
                    cwd=working_dir,
                    env=env,
                    shell=shell
                )
                
                await process.wait()
                execution_time = time.time() - start_time
                
                return ToolResult(
                    status=ToolStatus.SUCCESS if process.returncode == 0 else ToolStatus.ERROR,
                    output=f"Command executed with return code: {process.returncode}",
                    error=None,
                    data={
                        "return_code": process.returncode,
                        "command": command,
                        "working_dir": working_dir
                    },
                    execution_time=execution_time
                )
                
        except asyncio.TimeoutError:
            execution_time = time.time() - start_time
            return ToolResult(
                status=ToolStatus.TIMEOUT,
                output="",
                error=f"Command timed out after {command_timeout} seconds",
                data={
                    "command": command,
                    "working_dir": working_dir
                },
                execution_time=execution_time
            )
        except Exception as e:
            execution_time = time.time() - start_time
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Failed to execute command: {str(e)}",
                data={
                    "command": command,
                    "working_dir": working_dir
                },
                execution_time=execution_time
            )
    
    async def _handle_operation(self, operation: str, **kwargs) -> ToolResult:
        """Handle specific operations."""
        if operation == "check_dependencies":
            return await self._check_dependencies(**kwargs)
        elif operation == "health_check":
            return await self._health_check(**kwargs)
        elif operation == "cleanup":
            return await self._cleanup(**kwargs)
        else:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Unknown operation: {operation}"
            )
    
    async def _check_dependencies(self, **kwargs) -> ToolResult:
        """Check system dependencies."""
        dependencies = ["flutter", "dart", "git"]
        results = {}
        
        for dep in dependencies:
            result = await self.execute(f"which {dep}")
            if result.status == ToolStatus.SUCCESS:
                version_result = await self.execute(f"{dep} --version")
                results[dep] = {
                    "installed": True,
                    "path": result.output.strip() if result.output else "",
                    "version": version_result.output.split('\n')[0] if version_result.status == ToolStatus.SUCCESS and version_result.output else "unknown"
                }
            else:
                results[dep] = {"installed": False}
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Dependency check completed for {len(dependencies)} tools",
            data={"dependencies": results}
        )
    
    async def _health_check(self, **kwargs) -> ToolResult:
        """Perform system health check."""
        checks = {
            "flutter_doctor": "flutter doctor",
            "dart_version": "dart --version",
            "git_status": "git --version",
            "disk_space": "df -h .",
            "memory_usage": "free -h"
        }
        
        health_data = {}
        overall_status = ToolStatus.SUCCESS
        
        for check_name, command in checks.items():
            result = await self.execute(command)
            health_data[check_name] = {
                "status": result.status.value,
                "output": result.output,
                "error": result.error
            }
            
            if result.status != ToolStatus.SUCCESS:
                overall_status = ToolStatus.WARNING
        
        return ToolResult(
            status=overall_status,
            output="Health check completed",
            data={"health_checks": health_data}
        )
    
    async def _cleanup(self, **kwargs) -> ToolResult:
        """Clean up temporary files and caches."""
        cleanup_commands = [
            "flutter clean",
            "flutter pub cache clean",
            "rm -rf build/",
            "rm -rf .dart_tool/",
            "find . -name '*.log' -delete"
        ]
        
        results = []
        for cmd in cleanup_commands:
            result = await self.execute(cmd)
            results.append({
                "command": cmd,
                "success": result.status == ToolStatus.SUCCESS,
                "output": result.output
            })
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output="Cleanup completed",
            data={"cleanup_results": results}
        )

    async def execute_script(self, script_content: str, script_type: str = "bash") -> ToolResult:
        """
        Execute a script from content.
        
        Args:
            script_content: Content of the script
            script_type: Type of script (bash, python, etc.)
            
        Returns:
            ToolResult with script output
        """
        import tempfile
        
        # Create temporary script file
        script_extension = {
            "bash": ".sh",
            "python": ".py",
            "dart": ".dart",
            "yaml": ".yaml"
        }.get(script_type, ".sh")
        
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix=script_extension, 
            delete=False
        ) as temp_file:
            temp_file.write(script_content)
            temp_file_path = temp_file.name
        
        try:
            # Make script executable
            os.chmod(temp_file_path, 0o755)
            
            # Execute script
            if script_type == "python":
                command = f"python {temp_file_path}"
            elif script_type == "dart":
                command = f"dart run {temp_file_path}"
            else:
                command = f"bash {temp_file_path}"
            
            result = await self.execute(command)
            
            # Clean up
            os.unlink(temp_file_path)
            
            return result
            
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
            
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Failed to execute script: {str(e)}"
            )
    
    async def check_command_exists(self, command: str) -> bool:
        """Check if a command exists in the system."""
        result = await self.execute(f"which {command}")
        return result.status == ToolStatus.SUCCESS
    
    async def get_environment_info(self) -> ToolResult:
        """Get system environment information."""
        commands = {
            "os": "uname -a",
            "flutter_version": "flutter --version",
            "dart_version": "dart --version",
            "git_version": "git --version",
            "python_version": "python --version",
            "node_version": "node --version"
        }
        
        env_info = {}
        for key, cmd in commands.items():
            result = await self.execute(cmd)
            env_info[key] = {
                "available": result.status == ToolStatus.SUCCESS,
                "output": result.output.strip() if result.output else "",
                "error": result.error
            }
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Environment info collected for {len(env_info)} tools",
            data=env_info
        )

    async def run_flutter_command(self, flutter_cmd: str, **kwargs) -> ToolResult:
        """Run a Flutter-specific command."""
        full_command = f"flutter {flutter_cmd}"
        return await self.execute(full_command, **kwargs)
    
    async def run_dart_command(self, dart_cmd: str, **kwargs) -> ToolResult:
        """Run a Dart-specific command."""
        full_command = f"dart {dart_cmd}"
        return await self.execute(full_command, **kwargs)
    
    async def run_git_command(self, git_cmd: str, **kwargs) -> ToolResult:
        """Run a Git-specific command."""
        full_command = f"git {git_cmd}"
        return await self.execute(full_command, **kwargs)
