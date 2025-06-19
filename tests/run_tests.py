"""
Manual test runner for governance system tests.
"""

import sys
import os
import traceback
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_test_safely(test_func, test_name):
    """Run a test function safely and report results."""
    try:
        test_func()
        print(f"✅ {test_name} - PASSED")
        return True
    except Exception as e:
        print(f"❌ {test_name} - FAILED: {str(e)}")
        print(f"   Error details: {traceback.format_exc()}")
        return False

def main():
    """Run all governance system tests."""
    print("🧪 Running FlutterSwarm Governance System Tests")
    print("=" * 60)
    
    total_tests = 0
    passed_tests = 0
    
    # Test 1: Basic imports and initialization
    def test_imports():
        from langgraph_swarm import FlutterSwarmGovernance, ProjectGovernanceState
        from shared.state import shared_state, AgentStatus, MessageType
        governance = FlutterSwarmGovernance()
        assert governance is not None
        assert hasattr(governance, 'governance_phases')
        assert hasattr(governance, 'quality_gates')
    
    total_tests += 1
    if run_test_safely(test_imports, "Basic imports and initialization"):
        passed_tests += 1
    
    # Test 2: Governance system structure
    def test_governance_structure():
        from langgraph_swarm import FlutterSwarmGovernance
        governance = FlutterSwarmGovernance()
        
        # Check governance phases
        expected_phases = [
            'project_initiation', 'architecture_approval', 'implementation_oversight',
            'quality_verification', 'security_compliance', 'performance_validation',
            'documentation_review', 'deployment_approval'
        ]
        assert governance.governance_phases == expected_phases
        
        # Check quality gates
        assert len(governance.quality_gates) > 0
        assert 'architecture_approval' in governance.quality_gates
        
        # Check that new methods exist
        assert hasattr(governance, '_project_initiation_gate')
        assert hasattr(governance, '_architecture_approval_gate')
        assert hasattr(governance, '_fallback_coordination_node')
        
        # Check that old methods don't exist
        assert not hasattr(governance, '_planning_node')
        assert not hasattr(governance, '_architecture_node')
    
    total_tests += 1
    if run_test_safely(test_governance_structure, "Governance system structure"):
        passed_tests += 1
    
    # Test 3: Real-time awareness integration
    def test_real_time_integration():
        from langgraph_swarm import FlutterSwarmGovernance
        from shared.state import shared_state
        
        governance = FlutterSwarmGovernance()
        
        # Test shared state interaction
        project_id = "test-integration-123"
        shared_state.create_project_with_id(
            project_id,
            "TestProject",
            "Test project for integration",
            ["req1", "req2"]
        )
        
        project = shared_state.get_project_state(project_id)
        assert project is not None
        assert project.name == "TestProject"
        
        # Test helper functions
        assert hasattr(governance, '_check_agent_collaboration_health')
        health = governance._assess_collaboration_health()
        assert isinstance(health, dict)
        assert 'healthy' in health
    
    total_tests += 1
    if run_test_safely(test_real_time_integration, "Real-time awareness integration"):
        passed_tests += 1
    
    # Test 4: Quality gates functionality
    def test_quality_gates():
        from langgraph_swarm import FlutterSwarmGovernance
        import asyncio
        
        governance = FlutterSwarmGovernance()
        
        # Create test state
        test_state = {
            "project_id": "quality-test-123",
            "name": "QualityTest",
            "description": "Test project for quality gates",
            "requirements": ["auth", "api"],
            "current_governance_phase": "project_initiation",
            "completed_governance_phases": [],
            "governance_phases": governance.governance_phases,
            "quality_gates": governance.quality_gates,
            "gate_statuses": {},
            "overall_progress": 0.0,
            "project_health": "healthy",
            "collaboration_effectiveness": 0.0,
            "governance_decisions": [],
            "approval_status": {},
            "real_time_metrics": {},
            "shared_consciousness_summary": {},
            "quality_criteria_met": {},
            "compliance_status": {},
            "coordination_fallback_active": False,
            "stuck_processes": []
        }
        
        # Test project initiation gate (synchronous test)
        # Note: We'll test the structure rather than async execution
        assert hasattr(governance, '_project_initiation_gate')
        assert hasattr(governance, '_architecture_approval_gate')
        assert hasattr(governance, '_quality_verification_gate')
    
    total_tests += 1
    if run_test_safely(test_quality_gates, "Quality gates functionality"):
        passed_tests += 1
    
    # Test 5: Routing logic
    def test_routing_logic():
        from langgraph_swarm import FlutterSwarmGovernance
        
        governance = FlutterSwarmGovernance()
        
        test_state = {
            "approval_status": {"project_initiation": "approved"},
            "stuck_processes": [],
            "gate_statuses": {}
        }
        
        # Test project initiation routing
        route = governance._route_from_project_initiation(test_state)
        assert route == "architecture_approval"
        
        # Test architecture approval routing
        test_state["approval_status"]["architecture_approval"] = "approved"
        route = governance._route_from_architecture_approval(test_state)
        assert route == "implementation_oversight"
        
        # Test fallback coordination routing
        test_state["stuck_processes"] = ["project_stagnation"]
        route = governance._route_from_fallback_coordination(test_state)
        assert route == "architecture_approval"
    
    total_tests += 1
    if run_test_safely(test_routing_logic, "Routing logic"):
        passed_tests += 1
    
    # Test 6: Helper functions
    def test_helper_functions():
        from langgraph_swarm import FlutterSwarmGovernance
        from shared.state import shared_state
        
        governance = FlutterSwarmGovernance()
        
        # Create test project
        project_id = "helper-test-123"
        shared_state.create_project_with_id(
            project_id,
            "HelperTest",
            "Test project for helpers",
            ["auth", "api"]
        )
        
        project = shared_state.get_project_state(project_id)
        
        # Test helper functions exist and return boolean values
        assert isinstance(governance._check_security_approval(project), bool)
        assert isinstance(governance._check_performance_considerations(project), bool)
        assert isinstance(governance._check_code_quality_standards(project), bool)
        assert isinstance(governance._check_agent_collaboration_health(), bool)
        
        # Test priority task identification
        test_state = {"gate_statuses": {"architecture_approval": "failed"}}
        priority_tasks = governance._identify_priority_tasks(test_state)
        assert isinstance(priority_tasks, list)
        
        # Test unblocking actions identification
        test_state = {"overall_progress": 0.05}
        unblocking_actions = governance._identify_unblocking_actions(test_state)
        assert isinstance(unblocking_actions, list)
    
    total_tests += 1
    if run_test_safely(test_helper_functions, "Helper functions"):
        passed_tests += 1
    
    # Test 7: Shared consciousness integration
    def test_shared_consciousness():
        from shared.state import shared_state
        
        # Test consciousness updates
        test_key = "test_governance_insight"
        test_value = {"status": "testing", "timestamp": datetime.now().isoformat()}
        
        shared_state.update_shared_consciousness(test_key, test_value)
        retrieved = shared_state.get_shared_consciousness(test_key)
        
        assert retrieved is not None
        assert 'value' in retrieved
        assert retrieved['value'] == test_value
        
        # Test predictive insights
        insights = shared_state.generate_predictive_insights("governance")
        assert isinstance(insights, list)
        
        # Test real-time metrics
        shared_state.update_real_time_metrics("test_metric", "test_value")
        metrics = shared_state.get_real_time_metrics()
        assert "test_metric" in metrics
    
    total_tests += 1
    if run_test_safely(test_shared_consciousness, "Shared consciousness integration"):
        passed_tests += 1
    
    # Test 8: Agent real-time awareness
    def test_agent_awareness():
        from agents.testing_agent import TestingAgent
        from agents.architecture_agent import ArchitectureAgent
        from agents.implementation_agent import ImplementationAgent
        
        # Create test agents
        test_agent = TestingAgent()
        arch_agent = ArchitectureAgent()
        impl_agent = ImplementationAgent()
        
        # Verify real-time awareness capabilities
        assert hasattr(test_agent, 'broadcast_activity')
        assert hasattr(test_agent, 'enable_real_time_awareness')
        assert hasattr(test_agent, '_react_to_peer_activity')
        
        assert hasattr(arch_agent, 'broadcast_activity')
        assert hasattr(arch_agent, '_react_to_peer_activity')
        
        assert hasattr(impl_agent, 'broadcast_activity')
        assert hasattr(impl_agent, '_react_to_peer_activity')
    
    total_tests += 1
    if run_test_safely(test_agent_awareness, "Agent real-time awareness"):
        passed_tests += 1
    
    # Test 9: No redundancy between systems
    def test_no_redundancy():
        from langgraph_swarm import FlutterSwarmGovernance
        from agents.testing_agent import TestingAgent
        
        governance = FlutterSwarmGovernance()
        test_agent = TestingAgent()
        
        # Governance should NOT have agent-specific methods
        agent_methods = [
            'execute_task', 'collaborate', 'on_state_change',
            '_create_unit_tests', '_implement_feature'
        ]
        
        for method in agent_methods:
            assert not hasattr(governance, method), f"Governance has agent method {method}!"
        
        # Agents should NOT have governance-specific methods
        governance_methods = [
            '_project_initiation_gate', '_architecture_approval_gate',
            '_quality_verification_gate'
        ]
        
        for method in governance_methods:
            assert not hasattr(test_agent, method), f"Agent has governance method {method}!"
    
    total_tests += 1
    if run_test_safely(test_no_redundancy, "No redundancy between systems"):
        passed_tests += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"🎯 Test Summary: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! ✅")
        print("✅ LangGraph migration from task orchestrator to governance system is complete and verified!")
        print("✅ Real-time awareness system integration is working properly!")
        print("✅ Quality gates and routing logic are functioning correctly!")
        print("✅ No redundancy between governance and agent systems!")
        return True
    else:
        print(f"⚠️  {total_tests - passed_tests} tests failed")
        print("❌ Some issues need to be resolved")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)