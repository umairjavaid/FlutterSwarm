"""
Flutter-specific tool for Flutter development operations.
"""

import os
import json
import time
from typing import Dict, Any, Optional, List
from .base_tool import BaseTool, ToolResult, ToolStatus
from .terminal_tool import TerminalTool
from utils.path_utils import get_absolute_project_path
from utils.function_logger import track_function

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
    
    @track_function(log_args=True, log_return=True)
    async def execute(self, operation: str, **kwargs) -> ToolResult:
        """
        Execute Flutter operation.
        
        Args:
            operation: Type of operation (build, test, analyze, etc.)
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
            elif operation == "validate":
                return await self._validate_project(**kwargs)
            elif operation == "health":
                return await self._get_project_health(**kwargs)
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
        """Create a new Flutter project with proper structure."""
        # Ensure flutter_projects directory exists at repo root
        project_path = get_absolute_project_path(project_name)
        flutter_projects_dir = os.path.dirname(project_path)
        os.makedirs(flutter_projects_dir, exist_ok=True)
        
        # Check if project already exists and has essential files
        if os.path.exists(project_path):
            essential_files = [
                os.path.join(project_path, "pubspec.yaml"),
                os.path.join(project_path, "lib", "main.dart"),
                os.path.join(project_path, "test"),
                os.path.join(project_path, "lib")
            ]
            missing_files = [f for f in essential_files if not os.path.exists(f)]
            if missing_files:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output=f"Project {project_name} exists but missing essential files: {missing_files}",
                    error=f"Incomplete Flutter project at {project_path}. Missing: {missing_files}"
                )
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Project {project_name} already exists at {project_path} with complete structure",
                data={
                    "project_name": project_name,
                    "project_path": project_path,
                    "exists": True,
                    "essential_files_verified": True
                }
            )
        # Run flutter create in the correct directory (repo_root/flutter_projects)
        command = f"flutter create --org {org} --template {template} {project_name}"
        result = await self.terminal.execute(command, working_dir=flutter_projects_dir)
        if result.status == ToolStatus.SUCCESS:
            # Verify essential files exist
            essential_files = [
                os.path.join(project_path, "pubspec.yaml"),
                os.path.join(project_path, "lib", "main.dart"),
                os.path.join(project_path, "test"),
                os.path.join(project_path, "lib")
            ]
            missing_files = [f for f in essential_files if not os.path.exists(f)]
            if missing_files:
                return ToolResult(
                    status=ToolStatus.ERROR,
                    output=result.output,
                    error=f"Flutter project created but missing essential files: {missing_files}"
                )
            # Initialize git repository
            try:
                git_init_result = await self.terminal.execute("git init", working_dir=project_path)
                if git_init_result.status == ToolStatus.SUCCESS:
                    await self.terminal.execute("git add .", working_dir=project_path)
                    await self.terminal.execute('git commit -m "Initial Flutter project structure"', working_dir=project_path)
                    git_initialized = True
                else:
                    git_initialized = False
            except Exception as e:
                print(f"Warning: Failed to initialize git repository: {e}")
                git_initialized = False
            result.data = {
                "project_name": project_name,
                "project_path": project_path,
                "template": template,
                "organization": org,
                "git_initialized": git_initialized,
                "essential_files_verified": True,
                "note": "Flutter project created with proper structure. Implementation agents will generate custom code via LLMs."
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
        
        command = f"flutter_command build {platform}"
        if mode != "debug":
            command += f" --{mode}"
        command = command.replace("flutter_command", "flutter")
        
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
        command = "flutter_command test"
        command = command.replace("flutter_command", "flutter")
        
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
        project_path = kwargs.get("project_path")
        
        if project_path:
            result = await self.terminal.execute(command, working_dir=project_path)
        else:
            result = await self.terminal.execute(command)
        
        # Parse analysis results
        if result.status == ToolStatus.SUCCESS:
            issues = self._parse_analysis_output(result.output)
            result.data = {
                "issues_found": len(issues),
                "issues": issues
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
        project_path = kwargs.get("project_path")
        
        if project_path:
            # Use the specified project path as working directory
            return await self.terminal.execute(command, working_dir=project_path)
        else:
            # Use current working directory
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
        
        project_path = kwargs.get("project_path")
        
        if project_path:
            result = await self.terminal.execute(command, working_dir=project_path)
        else:
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
        project_path = kwargs.get("project_path")
        
        if project_path:
            return await self.terminal.execute(command, working_dir=project_path)
        else:
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
        command = "flutter_command run"
        command = command.replace("flutter_command", "flutter")
        
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
                error="build_runner not available. Add it to dev_dependencies in the project's dependency file"
            )
        
        command = "flutter packages pub run build_runner build"
        result = await self.terminal.execute(command)
        
        return result
    
    async def _validate_project(self, project_path: str = None, **kwargs) -> ToolResult:
        """Validate Flutter project structure and configuration."""
        from utils.flutter_validation import validate_flutter_project
        
        if not project_path:
            project_path = self.project_directory
            
        if not project_path:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="No project path specified for validation"
            )
        
        try:
            # Perform comprehensive project validation
            validation_result = await validate_flutter_project(project_path)
            
            # Determine status based on validation
            if validation_result['valid']:
                status = ToolStatus.SUCCESS
                output = f"✅ Flutter project validation passed for {project_path}"
            else:
                status = ToolStatus.ERROR
                missing_files = validation_result.get('missing_files', [])
                output = f"❌ Flutter project validation failed. Missing files: {missing_files}"
            
            return ToolResult(
                status=status,
                output=output,
                data=validation_result
            )
            
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Error during project validation: {str(e)}"
            )

    async def _get_project_health(self, project_path: str = None, **kwargs) -> ToolResult:
        """Get Flutter project health score and recommendations."""
        from utils.flutter_validation import validate_flutter_project, get_flutter_project_health_score
        
        if not project_path:
            project_path = self.project_directory
            
        if not project_path:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="No project path specified for health check"
            )
        
        try:
            # Get validation results
            validation_result = await validate_flutter_project(project_path)
            
            # Calculate health score
            health_score = get_flutter_project_health_score(validation_result)
            
            # Format output message
            score = health_score['score']
            grade = health_score['grade']
            issues_count = len(health_score['issues'])
            
            if score >= 80:
                status = ToolStatus.SUCCESS
                output = f"🎯 Project health: {score}/100 (Grade: {grade}) - Good project structure"
            elif score >= 60:
                status = ToolStatus.WARNING
                output = f"⚠️ Project health: {score}/100 (Grade: {grade}) - {issues_count} issues found"
            else:
                status = ToolStatus.ERROR
                output = f"🚨 Project health: {score}/100 (Grade: {grade}) - Significant issues detected"
            
            return ToolResult(
                status=status,
                output=output,
                data={
                    'health_score': health_score,
                    'validation_result': validation_result
                }
            )
            
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Error during health check: {str(e)}"
            )

    # Public methods for test and agent compatibility
    async def doctor(self, **kwargs):
        return await self.execute("doctor", **kwargs)

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
                    
                    issues.append({
                        "message": message,
                        "severity": severity,
                        "line": line
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
    
    async def get_project_info(self, pubspec_path: str) -> ToolResult:
        """Get information about the current Flutter project - analysis only."""
        
        if not os.path.exists(pubspec_path):
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Not a Flutter project (dependencies file not found). Use LLM agents to generate project structure."
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
