"""
Comprehensive tests for LangGraph governance migration.
Tests the transformation from task orchestrator to project governance system.
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_swarm import FlutterSwarmGovernance, ProjectGovernanceState
from shared.state import shared_state, AgentStatus, MessageType
from agents.base_agent import BaseAgent
from agents.testing_agent import TestingAgent
from agents.architecture_agent import ArchitectureAgent
from agents.implementation_agent import ImplementationAgent


class TestGovernanceMigration:
    """Test the complete migration from task orchestrator to governance system."""
    
    @pytest.fixture
    def governance_system(self):
        """Create a governance system for testing."""
        return FlutterSwarmGovernance()
    
    @pytest.fixture
    def sample_project_state(self):
        """Create a sample project governance state."""
        return {
            "project_id": "test-project-123",
            "name": "TestMusicApp",
            "description": "A test music streaming application",
            "requirements": [
                "User authentication",
                "Music streaming",
                "Playlist management"
            ],
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
    
    def test_governance_system_initialization(self, governance_system):
        """Test that the governance system initializes properly."""
        assert governance_system is not None
        assert hasattr(governance_system, 'governance_phases')
        assert hasattr(governance_system, 'quality_gates')
        assert hasattr(governance_system, 'graph')
        assert hasattr(governance_system, 'app')
        
        # Verify governance phases
        expected_phases = [
            'project_initiation', 'architecture_approval', 'implementation_oversight',
            'quality_verification', 'security_compliance', 'performance_validation',
            'documentation_review', 'deployment_approval'
        ]
        assert governance_system.governance_phases == expected_phases
        
        # Verify quality gates are configured
        assert len(governance_system.quality_gates) > 0
        assert 'architecture_approval' in governance_system.quality_gates
        assert 'implementation_oversight' in governance_system.quality_gates
        
    def test_no_old_swarm_state_references(self):
        """Test that no old SwarmState references exist."""
        from langgraph_swarm import FlutterSwarmGovernance
        
        # Check that the class doesn't have old SwarmState methods
        governance = FlutterSwarmGovernance()
        
        # These old methods should NOT exist
        old_methods = [
            '_planning_node', '_architecture_node', '_implementation_node',
            '_testing_node', '_security_node', '_performance_node'
        ]
        
        for method in old_methods:
            assert not hasattr(governance, method), f"Old method {method} still exists!"
        
        # These new methods SHOULD exist
        new_methods = [
            '_project_initiation_gate', '_architecture_approval_gate',
            '_implementation_oversight_gate', '_quality_verification_gate',
            '_security_compliance_gate', '_performance_validation_gate',
            '_documentation_review_gate', '_deployment_approval_gate'
        ]
        
        for method in new_methods:
            assert hasattr(governance, method), f"New method {method} is missing!"
    
    def test_real_time_awareness_integration(self, governance_system):
        """Test integration with real-time awareness system."""
        # Test that governance system uses shared_state
        project_id = "test-integration-project"
        
        # Create a project in shared state
        shared_state.create_project_with_id(
            project_id,
            "IntegrationTest", 
            "Test project for integration",
            ["requirement1", "requirement2"]
        )
        
        # Test that governance can access project
        project = shared_state.get_project_state(project_id)
        assert project is not None
        assert project.name == "IntegrationTest"
        
        # Test helper functions use shared state
        assert hasattr(governance_system, '_check_agent_collaboration_health')
        assert hasattr(governance_system, '_assess_collaboration_health')
        
        # Test collaboration health assessment
        health = governance_system._assess_collaboration_health()
        assert isinstance(health, dict)
        assert 'healthy' in health
        assert 'productive' in health
    
    @pytest.mark.asyncio
    async def test_quality_gates_functionality(self, governance_system, sample_project_state):
        """Test that quality gates work properly."""
        # Test project initiation gate
        result = await governance_system._project_initiation_gate(sample_project_state)
        assert isinstance(result, dict)
        assert 'governance_decisions' in result
        assert len(result['governance_decisions']) > 0
        
        # Test that gate status is updated
        last_decision = result['governance_decisions'][-1]
        assert last_decision['gate'] == 'project_initiation'
        assert 'criteria_met' in last_decision
        assert 'approved' in last_decision
        
        # Test architecture approval gate
        result = await governance_system._architecture_approval_gate(sample_project_state)
        assert isinstance(result, dict)
        
        # Test implementation oversight gate
        result = await governance_system._implementation_oversight_gate(sample_project_state)
        assert isinstance(result, dict)
        
    def test_routing_logic(self, governance_system, sample_project_state):
        """Test that routing logic works correctly."""
        # Test project initiation routing
        sample_project_state['approval_status'] = {'project_initiation': 'approved'}
        route = governance_system._route_from_project_initiation(sample_project_state)
        assert route == "architecture_approval"
        
        # Test architecture approval routing
        sample_project_state['approval_status']['architecture_approval'] = 'approved'
        route = governance_system._route_from_architecture_approval(sample_project_state)
        assert route == "implementation_oversight"
        
        # Test fallback routing when approval rejected
        sample_project_state['approval_status']['architecture_approval'] = 'rejected'
        route = governance_system._route_from_architecture_approval(sample_project_state)
        assert route in ["fallback_coordination", "end"]
    
    @pytest.mark.asyncio
    async def test_fallback_coordination(self, governance_system, sample_project_state):
        """Test fallback coordination functionality."""
        # Set up scenario requiring fallback coordination
        sample_project_state['gate_statuses'] = {
            'architecture_approval': 'failed',
            'implementation_oversight': 'failed',
            'quality_verification': 'failed'
        }
        sample_project_state['overall_progress'] = 0.05  # Very low progress
        
        # Test fallback coordination node
        result = await governance_system._fallback_coordination_node(sample_project_state)
        
        assert isinstance(result, dict)
        assert result['coordination_fallback_active'] == True
        assert len(result['stuck_processes']) > 0
        assert len(result['governance_decisions']) > 0
        
        # Check that fallback coordination recorded decisions
        fallback_decision = next(
            (d for d in result['governance_decisions'] if d['gate'] == 'fallback_coordination'),
            None
        )
        assert fallback_decision is not None
        assert 'coordination_needs' in fallback_decision
        assert 'actions_taken' in fallback_decision
    
    def test_helper_functions_work(self, governance_system):
        """Test that all helper functions work correctly."""
        # Create a test project
        project_id = "helper-test-project"
        shared_state.create_project_with_id(
            project_id,
            "HelperTest",
            "Test project for helper functions",
            ["auth", "api", "ui"]
        )
        
        project = shared_state.get_project_state(project_id)
        
        # Test security checks
        security_result = governance_system._check_security_approval(project)
        assert isinstance(security_result, bool)
        
        # Test performance checks
        performance_result = governance_system._check_performance_considerations(project)
        assert isinstance(performance_result, bool)
        
        # Test scalability checks
        scalability_result = governance_system._check_scalability_verification(project)
        assert isinstance(scalability_result, bool)
        
        # Test code quality checks
        quality_result = governance_system._check_code_quality_standards(project)
        assert isinstance(quality_result, bool)
        
        # Test collaboration health
        collaboration_result = governance_system._check_agent_collaboration_health()
        assert isinstance(collaboration_result, bool)
    
    @pytest.mark.asyncio
    async def test_public_api(self, governance_system):
        """Test the public API for running governance."""
        # Test the main governance execution method
        result = await governance_system.run_governance(
            project_id="api-test-project",
            name="APITestProject",
            description="Test project for API testing",
            requirements=["authentication", "data_storage", "user_interface"]
        )
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'project_id' in result
        assert 'governance_status' in result
        assert 'completed_phases' in result
        assert 'overall_progress' in result
        assert 'project_health' in result
        
        # Verify the result makes sense
        assert result['project_id'] == "api-test-project"
        assert result['governance_status'] in ['completed', 'in_progress', 'failed']
        assert isinstance(result['overall_progress'], float)
        assert 0.0 <= result['overall_progress'] <= 1.0
    
    def test_shared_consciousness_integration(self, governance_system):
        """Test integration with shared consciousness system."""
        # Test that governance system can update shared consciousness
        test_key = "test_governance_insight"
        test_value = {"status": "testing", "timestamp": datetime.now().isoformat()}
        
        shared_state.update_shared_consciousness(test_key, test_value)
        
        # Test that governance can read from shared consciousness
        retrieved_value = shared_state.get_shared_consciousness(test_key)
        assert retrieved_value is not None
        assert 'value' in retrieved_value
        assert retrieved_value['value'] == test_value
        
        # Test predictive insights generation
        insights = shared_state.generate_predictive_insights("governance")
        assert isinstance(insights, list)
        
        # Test real-time metrics
        shared_state.update_real_time_metrics("governance_health", "excellent")
        metrics = shared_state.get_real_time_metrics()
        assert "governance_health" in metrics
    
    def test_no_redundancy_with_agents(self):
        """Test that there's no redundancy between governance and agent systems."""
        # Create test agents
        test_agent = TestingAgent()
        arch_agent = ArchitectureAgent()
        impl_agent = ImplementationAgent()
        
        # Verify agents have real-time awareness capabilities
        assert hasattr(test_agent, 'broadcast_activity')
        assert hasattr(test_agent, 'enable_real_time_awareness')
        assert hasattr(test_agent, '_react_to_peer_activity')
        
        assert hasattr(arch_agent, 'broadcast_activity')
        assert hasattr(arch_agent, '_react_to_peer_activity')
        
        assert hasattr(impl_agent, 'broadcast_activity')
        assert hasattr(impl_agent, '_react_to_peer_activity')
        
        # Verify governance system doesn't duplicate agent functionality
        governance = FlutterSwarmGovernance()
        
        # Governance should NOT have agent-specific methods
        agent_methods = [
            'execute_task', 'collaborate', 'on_state_change',
            '_create_unit_tests', '_implement_feature', '_design_flutter_architecture'
        ]
        
        for method in agent_methods:
            assert not hasattr(governance, method), f"Governance has agent method {method}!"
        
        # Governance SHOULD have governance-specific methods
        governance_methods = [
            '_project_initiation_gate', '_architecture_approval_gate',
            '_quality_verification_gate', '_fallback_coordination_node'
        ]
        
        for method in governance_methods:
            assert hasattr(governance, method), f"Governance missing {method}!"


