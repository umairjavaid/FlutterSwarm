"""
Package management tool for handling dependencies in Flutter projects.
"""

import asyncio
import json
import os
import yaml
from typing import Dict, Any, Optional, List
from .base_tool import BaseTool, ToolResult, ToolStatus
from .terminal_tool import TerminalTool

class PackageManagerTool(BaseTool):
    """
    Tool for managing Flutter packages and dependencies.
    """
    
    def __init__(self, project_directory: Optional[str] = None):
        super().__init__(
            name="package_manager",
            description="Manage Flutter packages and dependencies",
            timeout=120
        )
        self.project_directory = project_directory or os.getcwd()
        self.terminal = TerminalTool(project_directory)
    
    async def execute(self, operation: str, **kwargs) -> ToolResult:
        """
        Execute package management operations.
        
        Args:
            operation: Operation to perform (add, remove, update, etc.)
            **kwargs: Operation-specific parameters
            
        Returns:
            ToolResult with operation outcome
        """
        self.validate_parameters(["operation"], operation=operation, **kwargs)
        
        if operation == "add":
            return await self._add_package(**kwargs)
        elif operation == "remove":
            return await self._remove_package(**kwargs)
        elif operation == "update":
            return await self._update_packages(**kwargs)
        elif operation == "get":
            return await self._get_packages(**kwargs)
        elif operation == "analyze":
            return await self._analyze_dependencies(**kwargs)
        elif operation == "search":
            return await self._search_packages(**kwargs)
        elif operation == "outdated":
            return await self._check_outdated(**kwargs)
        else:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Unknown operation: {operation}"
            )
    
    async def _add_package(self, **kwargs) -> ToolResult:
        """Add a package to the project."""
        package_name = kwargs.get("package_name")
        version = kwargs.get("version")
        dev_dependency = kwargs.get("dev_dependency", False)
        
        if not package_name:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Package name is required"
            )
        
        # Build command
        cmd_parts = ["flutter", "pub", "add"]
        if dev_dependency:
            cmd_parts.append("--dev")
        
        if version:
            cmd_parts.append(f"{package_name}:{version}")
        else:
            cmd_parts.append(package_name)
        
        command = " ".join(cmd_parts)
        result = await self.terminal.execute(command, working_dir=self.project_directory)
        
        if result.status == ToolStatus.SUCCESS:
            # Verify package was added by checking pubspec.yaml
            pubspec_result = await self._read_pubspec()
            if pubspec_result.status == ToolStatus.SUCCESS:
                dependencies = pubspec_result.data.get("dependencies", {})
                dev_dependencies = pubspec_result.data.get("dev_dependencies", {})
                
                target_deps = dev_dependencies if dev_dependency else dependencies
                
                return ToolResult(
                    status=ToolStatus.SUCCESS,
                    output=f"Package '{package_name}' added successfully",
                    data={
                        "package_name": package_name,
                        "version": target_deps.get(package_name, "unknown"),
                        "dev_dependency": dev_dependency
                    }
                )
        
        return result
    
    async def _remove_package(self, **kwargs) -> ToolResult:
        """Remove a package from the project."""
        package_name = kwargs.get("package_name")
        
        if not package_name:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Package name is required"
            )
        
        command = f"flutter pub remove {package_name}"
        result = await self.terminal.execute(command, working_dir=self.project_directory)
        
        if result.status == ToolStatus.SUCCESS:
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Package '{package_name}' removed successfully",
                data={"package_name": package_name}
            )
        
        return result
    
    async def _update_packages(self, **kwargs) -> ToolResult:
        """Update all packages or specific package."""
        package_name = kwargs.get("package_name")
        
        if package_name:
            command = f"flutter pub upgrade {package_name}"
        else:
            command = "flutter pub upgrade"
        
        result = await self.terminal.execute(command, working_dir=self.project_directory)
        
        if result.status == ToolStatus.SUCCESS:
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output="Packages updated successfully",
                data={"updated_package": package_name or "all"}
            )
        
        return result
    
    async def _get_packages(self, **kwargs) -> ToolResult:
        """Get/download packages."""
        command = "flutter pub get"
        result = await self.terminal.execute(command, working_dir=self.project_directory)
        
        if result.status == ToolStatus.SUCCESS:
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output="Packages downloaded successfully",
                data={"operation": "pub_get"}
            )
        
        return result
    
    async def _analyze_dependencies(self, **kwargs) -> ToolResult:
        """Analyze project dependencies."""
        pubspec_result = await self._read_pubspec()
        if pubspec_result.status != ToolStatus.SUCCESS:
            return pubspec_result
        
        pubspec_data = pubspec_result.data
        dependencies = pubspec_data.get("dependencies", {})
        dev_dependencies = pubspec_data.get("dev_dependencies", {})
        
        # Get dependency tree
        tree_result = await self.terminal.execute(
            "flutter pub deps --style=tree",
            working_dir=self.project_directory
        )
        
        # Count dependencies
        dep_count = len(dependencies)
        dev_dep_count = len(dev_dependencies)
        total_count = dep_count + dev_dep_count
        
        analysis = {
            "total_dependencies": total_count,
            "runtime_dependencies": dep_count,
            "dev_dependencies": dev_dep_count,
            "dependencies": dependencies,
            "dev_dependencies": dev_dependencies,
            "dependency_tree": tree_result.output if tree_result.status == ToolStatus.SUCCESS else None
        }
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Analyzed {total_count} dependencies ({dep_count} runtime, {dev_dep_count} dev)",
            data=analysis
        )
    
    async def _search_packages(self, **kwargs) -> ToolResult:
        """Search for packages on pub.dev."""
        query = kwargs.get("query")
        
        if not query:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Search query is required"
            )
        
        command = f"flutter pub search {query}"
        result = await self.terminal.execute(command, working_dir=self.project_directory)
        
        if result.status == ToolStatus.SUCCESS:
            # Parse search results
            packages = []
            lines = result.output.strip().split('\n')
            
            for line in lines:
                if line.startswith('  '):  # Package lines are indented
                    parts = line.strip().split(' - ')
                    if len(parts) >= 2:
                        name = parts[0]
                        description = parts[1] if len(parts) > 1 else ""
                        packages.append({
                            "name": name,
                            "description": description
                        })
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"Found {len(packages)} packages matching '{query}'",
                data={
                    "query": query,
                    "packages": packages
                }
            )
        
        return result
    
    async def _check_outdated(self, **kwargs) -> ToolResult:
        """Check for outdated packages."""
        command = "flutter pub outdated"
        result = await self.terminal.execute(command, working_dir=self.project_directory)
        
        if result.status == ToolStatus.SUCCESS:
            # Parse outdated packages info
            outdated_info = {
                "raw_output": result.output,
                "has_outdated": "outdated" in result.output.lower() and result.output.strip() != ""
            }
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output="Checked for outdated packages",
                data=outdated_info
            )
        
        return result
    
    async def _read_pubspec(self) -> ToolResult:
        """Read and parse pubspec.yaml - analysis only, no generation."""
        pubspec_path = os.path.join(self.project_directory, "pubspec.yaml")
        
        try:
            with open(pubspec_path, 'r') as file:
                pubspec_data = yaml.safe_load(file)
            
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output="Pubspec.yaml read successfully",
                data=pubspec_data
            )
        except FileNotFoundError:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="pubspec.yaml not found. Use LLM agents to generate project structure."
            )
        except yaml.YAMLError as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Error parsing pubspec.yaml: {str(e)}"
            )
        except Exception as e:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Error reading pubspec.yaml: {str(e)}"
            )
    
    async def add_multiple_packages(self, packages: List[Dict[str, Any]]) -> ToolResult:
        """Add multiple packages at once."""
        results = []
        
        for package_info in packages:
            result = await self._add_package(**package_info)
            results.append({
                "package": package_info.get("package_name"),
                "success": result.status == ToolStatus.SUCCESS,
                "error": result.error
            })
        
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        
        return ToolResult(
            status=ToolStatus.SUCCESS if len(failed) == 0 else ToolStatus.WARNING,
            output=f"Added {len(successful)} packages, {len(failed)} failed",
            data={
                "successful": successful,
                "failed": failed,
                "total": len(packages)
            }
        )
    
    async def get_package_info(self, package_name: str) -> ToolResult:
        """Get detailed information about a specific package."""
        # First check if package is in current project
        pubspec_result = await self._read_pubspec()
        
        package_info = {
            "name": package_name,
            "in_project": False,
            "version": None,
            "is_dev_dependency": False
        }
        
        if pubspec_result.status == ToolStatus.SUCCESS:
            pubspec_data = pubspec_result.data
            dependencies = pubspec_data.get("dependencies", {})
            dev_dependencies = pubspec_data.get("dev_dependencies", {})
            
            if package_name in dependencies:
                package_info.update({
                    "in_project": True,
                    "version": dependencies[package_name],
                    "is_dev_dependency": False
                })
            elif package_name in dev_dependencies:
                package_info.update({
                    "in_project": True,
                    "version": dev_dependencies[package_name],
                    "is_dev_dependency": True
                })
        
        return ToolResult(
            status=ToolStatus.SUCCESS,
            output=f"Package info for '{package_name}'",
            data=package_info
        )
