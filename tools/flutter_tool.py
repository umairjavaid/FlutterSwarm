"""
Flutter-specific tool for Flutter development operations.
"""

import os
import json
import time
from typing import Dict, Any, Optional, List
from .base_tool import BaseTool, ToolResult, ToolStatus
from .terminal_tool import TerminalTool

class FlutterTool(BaseTool):
    """
    Tool for Flutter-specific development operations.
    """
    
    def __init__(self, project_directory: Optional[str] = None):
        super().__init__(
            name="flutter",
            description="Perform Flutter development operations",
            timeout=300  # Flutter commands can take longer
        )
        self.project_directory = project_directory or os.getcwd()
        self.terminal = TerminalTool(self.project_directory)
    
    async def execute(self, operation: str, **kwargs) -> ToolResult:
        """
        Execute Flutter operation.
        
        Args:
            operation: Type of operation (create, build, test, analyze, etc.)
            **kwargs: Operation-specific parameters
            
        Returns:
            ToolResult with operation outcome
        """
        self.validate_parameters(["operation"], operation=operation, **kwargs)
        
        start_time = time.time()
        
        try:
            if operation == "create":
                return await self._create_project(**kwargs)
            elif operation == "build":
                return await self._build_project(**kwargs)
            elif operation == "test":
                return await self._run_tests(**kwargs)
            elif operation == "analyze":
                return await self._analyze_code(**kwargs)
            elif operation == "format":
                return await self._format_code(**kwargs)
            elif operation == "pub_get":
                return await self._pub_get(**kwargs)
            elif operation == "pub_add":
                return await self._pub_add(**kwargs)
            elif operation == "clean":
                return await self._clean_project(**kwargs)
            elif operation == "doctor":
                return await self._flutter_doctor(**kwargs)
            elif operation == "devices":
                return await self._list_devices(**kwargs)
            elif operation == "run":
                return await self._run_app(**kwargs)
            elif operation == "generate":
                return await self._generate_code(**kwargs)
            else:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output="",
                    error=f"Unknown Flutter operation: {operation}",
                    execution_time=time.time() - start_time
                )
                
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Flutter operation '{operation}' failed: {str(e)}",
                execution_time=time.time() - start_time
            )
    
    async def _create_project(self, project_name: str, template: str = "app", 
                             org: str = "com.example", **kwargs) -> ToolResult:
        """Create a new Flutter project."""
        command = f"flutter create --org {org} --template {template} {project_name}"
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            project_path = os.path.join(self.project_directory, project_name)
            result.data = {
                "project_name": project_name,
                "project_path": project_path,
                "template": template,
                "organization": org
            }
        
        return result
    
    async def _build_project(self, platform: str = "apk", mode: str = "debug", **kwargs) -> ToolResult:
        """Build Flutter project for specified platform."""
        valid_platforms = ["apk", "appbundle", "ios", "web", "windows", "macos", "linux"]
        valid_modes = ["debug", "profile", "release"]
        
        if platform not in valid_platforms:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Invalid platform '{platform}'. Valid platforms: {valid_platforms}"
            )
        
        if mode not in valid_modes:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Invalid mode '{mode}'. Valid modes: {valid_modes}"
            )
        
        command = f"flutter build {platform}"
        if mode != "debug":
            command += f" --{mode}"
        
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            result.data = {
                "platform": platform,
                "mode": mode,
                "build_command": command
            }
        
        return result
    
    async def _run_tests(self, test_file: Optional[str] = None, coverage: bool = False, **kwargs) -> ToolResult:
        """Run Flutter tests."""
        command = "flutter test"
        
        if test_file:
            command += f" {test_file}"
        
        if coverage:
            command += " --coverage"
        
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS and coverage:
            # Try to read coverage information
            coverage_file = os.path.join(self.project_directory, "coverage", "lcov.info")
            if os.path.exists(coverage_file):
                result.data = {
                    "test_file": test_file,
                    "coverage_enabled": coverage,
                    "coverage_file": coverage_file
                }
        
        return result
    
    async def _analyze_code(self, **kwargs) -> ToolResult:
        """Analyze Dart code for issues."""
        command = "flutter analyze"
        result = await self.terminal.execute(command)
        
        # Parse analysis results
        if result.status == ToolStatus.SUCCESS:
            issues = self._parse_analysis_output(result.output)
            result.data = {
                "issues_found": len(issues),
                "issues": issues,
                "analysis_output": result.output  # Include full output for debugging
            }
        elif result.status == ToolStatus.ERROR:
            # Even if analyze fails, try to parse issues from error output
            issues = self._parse_analysis_output(result.output)
            result.data = {
                "issues_found": len(issues),
                "issues": issues,
                "analysis_output": result.output,
                "error_details": result.error
            }
        
        return result
    
    async def _format_code(self, file_path: Optional[str] = None, **kwargs) -> ToolResult:
        """Format Dart code."""
        command = "dart format"
        
        if file_path:
            command += f" {file_path}"
        else:
            command += " ."
        
        return await self.terminal.execute(command)
    
    async def _pub_get(self, **kwargs) -> ToolResult:
        """Get Flutter dependencies."""
        command = "flutter pub get"
        return await self.terminal.execute(command)
    
    async def _pub_add(self, packages: List[str], dev: bool = False, **kwargs) -> ToolResult:
        """Add Flutter packages."""
        if not packages:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="No packages specified"
            )
        
        command = "flutter pub add"
        if dev:
            command += " --dev"
        command += " " + " ".join(packages)
        
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            result.data = {
                "packages": packages,
                "dev_dependencies": dev
            }
        
        return result
    
    async def _clean_project(self, **kwargs) -> ToolResult:
        """Clean Flutter project."""
        command = "flutter clean"
        return await self.terminal.execute(command)
    
    async def _flutter_doctor(self, verbose: bool = False, **kwargs) -> ToolResult:
        """Run Flutter doctor to check environment."""
        command = "flutter doctor"
        if verbose:
            command += " -v"
        
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            # Parse doctor output for issues
            issues = self._parse_doctor_output(result.output)
            result.data = {
                "environment_issues": issues,
                "verbose": verbose
            }
        
        return result
    
    async def _list_devices(self, **kwargs) -> ToolResult:
        """List available devices."""
        command = "flutter devices --machine"
        result = await self.terminal.execute(command)
        
        if result.status == ToolStatus.SUCCESS:
            try:
                devices = json.loads(result.output)
                result.data = {
                    "devices": devices,
                    "device_count": len(devices)
                }
                result.output = f"Found {len(devices)} available devices"
            except json.JSONDecodeError:
                # Fallback to regular device list
                result = await self.terminal.execute("flutter devices")
        
        return result
    
    async def _run_app(self, device_id: Optional[str] = None, debug: bool = True, **kwargs) -> ToolResult:
        """Run Flutter app on device."""
        command = "flutter run"
        
        if device_id:
            command += f" -d {device_id}"
        
        if not debug:
            command += " --release"
        
        # For run command, we don't wait for completion as it's interactive
        result = await self.terminal.execute(command, capture_output=False)
        
        result.data = {
            "device_id": device_id,
            "debug_mode": debug
        }
        
        return result
    
    async def _generate_code(self, **kwargs) -> ToolResult:
        """Generate code using build_runner."""
        # First check if build_runner is available
        check_result = await self.terminal.execute("flutter packages pub run build_runner --help")
        
        if check_result.status != ToolStatus.SUCCESS:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="build_runner not available. Add it to dev_dependencies in pubspec.yaml"
            )
        
        command = "flutter packages pub run build_runner build"
        result = await self.terminal.execute(command)
        
        return result
    
    # Public methods for test and agent compatibility
    async def doctor(self, **kwargs):
        return await self.execute("doctor", **kwargs)

    async def create_project(self, **kwargs):
        return await self.execute("create", **kwargs)

    async def build(self, **kwargs):
        return await self.execute("build", **kwargs)

    async def test(self, **kwargs):
        return await self.execute("test", **kwargs)

    async def pub_get(self, **kwargs):
        return await self.execute("pub_get", **kwargs)

    async def pub_add(self, packages, **kwargs):
        return await self.execute("pub_add", packages=packages, **kwargs)
    
    def _parse_analysis_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse flutter analyze output for issues."""
        issues = []
        lines = output.split('\n')
        
        for line in lines:
            line = line.strip()
            if '•' in line and ('error' in line.lower() or 'warning' in line.lower() or 'info' in line.lower()):
                # Try to parse the issue format
                parts = line.split('•')
                if len(parts) >= 2:
                    message = parts[1].strip()
                    # Extract severity, file, and line info if present
                    severity = "info"
                    if "error" in line.lower():
                        severity = "error"
                    elif "warning" in line.lower():
                        severity = "warning"
                    
                    # Try to extract file path and line number
                    file_path = ""
                    line_number = ""
                    if " at " in line:
                        location_part = line.split(" at ")[-1]
                        if ":" in location_part:
                            file_path = location_part.split(":")[0]
                            line_number = location_part.split(":")[1] if len(location_part.split(":")) > 1 else ""
                    
                    issues.append({
                        "message": message,
                        "severity": severity,
                        "file_path": file_path,
                        "line_number": line_number,
                        "full_line": line
                    })
        
        # Also check for common error patterns
        error_patterns = [
            "Error: ",
            "Warning: ",
            "Info: ",
            "missing_return",
            "undefined_class",
            "undefined_method",
            "invalid_assignment"
        ]
        
        for line in lines:
            for pattern in error_patterns:
                if pattern in line and not any(issue["full_line"] == line for issue in issues):
                    issues.append({
                        "message": line.strip(),
                        "severity": "error" if "Error:" in line else "warning",
                        "file_path": "",
                        "line_number": "",
                        "full_line": line
                    })
        
        return issues
    
    def _parse_doctor_output(self, output: str) -> List[Dict[str, Any]]:
        """Parse flutter doctor output for issues."""
        issues = []
        lines = output.split('\n')
        
        current_section = None
        for line in lines:
            line = line.strip()
            
            if line.startswith('[✓]'):
                current_section = line[3:].strip()
            elif line.startswith('[✗]'):
                current_section = line[3:].strip()
                issues.append({
                    "section": current_section,
                    "status": "error",
                    "message": current_section
                })
            elif line.startswith('[!]'):
                current_section = line[3:].strip()
                issues.append({
                    "section": current_section,
                    "status": "warning",
                    "message": current_section
                })
        
        return issues
    
    async def get_project_info(self) -> ToolResult:
        """Get information about the current Flutter project."""
        pubspec_path = os.path.join(self.project_directory, "pubspec.yaml")
        
        if not os.path.exists(pubspec_path):
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Not a Flutter project (pubspec.yaml not found)"
            )
        
        try:
            import yaml
            with open(pubspec_path, 'r') as f:
                pubspec = yaml.safe_load(f)
            
            # Get Flutter version info
            flutter_version_result = await self.terminal.execute("flutter --version")
            
            project_info = {
                "name": pubspec.get("name", "unknown"),
                "version": pubspec.get("version", "unknown"),
                "description": pubspec.get("description", ""),
                "dependencies": list(pubspec.get("dependencies", {}).keys()),
                "dev_dependencies": list(pubspec.get("dev_dependencies", {}).keys()),
                "flutter_version": flutter_version_result.output.split('\n')[0] if flutter_version_result.status == ToolStatus.SUCCESS else "unknown"
            }
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Project: {project_info['name']} v{project_info['version']}",
                data=project_info
            )
            
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Failed to read project info: {str(e)}"
            )
