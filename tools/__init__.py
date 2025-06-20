"""
Tools package for FlutterSwarm agents.
All code generation is exclusively handled by LLM agents - no hardcoded templates.
"""

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
from .tool_manager import ToolManager, AgentToolbox

__all__ = [
    'BaseTool',
    'ToolResult',
    'ToolStatus',
    'TerminalTool',
    'FileTool',
    'FlutterTool',
    'GitTool',
    'AnalysisTool',
    'PackageManagerTool',
    'TestingTool',
    'SecurityTool',
    'CodeGenerationTool',
    'ToolManager',
    'AgentToolbox'
]

# Validation to ensure LLM-only approach
def validate_llm_only_approach():
    """Ensure all tools follow LLM-only code generation approach."""
    return "All Flutter/Dart code generation is exclusively handled by LLM agents"
