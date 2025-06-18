#!/usr/bin/env python3
"""
Minimal test to debug import issues.
"""

def test_imports():
    """Test individual imports to identify the problematic one."""
    print("Testing imports...")
    
    try:
        from tools.base_tool import BaseTool, ToolResult, ToolStatus
        print("✓ base_tool imported")
    except Exception as e:
        print(f"✗ base_tool failed: {e}")
        return False
    
    try:
        from tools.terminal_tool import TerminalTool
        print("✓ terminal_tool imported")
    except Exception as e:
        print(f"✗ terminal_tool failed: {e}")
        return False
    
    try:
        from tools.file_tool import FileTool
        print("✓ file_tool imported")
    except Exception as e:
        print(f"✗ file_tool failed: {e}")
        return False
    
    try:
        from tools.flutter_tool import FlutterTool
        print("✓ flutter_tool imported")
    except Exception as e:
        print(f"✗ flutter_tool failed: {e}")
        return False
    
    try:
        from tools.git_tool import GitTool
        print("✓ git_tool imported")
    except Exception as e:
        print(f"✗ git_tool failed: {e}")
        return False
    
    try:
        from tools.analysis_tool import AnalysisTool
        print("✓ analysis_tool imported")
    except Exception as e:
        print(f"✗ analysis_tool failed: {e}")
        return False
    
    try:
        from tools.package_manager_tool import PackageManagerTool
        print("✓ package_manager_tool imported")
    except Exception as e:
        print(f"✗ package_manager_tool failed: {e}")
        return False
    
    try:
        from tools.testing_tool import TestingTool
        print("✓ testing_tool imported")
    except Exception as e:
        print(f"✗ testing_tool failed: {e}")
        return False
    
    try:
        from tools.security_tool import SecurityTool
        print("✓ security_tool imported")
    except Exception as e:
        print(f"✗ security_tool failed: {e}")
        return False
    
    try:
        from tools.code_generation_tool import CodeGenerationTool
        print("✓ code_generation_tool imported")
    except Exception as e:
        print(f"✗ code_generation_tool failed: {e}")
        return False
    
    try:
        from tools.tool_manager import ToolManager, AgentToolbox
        print("✓ tool_manager imported")
    except Exception as e:
        print(f"✗ tool_manager failed: {e}")
        return False
    
    try:
        import tools
        print("✓ tools package imported")
    except Exception as e:
        print(f"✗ tools package failed: {e}")
        return False
    
    print("All imports successful!")
    return True

if __name__ == "__main__":
    test_imports()
