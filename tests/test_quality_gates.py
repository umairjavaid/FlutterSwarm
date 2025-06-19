"""
Tests for quality gates functionality in the governance system.
"""

import pytest
import asyncio
import sys
import os
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langgraph_swarm import FlutterSwarmGovernance, ProjectGovernanceState
from shared.state import shared_state


class TestQualityGates:
    """Test the quality gates system."""
    
    @pytest.fixture
    def governance_system(self):
        """Create a governance system for testing."""
        return FlutterSwarmGovernance()
    
    @pytest.fixture
    def base_project_state(self):
        """Create a base project state for testing."""
        return {
            "project_id": "quality-gate-test",
            "name": "QualityGateTest",
            "description": "Test project for quality gates",
            "requirements": ["auth", "api", "ui"],
            "current_governance_phase": "project_initiation",
            "completed_governance_phases": [],
            "governance_phases": [
                'project_initiation', 'architecture_approval', 'implementation_oversight',
                'quality_verification', 'security_compliance', 'performance_validation',
                'documentation_review', 'deployment_approval'
            ],
            "quality_gates": {},
            "gate_statuses": {phase: "pending" for phase in [
                'project_initiation', 'architecture_approval', 'implementation_oversight',
                'quality_verification', 'security_compliance', 'performance_validation',
                'documentation_review', 'deployment_approval'
            ]},
            "overall_progress": 0.0,
            "project_health": "healthy",
            "collaboration_effectiveness": 0.0,
            "governance_decisions": [],
            "approval_status": {phase: "pending" for phase in [
                'project_initiation', 'architecture_approval', 'implementation_oversight',
                'quality_verification', 'security_compliance', 'performance_validation',
                'documentation_review', 'deployment_approval'
            ]},
            "real_time_metrics": {},
            "shared_consciousness_summary": {},
            "quality_criteria_met": {},
            "compliance_status": {},
            "coordination_fallback_active": False,
            "stuck_processes": []
        }
    
    @pytest.mark.asyncio
    async def test_project_initiation_gate(self, governance_system, base_project_state):
        """Test project initiation gate."""
        # Test with valid project
        result = await governance_system._project_initiation_gate(base_project_state)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'governance_decisions' in result
        assert 'gate_statuses' in result
        assert 'approval_status' in result
        
        # Verify decision was recorded
        decisions = result['governance_decisions']
        assert len(decisions) > 0
        
        initiation_decision = next(
            (d for d in decisions if d['gate'] == 'project_initiation'), None
        )
        assert initiation_decision is not None
        assert 'criteria_met' in initiation_decision
        assert 'approved' in initiation_decision
        
        # Verify gate status was updated
        assert result['gate_statuses']['project_initiation'] in ['passed', 'failed']
        assert result['approval_status']['project_initiation'] in ['approved', 'rejected']
    
    @pytest.mark.asyncio
    async def test_architecture_approval_gate(self, governance_system, base_project_state):
        """Test architecture approval gate."""
        # Create a project with architecture decisions
        project_id = base_project_state['project_id']
        shared_state.create_project_with_id(
            project_id,
            base_project_state['name'],
            base_project_state['description'],
            base_project_state['requirements']
        )
        
        # Add some architecture decisions to the project
        project = shared_state.get_project_state(project_id)
        project.architecture_decisions.append({
            'decision_id': 'arch_001',
            'title': 'State Management Pattern',
            'description': 'Use BLoC pattern for state management',
            'type': 'architecture',
            'status': 'approved'
        })
        
        result = await governance_system._architecture_approval_gate(base_project_state)
        
        # Verify result
        assert isinstance(result, dict)
        assert 'governance_decisions' in result
        
        # Check that architecture criteria were evaluated
        arch_decision = next(
            (d for d in result['governance_decisions'] if d['gate'] == 'architecture_approval'), None
        )
        assert arch_decision is not None
        assert 'criteria_met' in arch_decision
        assert 'architecture_design_complete' in arch_decision['criteria_met']
    
    @pytest.mark.asyncio
    async def test_implementation_oversight_gate(self, governance_system, base_project_state):
        """Test implementation oversight gate."""
        result = await governance_system._implementation_oversight_gate(base_project_state)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'governance_decisions' in result
        assert 'overall_progress' in result
        
        # Verify implementation criteria were checked
        impl_decision = next(
            (d for d in result['governance_decisions'] if d['gate'] == 'implementation_oversight'), None
        )
        assert impl_decision is not None
        assert 'criteria_met' in impl_decision
        assert 'collaboration_health' in impl_decision
        
        # Verify progress was calculated
        assert isinstance(result['overall_progress'], float)
        assert 0.0 <= result['overall_progress'] <= 1.0
    
    @pytest.mark.asyncio
    async def test_quality_verification_gate(self, governance_system, base_project_state):
        """Test quality verification gate."""
        result = await governance_system._quality_verification_gate(base_project_state)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'governance_decisions' in result
        
        # Verify quality criteria were checked
        quality_decision = next(
            (d for d in result['governance_decisions'] if d['gate'] == 'quality_verification'), None
        )
        assert quality_decision is not None
        assert 'criteria_met' in quality_decision
        
        expected_criteria = [
            'all_tests_passing', 'security_vulnerabilities_resolved',
            'performance_benchmarks_met', 'documentation_complete'
        ]
        
        for criterion in expected_criteria:
            assert criterion in quality_decision['criteria_met']
    
    @pytest.mark.asyncio
    async def test_security_compliance_gate(self, governance_system, base_project_state):
        """Test security compliance gate."""
        result = await governance_system._security_compliance_gate(base_project_state)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'governance_decisions' in result
        
        # Verify security criteria were checked
        security_decision = next(
            (d for d in result['governance_decisions'] if d['gate'] == 'security_compliance'), None
        )
        assert security_decision is not None
        assert 'criteria_met' in security_decision
        
        expected_criteria = [
            'security_scan_passed', 'authentication_secure',
            'data_protection_implemented', 'compliance_requirements_met'
        ]
        
        for criterion in expected_criteria:
            assert criterion in security_decision['criteria_met']
    
    @pytest.mark.asyncio
    async def test_performance_validation_gate(self, governance_system, base_project_state):
        """Test performance validation gate."""
        result = await governance_system._performance_validation_gate(base_project_state)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'governance_decisions' in result
        
        # Verify performance criteria were checked
        perf_decision = next(
            (d for d in result['governance_decisions'] if d['gate'] == 'performance_validation'), None
        )
        assert perf_decision is not None
        assert 'criteria_met' in perf_decision
        
        expected_criteria = [
            'startup_time_acceptable', 'memory_usage_optimal',
            'battery_efficiency_good', 'network_optimization_implemented'
        ]
        
        for criterion in expected_criteria:
            assert criterion in perf_decision['criteria_met']
    
    @pytest.mark.asyncio
    async def test_documentation_review_gate(self, governance_system, base_project_state):
        """Test documentation review gate."""
        result = await governance_system._documentation_review_gate(base_project_state)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'governance_decisions' in result
        
        # Verify documentation criteria were checked
        doc_decision = next(
            (d for d in result['governance_decisions'] if d['gate'] == 'documentation_review'), None
        )
        assert doc_decision is not None
        assert 'criteria_met' in doc_decision
        
        expected_criteria = [
            'api_documentation_complete', 'user_documentation_available',
            'developer_documentation_complete', 'deployment_documentation_ready'
        ]
        
        for criterion in expected_criteria:
            assert criterion in doc_decision['criteria_met']
    
    @pytest.mark.asyncio
    async def test_deployment_approval_gate(self, governance_system, base_project_state):
        """Test deployment approval gate."""
        result = await governance_system._deployment_approval_gate(base_project_state)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'governance_decisions' in result
        
        # Verify deployment criteria were checked
        deploy_decision = next(
            (d for d in result['governance_decisions'] if d['gate'] == 'deployment_approval'), None
        )
        assert deploy_decision is not None
        assert 'criteria_met' in deploy_decision
        
        expected_criteria = [
            'production_readiness_verified', 'deployment_strategy_approved',
            'rollback_procedures_tested', 'monitoring_configured'
        ]
        
        for criterion in expected_criteria:
            assert criterion in deploy_decision['criteria_met']
        
        # Check if project completion is handled
        if deploy_decision['approved']:
            assert result['project_health'] == 'healthy'
            assert result['overall_progress'] == 1.0
    
    def test_quality_gate_criteria_definitions(self, governance_system):
        """Test that quality gate criteria are properly defined."""
        quality_gates = governance_system.quality_gates
        
        # Verify all expected gates are defined
        expected_gates = [
            'architecture_approval', 'implementation_oversight',
            'quality_verification', 'deployment_approval'
        ]
        
        for gate in expected_gates:
            assert gate in quality_gates
            assert isinstance(quality_gates[gate], dict)
            assert len(quality_gates[gate]) > 0
        
        # Verify architecture approval criteria
        arch_criteria = quality_gates['architecture_approval']
        expected_arch_criteria = [
            'architecture_design_complete', 'security_review_passed',
            'performance_considerations_addressed', 'scalability_verified'
        ]
        
        for criterion in expected_arch_criteria:
            assert criterion in arch_criteria
            assert arch_criteria[criterion] == True
        
        # Verify implementation oversight criteria
        impl_criteria = quality_gates['implementation_oversight']
        expected_impl_criteria = [
            'code_quality_standards_met', 'test_coverage_adequate',
            'architecture_compliance_verified', 'real_time_collaboration_healthy'
        ]
        
        for criterion in expected_impl_criteria:
            assert criterion in impl_criteria
            assert impl_criteria[criterion] == True


if __name__ == "__main__":
    # Run tests manually
    print("🧪 Running Quality Gates Tests...")
    
    test_gates = TestQualityGates()
    governance = FlutterSwarmGovernance()
    
    # Create base project state
    base_state = {
        "project_id": "manual-test",
        "name": "ManualTest",
        "description": "Manual test project",
        "requirements": ["auth", "api"],
        "current_governance_phase": "project_initiation",
        "completed_governance_phases": [],
        "governance_phases": governance.governance_phases,
        "quality_gates": governance.quality_gates,
        "gate_statuses": {phase: "pending" for phase in governance.governance_phases},
        "overall_progress": 0.0,
        "project_health": "healthy",
        "collaboration_effectiveness": 0.0,
        "governance_decisions": [],
        "approval_status": {phase: "pending" for phase in governance.governance_phases},
        "real_time_metrics": {},
        "shared_consciousness_summary": {},
        "quality_criteria_met": {},
        "compliance_status": {},
        "coordination_fallback_active": False,
        "stuck_processes": []
    }
    
    # Test quality gate criteria definitions
    test_gates.test_quality_gate_criteria_definitions(governance)
    print("✅ Quality gate criteria definitions test passed")
    
    print("\n🎉 Quality gates tests completed!")