#!/usr/bin/env python3
"""
Test script for verifying the FlutterSwarmGovernance implementation.
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the current directory to the Python path
sys.path.insert(0, os.getcwd())

def test_governance_import():
    """Test importing the governance module."""
    try:
        from langgraph_swarm import FlutterSwarmGovernance, ProjectGovernanceState
        print("✅ Successfully imported FlutterSwarmGovernance")
        return True
    except Exception as e:
        print(f"❌ Failed to import FlutterSwarmGovernance: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_governance_creation():
    """Test creating a governance instance."""
    try:
        from langgraph_swarm import FlutterSwarmGovernance
        
        print("🏛️ Creating FlutterSwarmGovernance instance...")
        governance = FlutterSwarmGovernance(enable_monitoring=False)
        print("✅ Successfully created FlutterSwarmGovernance instance")
        
        # Check if the execute_implementation_phase method exists
        if hasattr(governance, 'execute_implementation_phase'):
            print("✅ execute_implementation_phase method exists")
        else:
            print("❌ execute_implementation_phase method missing")
            return False
            
        # Check method signature
        import inspect
        sig = inspect.signature(governance.execute_implementation_phase)
        print(f"📋 Method signature: execute_implementation_phase{sig}")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create governance instance: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_implementation_phase():
    """Test the execute_implementation_phase method."""
    try:
        from langgraph_swarm import FlutterSwarmGovernance, ProjectGovernanceState
        
        print("🧪 Testing execute_implementation_phase method...")
        
        # Create governance instance
        governance = FlutterSwarmGovernance(enable_monitoring=False)
        
        # Create test state
        test_state = {
            "project_id": "test_123",
            "name": "Test Project",
            "description": "A test Flutter project",
            "requirements": ["Feature 1", "Feature 2"],
            "current_governance_phase": "implementation_oversight",
            "completed_governance_phases": ["project_initiation", "architecture_approval"],
            "quality_criteria_met": {},
            "project_health": "healthy"
        }
        
        # Test the method (this will likely fail due to missing agents, but we can test the method exists)
        print("🚀 Calling execute_implementation_phase...")
        result = await governance.execute_implementation_phase(test_state)
        
        print(f"📊 Result: {result}")
        print("✅ execute_implementation_phase method executed successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing execute_implementation_phase: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function."""
    print("🧪 Starting FlutterSwarmGovernance tests...")
    print("=" * 50)
    
    # Test 1: Import
    print("\n📦 Test 1: Module Import")
    import_success = test_governance_import()
    
    if not import_success:
        print("❌ Import test failed, stopping...")
        return
    
    # Test 2: Instance creation
    print("\n🏗️ Test 2: Instance Creation")
    creation_success = test_governance_creation()
    
    if not creation_success:
        print("❌ Creation test failed, stopping...")
        return
    
    # Test 3: Method execution
    print("\n⚙️ Test 3: Method Execution")
    try:
        asyncio.run(test_implementation_phase())
    except Exception as e:
        print(f"❌ Async test failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Tests completed!")

if __name__ == "__main__":
    main()
