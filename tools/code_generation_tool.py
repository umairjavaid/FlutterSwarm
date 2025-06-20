"""
Code generation tool for Flutter/Dart development.
"""

import os
from typing import Dict, Any, Optional
from .base_tool import BaseTool, ToolResult, ToolStatus
from .file_tool import FileTool

class CodeGenerationTool(BaseTool):
    """
    Tool for generating Flutter/Dart code components.
    """
    
    def __init__(self, project_directory: Optional[str] = None):
        super().__init__(
            name="code_generation",
            description="Generate Flutter/Dart code components",
            timeout=60
        )
        self.project_directory = project_directory or os.getcwd()
        self.file_tool = FileTool(project_directory)
    
    async def execute(self, operation: str, **kwargs) -> ToolResult:
        """
        Execute code generation operations.
        
        Args:
            operation: Operation to perform (e.g., 'generate')
            **kwargs: Operation-specific parameters
            
        Returns:
            ToolResult with operation outcome
        """
        self.validate_parameters(["operation"], operation=operation, **kwargs)
        
        if operation == "generate":
            return await self._generate_component(**kwargs)
        else:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error=f"Unknown operation: {operation}"
            )
    
    async def _generate_component(self, **kwargs) -> ToolResult:
        """Writes a component to a file. The content MUST be provided by LLM agents."""
        component_type = kwargs.get("component_type")
        name = kwargs.get("name")
        content = kwargs.get("content")
        options = kwargs.get("options", {})

        if not all([component_type, name, content]):
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="component_type, name, and content are required. Content MUST be provided by LLM agents - ZERO hardcoded templates allowed."
            )
        
        # Validate that content is not empty or a placeholder
        if not content.strip() or content.strip() in ["", "TODO", "// TODO"]:
            return ToolResult(
                status=ToolStatus.ERROR,
                output="",
                error="Content cannot be empty. Must be actual LLM-generated code, not placeholder text."
            )
        
        # Determine file path
        file_path = self._get_component_file_path(component_type, name, options)
        
        # Create directories if needed
        dir_path = os.path.dirname(os.path.join(self.project_directory, file_path))
        os.makedirs(dir_path, exist_ok=True)
        
        # Write file with LLM-generated content only
        write_result = await self.file_tool.execute(
            "write",
            file_path=file_path,
            content=content
        )
        
        if write_result.status == ToolStatus.SUCCESS:
            return ToolResult(
                status=ToolStatus.SUCCESS,
                output=f"{component_type.title()} '{name}' generated at {file_path} using LLM-provided content",
                data={
                    "component_type": component_type,
                    "name": name,
                    "file_path": file_path,
                    "content_source": "llm_generated",
                    "content_length": len(content)
                }
            )
        
        return write_result
    
    def _get_component_file_path(self, component_type: str, name: str, options: Dict) -> str:
        """Get the file path for a component - using LLM-guided structure."""
        # Use LLM-guided structure from options if provided, else default
        custom_path = options.get("custom_path")
        if custom_path:
            return custom_path
        
        # Basic path if no custom path provided
        return f"lib/{component_type}/{name.lower()}.dart"
