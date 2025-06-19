#!/usr/bin/env python3
"""
Basic test script to verify LangGraph implementation works.
"""

import os
import sys
import asyncio
from unittest.mock import patch, MagicMock

# Set up environment to avoid API key issues
os.environ['ANTHROPIC_API_KEY'] = 'test-key'

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...")
    
    try:
        # Test LangGraph imports
        from langgraph.graph import StateGraph, END
        print("✅ LangGraph imports successful")
        
        # Test FlutterSwarm imports with mocked agents
        with patch('agents.architecture_agent.ArchitectureAgent'), \
             patch('agents.implementation_agent.ImplementationAgent'), \
             patch('agents.testing_agent.TestingAgent'), \
             patch('agents.security_agent.SecurityAgent'), \
             patch('agents.devops_agent.DevOpsAgent'), \
             patch('agents.documentation_agent.DocumentationAgent'), \
             patch('agents.performance_agent.PerformanceAgent'), \
             patch('agents.quality_assurance_agent.QualityAssuranceAgent'):
            
            from langgraph_swarm import LangGraphFlutterSwarm, SwarmState
            print("✅ LangGraphFlutterSwarm imports successful")
            
            # Test initialization
            swarm = LangGraphFlutterSwarm(enable_monitoring=False)
            print("✅ LangGraphFlutterSwarm initialization successful")
            
            # Test project creation
            project_id = swarm.create_project("TestApp", "A test app")
            print(f"✅ Project creation successful: {project_id}")
            
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_workflow():
    """Test that the workflow can be executed."""
    print("\nTesting workflow execution...")
    
    try:
        # Mock all agents
        with patch('agents.architecture_agent.ArchitectureAgent') as mock_arch, \
             patch('agents.implementation_agent.ImplementationAgent') as mock_impl, \
             patch('agents.testing_agent.TestingAgent') as mock_test, \
             patch('agents.security_agent.SecurityAgent') as mock_sec, \
             patch('agents.devops_agent.DevOpsAgent') as mock_devops, \
             patch('agents.documentation_agent.DocumentationAgent') as mock_doc, \
             patch('agents.performance_agent.PerformanceAgent') as mock_perf, \
             patch('agents.quality_assurance_agent.QualityAssuranceAgent') as mock_qa:
            
            # Configure mock returns
            for mock_agent_class in [mock_arch, mock_impl, mock_test, mock_sec, 
                                   mock_devops, mock_doc, mock_perf, mock_qa]:
                mock_agent = mock_agent_class.return_value
                mock_agent.execute_task = MagicMock(return_value={"status": "completed"})
            
            from langgraph_swarm import LangGraphFlutterSwarm
            
            swarm = LangGraphFlutterSwarm(enable_monitoring=False)
            project_id = swarm.create_project("TestApp", "A test app")
            
            # Test a simple build (this should work without real agents)
            result = await swarm.build_project(
                project_id=project_id,
                name="TestApp",
                description="A test app",
                requirements=["basic_ui"],
                features=["home_screen"],
                platforms=["android"]
            )
            
            print(f"✅ Workflow execution successful: {result['status']}")
            print(f"✅ Progress: {result['overall_progress']}")
            print(f"✅ Completed phases: {len(result['completed_phases'])}")
            
        return True
        
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🐝 FlutterSwarm LangGraph Migration Test")
    print("=" * 50)
    
    # Test imports
    import_success = test_imports()
    
    if import_success:
        # Test workflow
        try:
            workflow_success = asyncio.run(test_workflow())
        except Exception as e:
            print(f"❌ Async test setup failed: {e}")
            workflow_success = False
    else:
        workflow_success = False
    
    print("\n" + "=" * 50)
    print("🎯 TEST SUMMARY:")
    print(f"  Imports: {'✅ PASS' if import_success else '❌ FAIL'}")
    print(f"  Workflow: {'✅ PASS' if workflow_success else '❌ FAIL'}")
    
    if import_success and workflow_success:
        print("\n🎉 LangGraph migration is working correctly!")
        return 0
    else:
        print("\n⚠️  LangGraph migration has issues that need attention.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
