"""
Tests for routing logic in the governance system.
"""

import pytest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_swarm import FlutterSwarmGovernance


class TestRoutingLogic:
    """Test the routing logic between governance gates."""
    
    @pytest.fixture
    def governance_system(self):
        """Create a governance system for testing."""
        return FlutterSwarmGovernance()
    
    @pytest.fixture
    def sample_state(self):
        """Create a sample state for testing."""
        return {
            "project_id": "routing-test",
            "name": "RoutingTest",
            "description": "Test project for routing",
            "requirements": ["auth", "api"],
            "current_governance_phase": "project_initiation",
            "completed_governance_phases": [],
            "governance_phases": [
                'project_initiation', 'architecture_approval', 'implementation_oversight',
                'quality_verification', 'security_compliance', 'performance_validation',
                'documentation_review', 'deployment_approval'
            ],
            "quality_gates": {},
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
    
    def test_project_initiation_routing(self, governance_system, sample_state):
        """Test routing from project initiation gate."""
        # Test approved scenario
        sample_state['approval_status'] = {'project_initiation': 'approved'}
        route = governance_system._route_from_project_initiation(sample_state)
        assert route == "architecture_approval"
        
        # Test rejected scenario
        sample_state['approval_status'] = {'project_initiation': 'rejected'}
        route = governance_system._route_from_project_initiation(sample_state)
        assert route in ["fallback_coordination", "architecture_approval"]
        
        # Test pending scenario with healthy collaboration
        sample_state['approval_status'] = {'project_initiation': 'pending'}
        route = governance_system._route_from_project_initiation(sample_state)
        assert route in ["architecture_approval", "fallback_coordination"]
    
    def test_architecture_approval_routing(self, governance_system, sample_state):
        """Test routing from architecture approval gate."""
        # Test approved scenario
        sample_state['approval_status'] = {'architecture_approval': 'approved'}
        route = governance_system._route_from_architecture_approval(sample_state)
        assert route == "implementation_oversight"
        
        # Test rejected scenario
        sample_state['approval_status'] = {'architecture_approval': 'rejected'}
        route = governance_system._route_from_architecture_approval(sample_state)
        assert route in ["fallback_coordination", "end"]
        
        # Test pending scenario
        sample_state['approval_status'] = {'architecture_approval': 'pending'}
        route = governance_system._route_from_architecture_approval(sample_state)
        assert route in ["fallback_coordination", "end"]
    
    def test_implementation_oversight_routing(self, governance_system, sample_state):
        """Test routing from implementation oversight gate."""
        # Test approved scenario
        sample_state['approval_status'] = {'implementation_oversight': 'approved'}
        route = governance_system._route_from_implementation_oversight(sample_state)
        assert route == "quality_verification"
        
        # Test rejected scenario
        sample_state['approval_status'] = {'implementation_oversight': 'rejected'}
        route = governance_system._route_from_implementation_oversight(sample_state)
        assert route in ["architecture_approval", "fallback_coordination"]
        
        # Test pending scenario
        sample_state['approval_status'] = {'implementation_oversight': 'pending'}
        route = governance_system._route_from_implementation_oversight(sample_state)
        assert route == "fallback_coordination"
    
    def test_quality_verification_routing(self, governance_system, sample_state):
        """Test routing from quality verification gate."""
        # Test approved scenario
        sample_state['approval_status'] = {'quality_verification': 'approved'}
        route = governance_system._route_from_quality_verification(sample_state)
        assert route == "security_compliance"
        
        # Test rejected scenario
        sample_state['approval_status'] = {'quality_verification': 'rejected'}
        route = governance_system._route_from_quality_verification(sample_state)
        assert route == "implementation_oversight"
        
        # Test pending scenario
        sample_state['approval_status'] = {'quality_verification': 'pending'}
        route = governance_system._route_from_quality_verification(sample_state)
        assert route == "fallback_coordination"
    
    def test_security_compliance_routing(self, governance_system, sample_state):
        """Test routing from security compliance gate."""
        # Test approved scenario
        sample_state['approval_status'] = {'security_compliance': 'approved'}
        route = governance_system._route_from_security_compliance(sample_state)
        assert route == "performance_validation"
        
        # Test rejected scenario
        sample_state['approval_status'] = {'security_compliance': 'rejected'}
        route = governance_system._route_from_security_compliance(sample_state)
        assert route == "implementation_oversight"
        
        # Test pending scenario
        sample_state['approval_status'] = {'security_compliance': 'pending'}
        route = governance_system._route_from_security_compliance(sample_state)
        assert route == "fallback_coordination"
    
    def test_performance_validation_routing(self, governance_system, sample_state):
        """Test routing from performance validation gate."""
        # Test approved scenario
        sample_state['approval_status'] = {'performance_validation': 'approved'}
        route = governance_system._route_from_performance_validation(sample_state)
        assert route == "documentation_review"
        
        # Test rejected scenario
        sample_state['approval_status'] = {'performance_validation': 'rejected'}
        route = governance_system._route_from_performance_validation(sample_state)
        assert route == "implementation_oversight"
        
        # Test pending scenario
        sample_state['approval_status'] = {'performance_validation': 'pending'}
        route = governance_system._route_from_performance_validation(sample_state)
        assert route == "fallback_coordination"
    
    def test_documentation_review_routing(self, governance_system, sample_state):
        """Test routing from documentation review gate."""
        # Test approved scenario
        sample_state['approval_status'] = {'documentation_review': 'approved'}
        route = governance_system._route_from_documentation_review(sample_state)
        assert route == "deployment_approval"
        
        # Test rejected scenario
        sample_state['approval_status'] = {'documentation_review': 'rejected'}
        route = governance_system._route_from_documentation_review(sample_state)
        assert route == "quality_verification"
        
        # Test pending scenario
        sample_state['approval_status'] = {'documentation_review': 'pending'}
        route = governance_system._route_from_documentation_review(sample_state)
        assert route == "fallback_coordination"
    
    def test_fallback_coordination_routing(self, governance_system, sample_state):
        """Test routing from fallback coordination node."""
        # Test project stagnation scenario
        sample_state['stuck_processes'] = ['project_stagnation']
        route = governance_system._route_from_fallback_coordination(sample_state)
        assert route == "architecture_approval"
        
        # Test quality gate failures scenario
        sample_state['stuck_processes'] = ['quality_gate_failures']
        sample_state['gate_statuses'] = {'architecture_approval': 'failed'}
        route = governance_system._route_from_fallback_coordination(sample_state)
        assert route == "architecture_approval"
        
        # Test agent collaboration breakdown scenario
        sample_state['stuck_processes'] = ['agent_collaboration_breakdown']
        route = governance_system._route_from_fallback_coordination(sample_state)
        assert route == "implementation_oversight"
        
        # Test no specific issues scenario
        sample_state['stuck_processes'] = []
        route = governance_system._route_from_fallback_coordination(sample_state)
        assert route == "end"
    
    def test_routing_consistency(self, governance_system, sample_state):
        """Test that routing is consistent and logical."""
        # Test the complete flow for a successful project
        success_flow = []
        
        # Start with approved project initiation
        sample_state['approval_status'] = {'project_initiation': 'approved'}
        route = governance_system._route_from_project_initiation(sample_state)
        success_flow.append(route)
        assert route == "architecture_approval"
        
        # Approved architecture
        sample_state['approval_status']['architecture_approval'] = 'approved'
        route = governance_system._route_from_architecture_approval(sample_state)
        success_flow.append(route)
        assert route == "implementation_oversight"
        
        # Approved implementation
        sample_state['approval_status']['implementation_oversight'] = 'approved'
        route = governance_system._route_from_implementation_oversight(sample_state)
        success_flow.append(route)
        assert route == "quality_verification"
        
        # Approved quality
        sample_state['approval_status']['quality_verification'] = 'approved'
        route = governance_system._route_from_quality_verification(sample_state)
        success_flow.append(route)
        assert route == "security_compliance"
        
        # Approved security
        sample_state['approval_status']['security_compliance'] = 'approved'
        route = governance_system._route_from_security_compliance(sample_state)
        success_flow.append(route)
        assert route == "performance_validation"
        
        # Approved performance
        sample_state['approval_status']['performance_validation'] = 'approved'
        route = governance_system._route_from_performance_validation(sample_state)
        success_flow.append(route)
        assert route == "documentation_review"
        
        # Approved documentation
        sample_state['approval_status']['documentation_review'] = 'approved'
        route = governance_system._route_from_documentation_review(sample_state)
        success_flow.append(route)
        assert route == "deployment_approval"
        
        # Verify the complete successful flow
        expected_flow = [
            "architecture_approval", "implementation_oversight", "quality_verification",
            "security_compliance", "performance_validation", "documentation_review",
            "deployment_approval"
        ]
        assert success_flow == expected_flow
    
    def test_fallback_routing_scenarios(self, governance_system, sample_state):
        """Test various fallback routing scenarios."""
        # Test that rejected gates route to appropriate fallback
        rejection_scenarios = [
            ('architecture_approval', 'rejected', ['fallback_coordination', 'end']),
            ('implementation_oversight', 'rejected', ['architecture_approval', 'fallback_coordination']),
            ('quality_verification', 'rejected', ['implementation_oversight']),
            ('security_compliance', 'rejected', ['implementation_oversight']),
            ('performance_validation', 'rejected', ['implementation_oversight']),
            ('documentation_review', 'rejected', ['quality_verification'])
        ]
        
        for gate, status, expected_routes in rejection_scenarios:
            sample_state['approval_status'] = {gate: status}
            route_method = getattr(governance_system, f'_route_from_{gate}')
            route = route_method(sample_state)
            assert route in expected_routes, f"Gate {gate} with status {status} routed to {route}, expected one of {expected_routes}"


if __name__ == "__main__":
    # Run tests manually
    print("🧪 Running Routing Logic Tests...")
    
    test_routing = TestRoutingLogic()
    governance = FlutterSwarmGovernance()
    
    # Create sample state
    sample_state = {
        "project_id": "manual-routing-test",
        "name": "ManualRoutingTest",
        "description": "Manual test for routing",
        "requirements": ["auth"],
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
    
    # Test project initiation routing
    test_routing.test_project_initiation_routing(governance, sample_state)
    print("✅ Project initiation routing test passed")
    
    # Test architecture approval routing
    test_routing.test_architecture_approval_routing(governance, sample_state)
    print("✅ Architecture approval routing test passed")
    
    # Test routing consistency
    test_routing.test_routing_consistency(governance, sample_state)
    print("✅ Routing consistency test passed")
    
    # Test fallback routing scenarios
    test_routing.test_fallback_routing_scenarios(governance, sample_state)
    print("✅ Fallback routing scenarios test passed")
    
    print("\n🎉 All routing logic tests passed!")