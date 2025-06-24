#!/usr/bin/env python3
"""
Test script to validate the Architecture Agent fixes.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, '/home/umair/Desktop/FlutterSwarm')

from agents.architecture_agent import ArchitectureAgent
from shared.state import shared_state, AgentStatus

async def test_architecture_agent_robustness():
    """Test that the Architecture Agent can handle incomplete state gracefully."""
    
    print("🧪 Testing Architecture Agent Robustness...")
    
    # Initialize the architecture agent
    arch_agent = ArchitectureAgent()
    
    # Create a test project with incomplete state
    project_id = "test-robust-architecture"
    
    # Test 1: Architecture agent with no project in shared state
    print("\n📋 Test 1: No project in shared state...")
    task_data = {
        "project_id": project_id,
        "name": "TestApp",
        "description": "A test Flutter application", 
        "requirements": ["Authentication", "Data storage", "UI components"]
    }
    
    try:
        result = await arch_agent._design_flutter_architecture(task_data)
        print("✅ Test 1 PASSED: Agent handled missing project gracefully")
        print(f"   Result type: {type(result)}")
        print(f"   Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}")
        return False
    
    # Test 2: Architecture agent with incomplete project state
    print("\n📋 Test 2: Incomplete project in shared state...")
    
    # Create a project with minimal state (simulating corrupted/incomplete state)
    class IncompleteProject:
        def __init__(self):
            # Missing 'name' and 'description' attributes intentionally
            self.project_id = project_id
            # Only some attributes present
            pass
    
    # Temporarily patch shared_state to return incomplete project
    original_get_project_state = shared_state.get_project_state
    
    def mock_get_project_state(pid):
        if pid == project_id:
            return IncompleteProject()
        return original_get_project_state(pid)
    
    shared_state.get_project_state = mock_get_project_state
    
    try:
        result = await arch_agent._design_flutter_architecture(task_data)
        print("✅ Test 2 PASSED: Agent handled incomplete project state gracefully")
        print(f"   Result type: {type(result)}")
        print(f"   Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}")
        return False
    finally:
        # Restore original method
        shared_state.get_project_state = original_get_project_state
    
    # Test 3: Test with project that has some attributes but not others
    print("\n📋 Test 3: Project with partial attributes...")
    
    class PartialProject:
        def __init__(self):
            self.project_id = project_id
            self.name = "TestApp"
            # Missing 'description' and 'architecture_decisions'
    
    def mock_get_project_state_partial(pid):
        if pid == project_id:
            return PartialProject()
        return original_get_project_state(pid)
    
    shared_state.get_project_state = mock_get_project_state_partial
    
    try:
        result = await arch_agent._design_flutter_architecture(task_data)
        print("✅ Test 3 PASSED: Agent handled partial project state gracefully")
        print(f"   Result type: {type(result)}")
        print(f"   Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
    except Exception as e:
        print(f"❌ Test 3 FAILED: {e}")
        return False
    finally:
        # Restore original method
        shared_state.get_project_state = original_get_project_state
    
    print("\n🎉 All Architecture Agent robustness tests PASSED!")
    return True

def test_path_utils():
    """Test path utilities for absolute path handling."""
    
    print("\n🧪 Testing Path Utilities...")
    
    from utils.path_utils import get_absolute_project_path, safe_join
    
    try:
        # Test basic project path resolution
        project_path = get_absolute_project_path("test_project")
        print(f"✅ get_absolute_project_path works: {project_path}")
        
        # Verify it's actually absolute
        if os.path.isabs(project_path):
            print("✅ Path is absolute")
        else:
            print("❌ Path is not absolute!")
            return False
            
        # Test safe_join
        joined_path = safe_join(project_path, "lib", "main.dart")
        print(f"✅ safe_join works: {joined_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Path utilities test failed: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting FlutterSwarm Robustness Tests")
    print("=" * 50)
    
    # Test 1: Architecture Agent robustness
    arch_test_passed = await test_architecture_agent_robustness()
    
    # Test 2: Path utilities
    path_test_passed = test_path_utils()
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    print(f"   Architecture Agent Robustness: {'✅ PASSED' if arch_test_passed else '❌ FAILED'}")
    print(f"   Path Utilities: {'✅ PASSED' if path_test_passed else '❌ FAILED'}")
    
    if arch_test_passed and path_test_passed:
        print("\n🎉 All tests PASSED! The fixes should resolve the KeyError issues.")
    else:
        print("\n❌ Some tests FAILED. Further investigation needed.")
    
    return arch_test_passed and path_test_passed

if __name__ == "__main__":
    asyncio.run(main())
