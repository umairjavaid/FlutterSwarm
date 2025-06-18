#!/usr/bin/env python3
"""
Simple test runner to debug import issues.
"""

import os
import sys

def main():
    """Run simple tests to debug issues."""
    print("FlutterSwarm Debug Test Runner")
    print("=============================")
    
    os.chdir("/workspaces/FlutterSwarm")
    
    # Test 1: Basic Python
    print("\n1. Testing basic Python...")
    try:
        exec("print('Python works!')")
        print("✅ Basic Python OK")
    except Exception as e:
        print(f"❌ Basic Python failed: {e}")
        return 1
    
    # Test 2: Simple imports
    print("\n2. Testing simple imports...")
    try:
        import asyncio
        import os
        import time
        print("✅ Standard library imports OK")
    except Exception as e:
        print(f"❌ Standard library imports failed: {e}")
        return 1
    
    # Test 3: Our base_tool import
    print("\n3. Testing base_tool import...")
    try:
        from tools.base_tool import BaseTool, ToolResult, ToolStatus
        print("✅ base_tool import OK")
    except Exception as e:
        print(f"❌ base_tool import failed: {e}")
        return 1
    
    # Test 4: Our terminal_tool import
    print("\n4. Testing terminal_tool import...")
    try:
        from tools.terminal_tool import TerminalTool
        print("✅ terminal_tool import OK")
    except Exception as e:
        print(f"❌ terminal_tool import failed: {e}")
        return 1
    
    # Test 5: Tools package import
    print("\n5. Testing tools package import...")
    try:
        from tools import TerminalTool as TT
        print("✅ tools package import OK")
    except Exception as e:
        print(f"❌ tools package import failed: {e}")
        return 1
    
    # Test 6: Run simple test file
    print("\n6. Testing simple test file...")
    try:
        os.system("python tests/test_simple.py")
        print("✅ Simple test file OK")
    except Exception as e:
        print(f"❌ Simple test file failed: {e}")
        return 1
    
    print("\n✅ All debug tests passed!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