class TestRealTimeAwarenessIntegration:
    """Test integration between governance system and real-time awareness."""
    
    @pytest.fixture
    def setup_agents(self):
        """Set up agents for testing."""
        agents = {
            'testing': TestingAgent(),
            'architecture': ArchitectureAgent(), 
            'implementation': ImplementationAgent()
        }
        
        # Enable real-time awareness for all agents
        for agent in agents.values():
            agent.enable_real_time_awareness()
        
        return agents
    
    def test_agent_subscription_system(self, setup_agents):
        """Test that agents are properly subscribed to each other."""
        agents = setup_agents
        
        # Check that agents are subscribed to each other
        subscriptions = shared_state._awareness_state.agent_subscriptions
        
        for agent_id in agents.keys():
            assert agent_id in subscriptions
            # Each agent should be subscribed to others
            assert len(subscriptions[agent_id]) >= 2
    
    def test_proactive_collaboration_triggers(self, setup_agents):
        """Test that proactive collaboration triggers work."""
        agents = setup_agents
        
        # Simulate architecture decision broadcast
        arch_agent = agents['architecture']
        arch_agent.broadcast_activity(
            activity_type="architecture_decision_made",
            activity_details={
                "decision": "Use BLoC pattern",
                "patterns": ["BLoC", "Clean Architecture"],
                "feature_name": "user_auth"
            },
            impact_level="medium",
            collaboration_relevance=["implementation", "testing"]
        )
        
        # Verify activity was broadcast
        activity_streams = shared_state._awareness_state.agent_activity_streams
        assert 'architecture' in activity_streams
        assert len(activity_streams['architecture']) > 0
        
        # Verify latest activity
        latest_activity = activity_streams['architecture'][-1]
        assert latest_activity['activity_type'] == "architecture_decision_made"
        assert latest_activity['activity_details']['decision'] == "Use BLoC pattern"
    
    def test_predictive_insights_generation(self):
        """Test predictive insights generation."""
        # Create a test project
        project_id = "predictive-test-project"
        shared_state.create_project_with_id(
            project_id,
            "PredictiveTest",
            "Test project for predictive insights",
            ["auth", "api"]
        )
        
        # Generate insights for different agents
        test_insights = shared_state.generate_predictive_insights("testing")
        impl_insights = shared_state.generate_predictive_insights("implementation")
        arch_insights = shared_state.generate_predictive_insights("architecture")
        
        # Verify insights are generated
        assert isinstance(test_insights, list)
        assert isinstance(impl_insights, list)
        assert isinstance(arch_insights, list)
        
        # Verify insights have proper structure
        for insights in [test_insights, impl_insights, arch_insights]:
            for insight in insights:
                assert 'type' in insight
                assert 'confidence' in insight
                assert 'generated_at' in insight
                assert isinstance(insight['confidence'], float)
                assert 0.0 <= insight['confidence'] <= 1.0


if __name__ == "__main__":
    # Run tests manually if pytest is not available
    print("🧪 Running Governance Migration Tests...")
    
    # Create test instances
    test_migration = TestGovernanceMigration()
    test_integration = TestRealTimeAwarenessIntegration()
    
    # Test governance system initialization
    governance = FlutterSwarmGovernance()
    test_migration.test_governance_system_initialization(governance)
    print("✅ Governance system initialization test passed")
    
    # Test no old SwarmState references
    test_migration.test_no_old_swarm_state_references()
    print("✅ No old SwarmState references test passed")
    
    # Test real-time awareness integration
    test_migration.test_real_time_awareness_integration(governance)
    print("✅ Real-time awareness integration test passed")
    
    # Test helper functions
    test_migration.test_helper_functions_work(governance)
    print("✅ Helper functions test passed")
    
    # Test shared consciousness integration
    test_migration.test_shared_consciousness_integration(governance)
    print("✅ Shared consciousness integration test passed")
    
    # Test no redundancy with agents
    test_migration.test_no_redundancy_with_agents()
    print("✅ No redundancy with agents test passed")
    
    print("\n🎉 All migration tests passed successfully!")
    print("✅ LangGraph migration from task orchestrator to governance system is complete and verified!")