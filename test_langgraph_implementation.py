"""
Tests for the new LangGraph-based FlutterSwarm system.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock

from langgraph_swarm import LangGraphFlutterSwarm, SwarmState
from flutter_swarm import FlutterSwarm


@pytest.mark.unit
class TestLangGraphFlutterSwarm:
    """Unit tests for the LangGraph-based FlutterSwarm."""
    
    def test_swarm_initialization(self):
        """Test that the swarm initializes correctly."""
        swarm = LangGraphFlutterSwarm()
        
        assert swarm is not None
        assert swarm.workflow_phases == [
            'planning', 'architecture', 'implementation', 'testing', 
            'security_review', 'performance_optimization', 'documentation', 
            'quality_assurance', 'deployment'
        ]
        assert swarm.graph is not None
        assert swarm.app is not None
    
    def test_create_project(self):
        """Test project creation."""
        swarm = LangGraphFlutterSwarm()
        
        project_id = swarm.create_project(
            name="TestApp",
            description="A test Flutter app",
            requirements=["auth", "crud"],
            features=["login", "dashboard"]
        )
        
        assert project_id is not None
        assert isinstance(project_id, str)
        assert len(project_id) > 0
    
    @pytest.mark.asyncio
    async def test_planning_node(self):
        """Test the planning node function."""
        swarm = LangGraphFlutterSwarm()
        
        initial_state: SwarmState = {
            "project_id": "test-123",
            "name": "TestApp",
            "description": "A test app",
            "requirements": ["auth", "crud"],
            "features": ["login"],
            "current_phase": "planning",
            "completed_phases": [],
            "workflow_phases": swarm.workflow_phases,
            "architecture_design": None,
            "implementation_artifacts": None,
            "test_results": None,
            "security_findings": None,
            "performance_metrics": None,
            "documentation": None,
            "deployment_config": None,
            "quality_assessment": None,
            "messages": [],
            "errors": [],
            "overall_progress": 0.0,
            "files_created": {},
            "platforms": ["android"],
            "ci_system": "github_actions"
        }
        
        result = await swarm._planning_node(initial_state)
        
        assert result["current_phase"] == "planning"
        assert "planning" in result["completed_phases"]
        assert result["overall_progress"] == 0.1
        assert "messages" in result
        assert "architecture_design" in result
    
    @pytest.mark.asyncio
    async def test_architecture_node(self):
        """Test the architecture node function."""
        swarm = LangGraphFlutterSwarm()
        
        initial_state: SwarmState = {
            "project_id": "test-123",
            "name": "TestApp",
            "description": "A test app",
            "requirements": ["auth", "crud"],
            "features": ["login"],
            "current_phase": "architecture",
            "completed_phases": ["planning"],
            "workflow_phases": swarm.workflow_phases,
            "architecture_design": {"planning": {"structure": "clean_architecture"}},
            "implementation_artifacts": None,
            "test_results": None,
            "security_findings": None,
            "performance_metrics": None,
            "documentation": None,
            "deployment_config": None,
            "quality_assessment": None,
            "messages": ["Planning completed"],
            "errors": [],
            "overall_progress": 0.1,
            "files_created": {},
            "platforms": ["android"],
            "ci_system": "github_actions"
        }
        
        with patch('agents.architecture_agent.ArchitectureAgent') as mock_agent_class:
            mock_agent = mock_agent_class.return_value
            mock_agent.execute_task = AsyncMock(return_value={"status": "completed"})
            
            result = await swarm._architecture_node(initial_state)
            
            assert result["current_phase"] == "architecture"
            assert "architecture" in result["completed_phases"]
            assert result["overall_progress"] == 0.25
            assert "architecture_design" in result
            assert "files_created" in result
            assert len(result["files_created"]) > 0
    
    @pytest.mark.asyncio
    async def test_route_from_planning(self):
        """Test routing from planning phase."""
        swarm = LangGraphFlutterSwarm()
        
        # Test successful planning completion
        state_with_planning = {
            "completed_phases": ["planning"]
        }
        
        next_node = swarm._route_from_planning(state_with_planning)
        assert next_node == "architecture"
        
        # Test incomplete planning
        state_without_planning = {
            "completed_phases": []
        }
        
        next_node = swarm._route_from_planning(state_without_planning)
        assert next_node == "end"
    
    @pytest.mark.asyncio
    async def test_route_from_testing(self):
        """Test routing from testing phase with different scenarios."""
        swarm = LangGraphFlutterSwarm()
        
        # Test passing tests
        state_passing_tests = {
            "completed_phases": ["planning", "architecture", "implementation", "testing"],
            "test_results": {
                "overall_coverage": 85,
                "unit_tests": {"failed": 0},
                "widget_tests": {"failed": 0},
                "integration_tests": {"failed": 1}
            }
        }
        
        next_node = swarm._route_from_testing(state_passing_tests)
        assert next_node == "security_review"
        
        # Test failing tests
        state_failing_tests = {
            "completed_phases": ["planning", "architecture", "implementation", "testing"],
            "test_results": {
                "overall_coverage": 60,
                "unit_tests": {"failed": 5},
                "widget_tests": {"failed": 0},
                "integration_tests": {"failed": 0}
            }
        }
        
        next_node = swarm._route_from_testing(state_failing_tests)
        assert next_node == "implementation"
    
    @pytest.mark.asyncio
    async def test_full_workflow_build(self):
        """Test a complete workflow build."""
        swarm = LangGraphFlutterSwarm(enable_monitoring=False)
        
        project_id = "test-project-123"
        
        # Mock all agent classes to avoid actual LLM calls
        with patch('agents.architecture_agent.ArchitectureAgent') as mock_arch, \
             patch('agents.implementation_agent.ImplementationAgent') as mock_impl, \
             patch('agents.testing_agent.TestingAgent') as mock_test, \
             patch('agents.security_agent.SecurityAgent') as mock_sec, \
             patch('agents.devops_agent.DevOpsAgent') as mock_devops, \
             patch('agents.documentation_agent.DocumentationAgent') as mock_doc, \
             patch('agents.performance_agent.PerformanceAgent') as mock_perf, \
             patch('agents.quality_assurance_agent.QualityAssuranceAgent') as mock_qa:
            
            # Setup all mocks
            for mock_agent_class in [mock_arch, mock_impl, mock_test, mock_sec, 
                                   mock_devops, mock_doc, mock_perf, mock_qa]:
                mock_agent = mock_agent_class.return_value
                mock_agent.execute_task = AsyncMock(return_value={"status": "completed"})
            
            # Execute build
            result = await swarm.build_project(
                project_id=project_id,
                name="TestApp",
                description="A comprehensive test application",
                requirements=["authentication", "data_management", "offline_support"],
                features=["login", "dashboard", "sync"],
                platforms=["android", "ios"],
                ci_system="github_actions"
            )
            
            # Verify result structure
            assert result["status"] == "completed"
            assert result["project_id"] == project_id
            assert result["files_created"] > 0
            assert result["architecture_decisions"] > 0
            assert "test_results" in result
            assert "security_findings" in result
            assert "performance_metrics" in result
            assert "documentation" in result
            assert "deployment_config" in result
            assert "quality_assessment" in result
            assert result["overall_progress"] == 1.0
            
            # Verify all phases completed
            expected_phases = [
                'planning', 'architecture', 'implementation', 'testing', 
                'security_review', 'performance_optimization', 'documentation', 
                'quality_assurance', 'deployment'
            ]
            assert all(phase in result["completed_phases"] for phase in expected_phases)


@pytest.mark.integration
class TestFlutterSwarmIntegration:
    """Integration tests for the FlutterSwarm system."""
    
    def test_backward_compatibility(self):
        """Test that the main FlutterSwarm class is properly aliased."""
        swarm = FlutterSwarm()
        
        assert isinstance(swarm, LangGraphFlutterSwarm)
        assert swarm.workflow_phases is not None
        assert swarm.graph is not None
    
    @pytest.mark.asyncio
    async def test_minimal_build_workflow(self):
        """Test a minimal build workflow to ensure the system works end-to-end."""
        swarm = FlutterSwarm(enable_monitoring=False)
        
        project_id = swarm.create_project(
            name="MinimalApp",
            description="A minimal test app",
            requirements=["basic_ui"],
            features=["home_screen"]
        )
        
        # Mock agent execution to avoid LLM calls
        with patch('agents.architecture_agent.ArchitectureAgent') as mock_arch, \
             patch('agents.implementation_agent.ImplementationAgent') as mock_impl, \
             patch('agents.testing_agent.TestingAgent') as mock_test, \
             patch('agents.security_agent.SecurityAgent') as mock_sec, \
             patch('agents.devops_agent.DevOpsAgent') as mock_devops, \
             patch('agents.documentation_agent.DocumentationAgent') as mock_doc, \
             patch('agents.performance_agent.PerformanceAgent') as mock_perf, \
             patch('agents.quality_assurance_agent.QualityAssuranceAgent') as mock_qa:
            
            # Setup all mocks to return success
            for mock_agent_class in [mock_arch, mock_impl, mock_test, mock_sec, 
                                   mock_devops, mock_doc, mock_perf, mock_qa]:
                mock_agent = mock_agent_class.return_value
                mock_agent.execute_task = AsyncMock(return_value={"status": "completed"})
            
            result = await swarm.build_project(
                project_id=project_id,
                name="MinimalApp",
                description="A minimal test app",
                requirements=["basic_ui"],
                features=["home_screen"],
                platforms=["android"]
            )
            
            assert result["status"] == "completed"
            assert result["overall_progress"] == 1.0
            assert len(result["completed_phases"]) == 9  # All phases
    
    def test_helper_methods(self):
        """Test helper methods for compatibility."""
        swarm = FlutterSwarm()
        
        # Test project status
        status = swarm.get_project_status("test-id")
        assert "project" in status
        assert "agents" in status
        
        # Test list projects
        projects = swarm.list_projects()
        assert isinstance(projects, list)
        
        # Test agent status
        agent_status = swarm.get_agent_status()
        assert isinstance(agent_status, dict)
        
        specific_agent_status = swarm.get_agent_status("architecture")
        assert "agent_id" in specific_agent_status


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
