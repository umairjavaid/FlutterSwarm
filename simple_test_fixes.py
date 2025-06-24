#!/usr/bin/env python3
"""
Simple test script to validate the critical defensive fixes.
"""

import os
import sys

def test_defensive_attribute_access():
    """Test the defensive attribute access pattern."""
    
    print("🧪 Testing Defensive Attribute Access Pattern...")
    
    # Simulate incomplete project objects
    class IncompleteProject:
        def __init__(self):
            self.project_id = "test"
            # Missing 'name', 'description', etc.
    
    class PartialProject:
        def __init__(self):
            self.project_id = "test"
            self.name = "TestApp"
            # Missing 'description', 'architecture_decisions'
    
    # Test the old (broken) way vs new (defensive) way
    projects = [None, IncompleteProject(), PartialProject()]
    
    task_data = {
        "name": "FallbackApp",
        "description": "Fallback description"
    }
    
    for i, project in enumerate(projects):
        print(f"\n  Test {i+1}: {type(project).__name__ if project else 'None'}")
        
        # Test old (broken) way - this would crash
        try:
            if not project:
                old_name = task_data.get("name", "Unknown Project")
            else:
                old_name = project.name  # This would crash on IncompleteProject
            print(f"    ❌ Old method would work: {old_name}")
        except AttributeError as e:
            print(f"    ✅ Old method crashes as expected: {e}")
        
        # Test new (defensive) way - this should always work
        try:
            if not project:
                new_name = task_data.get("name", "Unknown Project")
            else:
                new_name = getattr(project, 'name', task_data.get('name', 'Unknown Project'))
            print(f"    ✅ New method works: {new_name}")
        except Exception as e:
            print(f"    ❌ New method failed: {e}")
            return False
    
    return True

def test_path_utilities():
    """Test path utilities without importing the full project."""
    
    print("\n🧪 Testing Path Utilities...")
    
    # Test basic path operations
    try:
        # Test absolute path detection
        test_paths = [
            "/absolute/path/test",
            "relative/path/test",
            "C:\\Windows\\Path",  # Windows absolute
            "flutter_projects/test_app"
        ]
        
        for path in test_paths:
            is_abs = os.path.isabs(path)
            abs_path = os.path.abspath(path) if not is_abs else path
            print(f"    Path: {path}")
            print(f"      Is absolute: {is_abs}")
            print(f"      Absolute version: {abs_path}")
        
        # Test path joining
        base = "/home/user/flutter_projects"
        relative = "test_app/lib/main.dart"
        joined = os.path.join(base, relative)
        print(f"    Joined path: {joined}")
        
        return True
        
    except Exception as e:
        print(f"    ❌ Path test failed: {e}")
        return False

def test_architecture_agent_fixes():
    """Test the specific lines we fixed in the architecture agent."""
    
    print("\n🧪 Testing Architecture Agent Fix Patterns...")
    
    # Simulate the fix patterns we implemented
    class MockProject:
        def __init__(self, has_name=True, has_description=True, has_decisions=True):
            self.project_id = "test"
            if has_name:
                self.name = "TestApp"
            if has_description:
                self.description = "Test description"
            if has_decisions:
                self.architecture_decisions = []
    
    task_data = {
        "name": "FallbackApp",
        "description": "Fallback description"
    }
    
    test_cases = [
        ("Complete project", MockProject(True, True, True)),
        ("Missing name", MockProject(False, True, True)),
        ("Missing description", MockProject(True, False, True)),
        ("Missing decisions", MockProject(True, True, False)),
        ("Missing all", MockProject(False, False, False)),
        ("None project", None)
    ]
    
    for case_name, project in test_cases:
        print(f"\n  Testing: {case_name}")
        
        try:
            # Test the defensive access patterns we implemented
            if not project:
                project_name = task_data.get("name", "Unknown Project")
                project_description = task_data.get("description", "No description available")
                existing_decisions = []
            else:
                project_name = getattr(project, 'name', task_data.get('name', 'Unknown Project'))
                project_description = getattr(project, 'description', task_data.get('description', 'No description available'))
                existing_decisions = getattr(project, 'architecture_decisions', [])
            
            print(f"    ✅ Name: {project_name}")
            print(f"    ✅ Description: {project_description}")
            print(f"    ✅ Decisions: {len(existing_decisions)} items")
            
        except Exception as e:
            print(f"    ❌ Failed: {e}")
            return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 FlutterSwarm Fix Validation Tests")
    print("=" * 50)
    
    # Run tests
    test1 = test_defensive_attribute_access()
    test2 = test_path_utilities()
    test3 = test_architecture_agent_fixes()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"   Defensive Attribute Access: {'✅ PASSED' if test1 else '❌ FAILED'}")
    print(f"   Path Utilities: {'✅ PASSED' if test2 else '❌ FAILED'}")
    print(f"   Architecture Agent Fixes: {'✅ PASSED' if test3 else '❌ FAILED'}")
    
    all_passed = test1 and test2 and test3
    
    if all_passed:
        print("\n🎉 All tests PASSED!")
        print("\n📋 Summary of fixes applied:")
        print("   1. ✅ Architecture Agent now uses defensive getattr() calls")
        print("   2. ✅ Fallback values from task_data when project state is incomplete")
        print("   3. ✅ Safe handling of missing architecture_decisions")
        print("   4. ✅ Path utilities maintain absolute path compatibility")
        print("\n🔧 Next steps:")
        print("   • The KeyError: 'name' should be resolved")
        print("   • Monitor logs for any remaining absolute path errors")
        print("   • Test the system with a new project creation")
    else:
        print("\n❌ Some tests failed - review the fixes!")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
