#!/usr/bin/env python3
"""Debug script to test imports."""

import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

def test_imports():
    """Test various import scenarios."""
    print("=== Testing Imports ===")
    
    try:
        print("1. Testing base_tool...")
        from tools.base_tool import BaseTool, ToolResult, ToolStatus
        print("   ✓ base_tool imported")
    except Exception as e:
        print(f"   ✗ base_tool failed: {e}")
        return False
    
    try:
        print("2. Testing terminal_tool...")
        from tools.terminal_tool import TerminalTool
        print("   ✓ terminal_tool imported")
        print(f"   TerminalTool: {TerminalTool}")
    except Exception as e:
        print(f"   ✗ terminal_tool failed: {e}")
        return False
    
    try:
        print("3. Testing tools.__init__...")
        from tools import TerminalTool as TT
        print("   ✓ tools.__init__ imported")
        print(f"   TerminalTool via __init__: {TT}")
    except Exception as e:
        print(f"   ✗ tools.__init__ failed: {e}")
        return False
    
    try:
        print("4. Testing full tools module...")
        import tools
        print("   ✓ tools module imported")
        print(f"   Has TerminalTool: {hasattr(tools, 'TerminalTool')}")
    except Exception as e:
        print(f"   ✗ tools module failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = test_imports()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    sys.exit(0 if success else 1)
