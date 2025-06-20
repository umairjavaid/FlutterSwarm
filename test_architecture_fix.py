#!/usr/bin/env python3
"""
Test the architecture agent fix
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_architecture_agent():
    """Test the architecture agent directly."""
    try:
        from agents.architecture_agent import ArchitectureAgent
        print("✅ ArchitectureAgent imported successfully!")
        
        arch_agent = ArchitectureAgent()
        print("✅ ArchitectureAgent created successfully!")
        
        # Test execute_task with sample data
        task_data = {
            "project_id": "test-project-123",
            "name": "TestApp",
            "description": "A test Flutter application",
            "requirements": [
                "User authentication",
                "Todo CRUD operations",
                "Offline synchronization"
            ]
        }
        
        print("🧪 Testing architecture design...")
        result = await arch_agent.execute_task("design_flutter_architecture", task_data)
        
        if result and result.get('architecture_design'):
            print("✅ Architecture design completed successfully!")
            print(f"📋 Result: {result}")
            return True
        else:
            print("❌ Architecture design failed or returned no design")
            print(f"📋 Result: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing architecture agent: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_governance_with_fallback():
    """Test the governance system with fallback coordination."""
    try:
        from langgraph_swarm import FlutterSwarmGovernance
        print("✅ FlutterSwarmGovernance imported successfully!")
        
        governance = FlutterSwarmGovernance()
        print("✅ FlutterSwarmGovernance created successfully!")
        
        # Create a test project
        project_id = governance.create_project(
            name="TestApp",
            description="A test Flutter application",
            requirements=[
                "User authentication",
                "Todo CRUD operations",
                "Offline synchronization"
            ]
        )
        
        print(f"✅ Test project created with ID: {project_id}")
        
        # Test the governance system
        print("🧪 Testing governance workflow...")
        result = await governance.run_governance(
            project_id=project_id,
            name="TestApp",
            description="A test Flutter application",
            requirements=[
                "User authentication",
                "Todo CRUD operations",
                "Offline synchronization"
            ]
        )
        
        print(f"📋 Governance result: {result}")
        
        # Check if we have architecture decisions now
        from shared.state import shared_state
        project = shared_state.get_project_state(project_id)
        if project and hasattr(project, 'architecture_decisions') and len(project.architecture_decisions) > 0:
            print("✅ Architecture decisions were created!")
            print(f"📋 Architecture decisions: {len(project.architecture_decisions)}")
            for decision in project.architecture_decisions:
                print(f"   - {decision.get('title', 'Unknown')}")
            return True
        else:
            print("❌ No architecture decisions were created")
            return False
            
    except Exception as e:
        print(f"❌ Error testing governance: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("🧪 Testing FlutterSwarm Architecture Agent Fix")
    print("=" * 50)
    
    # Test 1: Architecture agent directly
    print("\n🧪 Test 1: Architecture Agent Direct Test")
    arch_test_passed = await test_architecture_agent()
    
    # Test 2: Governance system with fallback
    print("\n🧪 Test 2: Governance System with Fallback")
    governance_test_passed = await test_governance_with_fallback()
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 50)
    print(f"Architecture Agent Test: {'✅ PASSED' if arch_test_passed else '❌ FAILED'}")
    print(f"Governance System Test: {'✅ PASSED' if governance_test_passed else '❌ FAILED'}")
    
    if arch_test_passed and governance_test_passed:
        print("\n🎉 All tests PASSED! The architecture agent fix is working!")
        return True
    else:
        print("\n⚠️ Some tests FAILED. Issues still remain.")
        return False

if __name__ == "__main__":
    asyncio.run(main())
