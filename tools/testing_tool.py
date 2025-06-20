"""
Testing tool for creating and running tests in Flutter projects.
"""

import asyncio
import os
import json
from typing import Dict, Any, Optional, List
from .base_tool import BaseTool, ToolResult, ToolStatus
from .terminal_tool import TerminalTool
from .file_tool import FileTool

class TestingTool(BaseTool):
    """
    Tool for managing Flutter tests - unit, widget, and integration tests.
    """
    
    def __init__(self, project_directory: Optional[str] = None):
        super().__init__(
            name="testing",
            description="Create and run Flutter tests",
            timeout=300  # Longer timeout for test execution
        )
        self.project_directory = project_directory or os.getcwd()
        self.terminal = TerminalTool(project_directory)
        self.file_tool = FileTool(project_directory)
    
    async def execute(self, operation: str, **kwargs) -> ToolResult:
        """
        Execute testing operations.
        
        Args:
            operation: Operation to perform (run, create, coverage, etc.)
            **kwargs: Operation-specific parameters
            
        Returns:
            ToolResult with operation outcome
        """
        self.validate_parameters(["operation"], operation=operation, **kwargs)
        
        if operation == "run":
            return await self._run_tests(**kwargs)
        elif operation == "create_unit_test":
            return await self._create_unit_test(**kwargs)
        elif operation == "create_widget_test":
            return await self._create_widget_test(**kwargs)
        elif operation == "create_integration_test":
            return await self._create_integration_test(**kwargs)
        elif operation == "coverage":
            return await self._run_coverage(**kwargs)
        elif operation == "analyze_coverage":
            return await self._analyze_coverage(**kwargs)
        elif operation == "setup_testing":
            return await self._setup_testing(**kwargs)
        else:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Unknown operation: {operation}"
            )
    
    async def _run_tests(self, **kwargs) -> ToolResult:
        """Run Flutter tests."""
        test_type = kwargs.get("test_type", "all")  # unit, widget, integration, all
        test_file = kwargs.get("test_file")
        coverage = kwargs.get("coverage", False)
        
        # Build command
        cmd_parts = ["flutter", "test"]
        
        if coverage:
            cmd_parts.append("--coverage")
        
        if test_file:
            cmd_parts.append(test_file)
        elif test_type != "all":
            # Run specific test type
            if test_type == "unit":
                cmd_parts.append("test/unit/")
            elif test_type == "widget":
                cmd_parts.append("test/widget/")
            elif test_type == "integration":
                cmd_parts = ["flutter", "test", "integration_test/"]
        
        command = " ".join(cmd_parts)
        result = await self.terminal.execute(command, working_dir=self.project_directory)
        
        # Parse test results
        test_results = self._parse_test_output(result.output)
        
        return ToolResult(
            status=result.status,
            output=result.output,
            error=result.error,
            data={
                "test_type": test_type,
                "test_file": test_file,
                "coverage_enabled": coverage,
                "test_results": test_results
            }
        )
    
    async def _create_unit_test(self, **kwargs) -> ToolResult:
        """Create a unit test file."""
        class_name = kwargs.get("class_name")
        test_name = kwargs.get("test_name")
        file_path = kwargs.get("file_path")
        
        if not class_name:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Class name is required for unit test creation"
            )
        
        # Generate test content
        test_content = self._generate_unit_test_template(class_name, test_name)
        
        # Determine test file path
        if not file_path:
            file_path = f"test/unit/{class_name.lower()}_test.dart"
        
        # Create test directory if it doesn't exist
        test_dir = os.path.dirname(os.path.join(self.project_directory, file_path))
        os.makedirs(test_dir, exist_ok=True)
        
        # Write test file
        write_result = await self.file_tool.execute(
            "write",
            file_path=file_path,
            content=test_content
        )
        
        if write_result.status == ToolStatus.SUCCESS:
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Unit test created at {file_path}",
                data={
                    "test_type": "unit",
                    "class_name": class_name,
                    "file_path": file_path
                }
            )
        
        return write_result
    
    async def _create_widget_test(self, **kwargs) -> ToolResult:
        """Create a widget test file."""
        widget_name = kwargs.get("widget_name")
        test_scenarios = kwargs.get("test_scenarios", [])
        file_path = kwargs.get("file_path")
        
        if not widget_name:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Widget name is required for widget test creation"
            )
        
        # Generate test content
        test_content = self._generate_widget_test_template(widget_name, test_scenarios)
        
        # Determine test file path
        if not file_path:
            file_path = f"test/widget/{widget_name.lower()}_test.dart"
        
        # Create test directory if it doesn't exist
        test_dir = os.path.dirname(os.path.join(self.project_directory, file_path))
        os.makedirs(test_dir, exist_ok=True)
        
        # Write test file
        write_result = await self.file_tool.execute(
            "write",
            file_path=file_path,
            content=test_content
        )
        
        if write_result.status == ToolStatus.SUCCESS:
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Widget test created at {file_path}",
                data={
                    "test_type": "widget",
                    "widget_name": widget_name,
                    "file_path": file_path,
                    "scenarios": len(test_scenarios)
                }
            )
        
        return write_result
    
    async def _create_integration_test(self, **kwargs) -> ToolResult:
        """Create an integration test file."""
        test_name = kwargs.get("test_name")
        test_flows = kwargs.get("test_flows", [])
        file_path = kwargs.get("file_path")
        
        if not test_name:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Test name is required for integration test creation"
            )
        
        # Generate test content
        test_content = self._generate_integration_test_template(test_name, test_flows)
        
        # Determine test file path
        if not file_path:
            file_path = f"integration_test/{test_name.lower()}_test.dart"
        
        # Create test directory if it doesn't exist
        test_dir = os.path.dirname(os.path.join(self.project_directory, file_path))
        os.makedirs(test_dir, exist_ok=True)
        
        # Write test file
        write_result = await self.file_tool.execute(
            "write",
            file_path=file_path,
            content=test_content
        )
        
        if write_result.status == ToolStatus.SUCCESS:
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Integration test created at {file_path}",
                data={
                    "test_type": "integration",
                    "test_name": test_name,
                    "file_path": file_path,
                    "flows": len(test_flows)
                }
            )
        
        return write_result
    
    async def _run_coverage(self, **kwargs) -> ToolResult:
        """Run tests with coverage analysis."""
        result = await self.terminal.execute(
            "flutter test --coverage",
            working_dir=self.project_directory
        )
        
        if result.status == ToolStatus.SUCCESS:
            # Check if coverage file was generated
            coverage_file = os.path.join(self.project_directory, "coverage", "lcov.info")
            
            if os.path.exists(coverage_file):
                # Parse coverage data
                coverage_data = await self._parse_coverage_file(coverage_file)
                
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    output="Test coverage analysis completed",
                    data={
                        "coverage_file": coverage_file,
                        "coverage_data": coverage_data
                    }
                )
        
        return result
    
    async def _analyze_coverage(self, **kwargs) -> ToolResult:
        """Analyze test coverage from existing coverage files."""
        coverage_file = os.path.join(self.project_directory, "coverage", "lcov.info")
        
        if not os.path.exists(coverage_file):
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Coverage file not found. Run tests with --coverage first."
            )
        
        coverage_data = await self._parse_coverage_file(coverage_file)
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output="Coverage analysis completed",
            data=coverage_data
        )
    
    async def _setup_testing(self, **kwargs) -> ToolResult:
        """Setup testing infrastructure for the project."""
        testing_packages = [
            "flutter_test",
            "mockito",
            "build_runner",
            "bloc_test",
            "integration_test"
        ]
        
        # Create test directories
        test_dirs = [
            "test/unit",
            "test/widget",
            "test/mocks",
            "integration_test"
        ]
        
        for dir_path in test_dirs:
            full_path = os.path.join(self.project_directory, dir_path)
            os.makedirs(full_path, exist_ok=True)
        
        # Create basic test helper file
        test_helper_content = self._generate_test_helper()
        await self.file_tool.execute(
            "write",
            file_path="test/test_helper.dart",
            content=test_helper_content
        )
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output="Testing infrastructure setup completed",
            data={
                "directories_created": test_dirs,
                "recommended_packages": testing_packages
            }
        )
    
    def _parse_test_output(self, output: str) -> Dict[str, Any]:
        """Parse Flutter test output to extract results."""
        lines = output.split('\n')
        
        test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "failures": []
        }
        
        for line in lines:
            line = line.strip()
            
            # Look for test result indicators
            if "All tests passed!" in line:
                # Extract number from lines like "All tests passed! (5 tests)"
                import re
                match = re.search(r'\((\d+) tests?\)', line)
                if match:
                    test_results["total_tests"] = int(match.group(1))
                    test_results["passed"] = int(match.group(1))
            elif "tests passed" in line and "failed" in line:
                # Parse lines like "4 tests passed, 1 failed"
                import re
                passed_match = re.search(r'(\d+) tests? passed', line)
                failed_match = re.search(r'(\d+) failed', line)
                
                if passed_match:
                    test_results["passed"] = int(passed_match.group(1))
                if failed_match:
                    test_results["failed"] = int(failed_match.group(1))
                
                test_results["total_tests"] = test_results["passed"] + test_results["failed"]
            
            # Look for failure details
            if "FAILED:" in line:
                test_results["failures"].append(line)
        
        return test_results
    
    async def _parse_coverage_file(self, coverage_file: str) -> Dict[str, Any]:
        """Parse LCOV coverage file."""
        try:
            with open(coverage_file, 'r') as file:
                content = file.read()
            
            lines = content.split('\n')
            coverage_data = {
                "files": {},
                "overall": {
                    "lines_found": 0,
                    "lines_hit": 0,
                    "functions_found": 0,
                    "functions_hit": 0,
                    "branches_found": 0,
                    "branches_hit": 0
                }
            }
            
            current_file = None
            
            for line in lines:
                line = line.strip()
                
                if line.startswith("SF:"):
                    current_file = line[3:]  # Remove "SF:" prefix
                    coverage_data["files"][current_file] = {
                        "lines_found": 0,
                        "lines_hit": 0,
                        "functions_found": 0,
                        "functions_hit": 0,
                        "branches_found": 0,
                        "branches_hit": 0
                    }
                elif line.startswith("LF:") and current_file:
                    coverage_data["files"][current_file]["lines_found"] = int(line[3:])
                elif line.startswith("LH:") and current_file:
                    coverage_data["files"][current_file]["lines_hit"] = int(line[3:])
                elif line.startswith("FNF:") and current_file:
                    coverage_data["files"][current_file]["functions_found"] = int(line[4:])
                elif line.startswith("FNH:") and current_file:
                    coverage_data["files"][current_file]["functions_hit"] = int(line[4:])
                elif line.startswith("BRF:") and current_file:
                    coverage_data["files"][current_file]["branches_found"] = int(line[4:])
                elif line.startswith("BRH:") and current_file:
                    coverage_data["files"][current_file]["branches_hit"] = int(line[4:])
            
            # Calculate overall coverage
            for file_data in coverage_data["files"].values():
                coverage_data["overall"]["lines_found"] += file_data["lines_found"]
                coverage_data["overall"]["lines_hit"] += file_data["lines_hit"]
                coverage_data["overall"]["functions_found"] += file_data["functions_found"]
                coverage_data["overall"]["functions_hit"] += file_data["functions_hit"]
                coverage_data["overall"]["branches_found"] += file_data["branches_found"]
                coverage_data["overall"]["branches_hit"] += file_data["branches_hit"]
            
            # Calculate percentages
            overall = coverage_data["overall"]
            if overall["lines_found"] > 0:
                overall["line_coverage"] = (overall["lines_hit"] / overall["lines_found"]) * 100
            if overall["functions_found"] > 0:
                overall["function_coverage"] = (overall["functions_hit"] / overall["functions_found"]) * 100
            if overall["branches_found"] > 0:
                overall["branch_coverage"] = (overall["branches_hit"] / overall["branches_found"]) * 100
            
            return coverage_data
            
        except Exception as e:
            return {"error": f"Failed to parse coverage file: {str(e)}"}
    
    def _generate_unit_test_template(self, class_name: str, test_name: Optional[str] = None) -> str:
        """Generate unit test template - REPLACED WITH LLM GENERATION."""
        pass

    def _generate_widget_test_template(self, widget_name: str, scenario_tests: str = "") -> str:
        """Generate widget test template - REPLACED WITH LLM GENERATION."""
        pass

    def _generate_integration_test_template(self, test_name: str, flow_tests: str = "") -> str:
        """Generate integration test template - REPLACED WITH LLM GENERATION."""
        pass

    def _generate_test_helper(self) -> str:
        """Generate test helper file - REPLACED WITH LLM GENERATION."""
        pass

    # New methods to use LLM for code generation
    async def _generate_test_code_with_llm(self, test_type: str, context: dict) -> str:
        """Generate test code using LLM."""
        prompt = f"Generate a Flutter {test_type} test for {context.get('widget_name', 'the widget')}"
        
        if test_type == "unit":
            prompt += f"\nInclude proper unit test structure, mocks, and assertions."
        elif test_type == "widget":
            prompt += f"\nInclude proper widget test setup, rendering tests, and interaction tests."
        elif test_type == "integration":
            prompt += f"\nInclude proper integration test setup with comprehensive flows."
        
        # Add more context to the prompt
        prompt += f"\nContext: {context}"
        
        # Use the agent's think method to generate code via LLM
        test_code = await self.think(prompt, context)
        return test_code
