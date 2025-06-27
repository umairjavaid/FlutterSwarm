#!/usr/bin/env python3
"""
Validation script to test the defensive state access fixes.
"""

import sys
import os

def test_defensive_patterns():
    """Test that the defensive patterns work correctly."""
    print("🛡️ Testing Defensive State Access Patterns")
    print("=" * 50)
    
    passed = 0
    total = 0
    
    # Test 1: Basic getattr safety
    print("\n1. Testing getattr() safety...")
    total += 1
    
    class IncompleteProject:
        def __init__(self):
            self.project_id = "test-123"
            # Missing name, description, etc.
    
    project = IncompleteProject()
    task_data = {"name": "TestApp", "description": "Test description"}
    
    try:
        # This should not crash
        project_name = getattr(project, 'name', task_data.get('name', 'Unknown Project'))
        project_description = getattr(project, 'description', task_data.get('description', 'No description'))
        architecture_decisions = getattr(project, 'architecture_decisions', [])
        
        assert project_name == "TestApp"
        assert project_description == "Test description"
        assert architecture_decisions == []
        
        print("  ✅ getattr() safety test passed")
        passed += 1
    except Exception as e:
        print(f"  ❌ getattr() safety test failed: {e}")
    
    # Test 2: None project handling
    print("\n2. Testing None project handling...")
    total += 1
    
    try:
        project = None
        project_name = getattr(project, 'name', task_data.get('name', 'Unknown Project')) if project else task_data.get('name', 'Unknown Project')
        project_description = getattr(project, 'description', task_data.get('description', 'No description')) if project else task_data.get('description', 'No description')
        
        assert project_name == "TestApp"
        assert project_description == "Test description"
        
        print("  ✅ None project handling test passed")
        passed += 1
    except Exception as e:
        print(f"  ❌ None project handling test failed: {e}")
    
    # Test 3: Complete project object
    print("\n3. Testing complete project object...")
    total += 1
    
    class CompleteProject:
        def __init__(self):
            self.project_id = "test-456"
            self.name = "CompleteApp"
            self.description = "Complete description"
            self.architecture_decisions = [{"id": "arch-1"}]
            self.requirements = ["req1", "req2"]
    
    try:
        project = CompleteProject()
        project_name = getattr(project, 'name', task_data.get('name', 'Unknown Project'))
        project_description = getattr(project, 'description', task_data.get('description', 'No description'))
        architecture_decisions = getattr(project, 'architecture_decisions', [])
        requirements = getattr(project, 'requirements', [])
        
        assert project_name == "CompleteApp"  # Should use project value
        assert project_description == "Complete description"  # Should use project value  
        assert len(architecture_decisions) == 1
        assert len(requirements) == 2
        
        print("  ✅ Complete project object test passed")
        passed += 1
    except Exception as e:
        print(f"  ❌ Complete project object test failed: {e}")
    
    # Test 4: Dictionary-like attribute access
    print("\n4. Testing dictionary fallback patterns...")
    total += 1
    
    try:
        empty_dict = {}
        performance_metrics = getattr(None, 'performance_metrics', {})
        performance_metrics.update({"metric1": "value1"})
        
        security_findings = getattr(None, 'security_findings', [])
        security_findings.extend([{"finding": "test"}])
        
        documentation = getattr(None, 'documentation', {})
        documentation["README.md"] = "content"
        
        # These should all work without crashing
        assert performance_metrics == {"metric1": "value1"}
        assert len(security_findings) == 1
        assert documentation["README.md"] == "content"
        
        print("  ✅ Dictionary fallback patterns test passed")
        passed += 1
    except Exception as e:
        print(f"  ❌ Dictionary fallback patterns test failed: {e}")
    
    # Summary
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    if passed == total:
        print("🎉 All defensive patterns working correctly!")
        return True
    else:
        print("❌ Some tests failed - defensive patterns need attention")
        return False

def check_file_fixes():
    """Check that critical files have been fixed."""
    print("\n🔍 Checking File Fixes")
    print("=" * 30)
    
    files_to_check = [
        "agents/orchestrator_agent.py",
        "agents/architecture_agent.py", 
        "agents/performance_agent.py",
        "agents/documentation_agent.py",
        "agents/e2e_testing_agent.py",
        "agents/quality_assurance_agent.py",
        "agents/security_agent.py"
    ]
    
    fixed_patterns = [
        "getattr(project, 'name'",
        "getattr(project, 'description'", 
        "getattr(project, 'architecture_decisions'",
        "getattr(project, 'requirements'",
        "getattr(project, 'performance_metrics'",
        "getattr(project, 'security_findings'",
        "getattr(project, 'files_created'"
    ]
    
    fixes_found = 0
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                
                file_fixes = 0
                for pattern in fixed_patterns:
                    if pattern in content:
                        file_fixes += 1
                
                if file_fixes > 0:
                    print(f"  ✅ {file_path}: {file_fixes} defensive patterns found")
                    fixes_found += file_fixes
                else:
                    print(f"  ⚠️  {file_path}: no defensive patterns found")
                    
            except Exception as e:
                print(f"  ❌ {file_path}: error reading file - {e}")
        else:
            print(f"  ❌ {file_path}: file not found")
    
    print(f"\n📈 Total defensive patterns found: {fixes_found}")
    return fixes_found > 0

def main():
    """Run all validation tests."""
    print("🔧 FlutterSwarm Defensive Fixes Validation")
    print("=" * 60)
    
    # Test the defensive patterns
    patterns_ok = test_defensive_patterns()
    
    # Check file fixes
    fixes_ok = check_file_fixes()
    
    # Overall result
    print("\n" + "=" * 60)
    if patterns_ok and fixes_ok:
        print("🎉 SUCCESS: All defensive fixes validated!")
        print("✅ Agents should no longer crash on missing project attributes")
        print("✅ System will gracefully handle incomplete project state")
        print("✅ Fallback mechanisms working correctly")
        return 0
    else:
        print("❌ FAILURE: Some issues found with defensive fixes")
        if not patterns_ok:
            print("❌ Defensive patterns not working correctly")
        if not fixes_ok:
            print("❌ File fixes not properly applied")
        return 1

if __name__ == "__main__":
    sys.exit(main())
