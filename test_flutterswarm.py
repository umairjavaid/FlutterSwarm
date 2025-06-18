#!/usr/bin/env python3
"""
Simple test script to verify FlutterSwarm functionality.
"""

import asyncio
import sys
import os

# Add the parent directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flutter_swarm import FlutterSwarm

async def test_basic_functionality():
    """Test basic FlutterSwarm functionality."""
    print("🧪 Testing FlutterSwarm Basic Functionality")
    print("=" * 50)
    
    try:
        # Test 1: Create FlutterSwarm instance
        print("1. Creating FlutterSwarm instance...")
        swarm = FlutterSwarm()
        print("   ✅ FlutterSwarm created successfully")
        
        # Test 2: Create a project
        print("\n2. Creating test project...")
        project_id = swarm.create_project(
            name="TestApp",
            description="A simple test application",
            requirements=["Basic UI", "Navigation"],
            features=["ui", "navigation"]
        )
        print(f"   ✅ Project created with ID: {project_id}")
        
        # Test 3: Check project status
        print("\n3. Checking project status...")
        status = swarm.get_project_status(project_id)
        if 'project' in status:
            project = status['project']
            print(f"   ✅ Project found: {project['name']}")
            print(f"   📋 Current phase: {project['current_phase']}")
        else:
            print(f"   ❌ Project not found: {status}")
            
        # Test 4: Check agent status
        print("\n4. Checking agent status...")
        agent_status = swarm.get_agent_status()
        print(f"   ✅ Found {len(agent_status)} agents")
        
        for agent_id, info in agent_status.items():
            print(f"   🤖 {agent_id}: {info['status']}")
        
        # Test 5: List projects
        print("\n5. Listing projects...")
        projects = swarm.list_projects()
        print(f"   ✅ Found {len(projects)} projects")
        
        print("\n🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_agent_initialization():
    """Test agent initialization and communication."""
    print("\n\n🧪 Testing Agent Initialization")
    print("=" * 50)
    
    try:
        swarm = FlutterSwarm()
        
        # Check if all expected agents are initialized
        expected_agents = [
            "orchestrator", "architecture", "implementation", 
            "testing", "security", "devops", "documentation", "performance"
        ]
        
        print("Checking agent initialization...")
        for agent_id in expected_agents:
            if agent_id in swarm.agents:
                agent = swarm.agents[agent_id]
                print(f"   ✅ {agent_id}: {agent.agent_config['name']}")
            else:
                print(f"   ❌ {agent_id}: Not found")
                return False
        
        print(f"\n🎉 All {len(expected_agents)} agents initialized successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Agent initialization test failed: {e}")
        return False

async def test_shared_state():
    """Test shared state functionality."""
    print("\n\n🧪 Testing Shared State")
    print("=" * 50)
    
    try:
        from shared.state import shared_state
        
        # Test registering an agent
        print("1. Testing agent registration...")
        shared_state.register_agent("test_agent", ["testing"])
        agents = shared_state.get_agent_states()
        
        if "test_agent" in agents:
            print("   ✅ Agent registered successfully")
        else:
            print("   ❌ Agent registration failed")
            return False
        
        # Test creating a project
        print("\n2. Testing project creation...")
        project_id = shared_state.create_project(
            "TestProject", 
            "Test description", 
            ["Test requirement"]
        )
        
        project = shared_state.get_project_state(project_id)
        if project and project.name == "TestProject":
            print(f"   ✅ Project created: {project.name}")
        else:
            print("   ❌ Project creation failed")
            return False
        
        # Test message sending
        print("\n3. Testing message system...")
        from shared.state import MessageType
        
        message_id = shared_state.send_message(
            from_agent="test_agent",
            to_agent="test_agent",
            message_type=MessageType.STATUS_UPDATE,
            content={"test": "message"}
        )
        
        messages = shared_state.get_messages("test_agent")
        if messages and len(messages) > 0:
            print(f"   ✅ Message sent and received: {message_id}")
        else:
            print("   ❌ Message system failed")
            return False
        
        print("\n🎉 Shared state tests passed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Shared state test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("🚀 FlutterSwarm Test Suite")
    print("Testing core functionality...\n")
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Agent Initialization", test_agent_initialization), 
        ("Shared State", test_shared_state)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name} test...")
        
        try:
            if await test_func():
                passed += 1
                print(f"✅ {test_name} test PASSED")
            else:
                print(f"❌ {test_name} test FAILED")
        except Exception as e:
            print(f"❌ {test_name} test FAILED with exception: {e}")
    
    print(f"\n" + "=" * 60)
    print(f"🏁 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! FlutterSwarm is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Check the output above for details.")
        return False

if __name__ == "__main__":
    # Set environment variable to avoid Anthropic API calls during testing
    os.environ.setdefault("ANTHROPIC_API_KEY", "test-key-for-testing")
    
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
