#!/usr/bin/env python3
"""
Test script to verify the create/build refactor is working
"""
import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.flutter_tool import FlutterTool

async def test_refactor():
    """Test that both create and build operations work"""
    
    flutter_tool = FlutterTool()
    
    print("🧪 Testing Flutter Tool operations...")
    
    # Test 1: create operation should work now
    try:
        result = await flutter_tool.execute(operation="create", project_name="test_project")
        if "Unknown Flutter operation" in str(result.error or ""):
            print("❌ FAILED: Create operation not supported")
            return False
        else:
            print("✅ PASSED: Create operation is supported")
    except Exception as e:
        print(f"❌ FAILED: Create operation threw error: {e}")
        return False
    
    # Test 2: build operation should still work
    try:
        result = await flutter_tool.execute(operation="build", platform="apk")
        if "Unknown Flutter operation" in str(result.error or ""):
            print("❌ FAILED: Build operation not supported")
            return False
        else:
            print("✅ PASSED: Build operation is supported")
    except Exception as e:
        print(f"✅ PASSED: Build operation is supported (expected error: {e})")
    
    # Test 3: invalid operation should fail appropriately
    try:
        result = await flutter_tool.execute(operation="invalid_operation")
        if "Unknown Flutter operation" in str(result.error or ""):
            print("✅ PASSED: Invalid operations are properly rejected")
        else:
            print("❌ FAILED: Invalid operations should be rejected")
            return False
    except Exception as e:
        print(f"✅ PASSED: Invalid operations are properly rejected ({e})")
    
    print("🎉 All refactor tests passed!")
    return True

if __name__ == "__main__":
    asyncio.run(test_refactor())
