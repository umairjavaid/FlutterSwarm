"""
Unit tests for the OrchestratorAgent.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from agents.orchestrator_agent import OrchestratorAgent
from shared.state import AgentStatus, MessageType, AgentMessage
from tests.mocks.mock_implementations import MockAgent, MockToolManager, MockAnthropicClient
from tests.fixtures.test_constants import AGENT_CAPABILITIES, MESSAGE_TEMPLATES


@pytest.mark.unit
class TestOrchestratorAgent:
    """Test suite for OrchestratorAgent."""
    
    @pytest.fixture
    def orchestrator(self, mock_anthropic_client, mock_config, mock_tool_manager):
        """Create orchestrator agent for testing."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            return OrchestratorAgent()
    
    def test_initialization(self, orchestrator):
        """Test orchestrator agent initialization."""
        assert orchestrator.agent_id == "orchestrator"
        assert orchestrator.capabilities == AGENT_CAPABILITIES["orchestrator"]
        assert not orchestrator.is_running
        assert orchestrator.status == AgentStatus.IDLE
        
    @pytest.mark.asyncio
    async def test_start_stop(self, orchestrator):
        """Test starting and stopping the orchestrator."""
        # Mock the agent loop
        orchestrator._agent_loop = AsyncMock()
        
        assert not orchestrator.is_running
        
        # Start agent
        start_task = asyncio.create_task(orchestrator.start())
        await asyncio.sleep(0.1)
        
        assert orchestrator.is_running
        assert orchestrator.status == AgentStatus.IDLE
        
        # Stop agent
        await orchestrator.stop()
        assert not orchestrator.is_running
        
    @pytest.mark.asyncio
    async def test_workflow_coordination(self, orchestrator, clean_shared_state):
        """Test workflow coordination capabilities."""
        # Mock dependencies
        orchestrator._handle_task_request = AsyncMock(return_value={"status": "assigned"})
        orchestrator._coordinate_agents = AsyncMock(return_value={"status": "coordinated"})
        
        # Create a task request message
        message = AgentMessage(
            message_id="test_msg_1",
            from_agent="test_agent",
            to_agent="orchestrator",
            message_type=MessageType.TASK_REQUEST,
            content={
                "task_description": "create_project",
                "task_data": {
                    "name": "TestApp",
                    "description": "Test application",
                    "requirements": ["auth", "database"]
                }
            },
            priority=5,
            timestamp=datetime.now()
        )
        
        # Process the message
        result = await orchestrator._handle_message(message)
        
        # Verify task was handled
        orchestrator._handle_task_request.assert_called_once()
        assert result is not None
        
    @pytest.mark.asyncio
    async def test_task_delegation(self, orchestrator, clean_shared_state):
        """Test task delegation to appropriate agents."""
        # Register some mock agents
        clean_shared_state.register_agent("implementation", ["code_generation"])
        clean_shared_state.register_agent("testing", ["unit_testing"])
        clean_shared_state.register_agent("security", ["vulnerability_scanning"])
        
        # Mock the delegation logic
        orchestrator._delegate_task = AsyncMock(return_value="task_123")
        orchestrator._monitor_task_progress = AsyncMock(return_value={"status": "completed"})
        
        # Create a project creation task
        task_data = {
            "task_description": "create_project",
            "task_data": {
                "name": "TestApp",
                "requirements": ["authentication", "data_persistence", "security"]
            }
        }
        
        # Execute task delegation
        result = await orchestrator._handle_task_request(
            AgentMessage(
                message_id="test_msg",
                from_agent="test",
                to_agent="orchestrator", 
                message_type=MessageType.TASK_REQUEST,
                content=task_data,
                priority=5,
                timestamp=datetime.now()
            )
        )
        
        # Verify delegation occurred
        orchestrator._delegate_task.assert_called()
        
    @pytest.mark.asyncio
    async def test_progress_monitoring(self, orchestrator, clean_shared_state):
        """Test progress monitoring capabilities."""
        # Register agents with different statuses
        clean_shared_state.register_agent("implementation", ["code_generation"])
        clean_shared_state.register_agent("testing", ["unit_testing"])
        
        # Update agent statuses
        clean_shared_state.update_agent_status(
            "implementation", AgentStatus.WORKING, "Creating models", 0.5
        )
        clean_shared_state.update_agent_status(
            "testing", AgentStatus.WORKING, "Writing tests", 0.3
        )
        
        # Mock progress calculation
        orchestrator._calculate_overall_progress = AsyncMock(return_value=0.4)
        orchestrator._update_project_status = AsyncMock()
        
        # Monitor progress
        await orchestrator._monitor_progress("test_project")
        
        # Verify monitoring occurred
        orchestrator._calculate_overall_progress.assert_called()
        orchestrator._update_project_status.assert_called()
        
    @pytest.mark.asyncio
    async def test_agent_collaboration_coordination(self, orchestrator, clean_shared_state):
        """Test coordination of agent collaborations."""
        # Register multiple agents
        for agent_id in ["implementation", "testing", "security"]:
            clean_shared_state.register_agent(agent_id, AGENT_CAPABILITIES.get(agent_id, []))
        
        # Mock collaboration logic
        orchestrator._facilitate_collaboration = AsyncMock(return_value={"status": "facilitated"})
        
        # Create collaboration request
        collaboration_message = AgentMessage(
            message_id="collab_msg",
            from_agent="testing",
            to_agent="orchestrator",
            message_type=MessageType.COLLABORATION_REQUEST,
            content={
                "collaboration_type": "code_review",
                "target_agent": "implementation",
                "data": {"file_path": "lib/main.dart"}
            },
            priority=3,
            timestamp=datetime.now()
        )
        
        # Handle collaboration
        result = await orchestrator._handle_collaboration_request(collaboration_message)
        
        # Verify collaboration was facilitated
        orchestrator._facilitate_collaboration.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_decision_making(self, orchestrator):
        """Test decision making capabilities."""
        # Mock decision-making components
        orchestrator._analyze_situation = AsyncMock(return_value={
            "complexity": "high",
            "risk_level": "medium",
            "recommended_approach": "incremental"
        })
        orchestrator._make_decision = AsyncMock(return_value={
            "decision": "proceed_with_caution",
            "rationale": "High complexity requires careful approach"
        })
        
        # Test decision making for a complex scenario
        scenario = {
            "project_requirements": ["real_time_sync", "offline_support", "encryption"],
            "current_progress": 0.6,
            "agent_availability": ["implementation", "security"],
            "issues": ["performance_concern", "security_gap"]
        }
        
        decision = await orchestrator._make_strategic_decision(scenario)
        
        # Verify decision process
        orchestrator._analyze_situation.assert_called_once()
        orchestrator._make_decision.assert_called_once()
        
    def test_capability_matching(self, orchestrator):
        """Test capability matching for task assignment."""
        # Mock agents with different capabilities
        available_agents = {
            "implementation": ["code_generation", "flutter_development"],
            "testing": ["unit_testing", "integration_testing"],
            "security": ["vulnerability_scanning", "secure_coding"],
            "devops": ["deployment", "ci_cd_setup"]
        }
        
        # Test capability matching
        best_agent = orchestrator._match_agent_capabilities(
            "code_generation", available_agents
        )
        assert best_agent == "implementation"
        
        best_agent = orchestrator._match_agent_capabilities(
            "vulnerability_scanning", available_agents
        )
        assert best_agent == "security"
        
        # Test no match scenario
        best_agent = orchestrator._match_agent_capabilities(
            "unknown_capability", available_agents
        )
        assert best_agent is None
        
    @pytest.mark.asyncio
    async def test_error_handling(self, orchestrator, clean_shared_state):
        """Test error handling in orchestration."""
        # Mock an agent failure scenario
        orchestrator._handle_agent_failure = AsyncMock(return_value={"status": "recovered"})
        
        # Simulate agent failure
        await orchestrator._handle_agent_error("implementation", "Tool execution failed")
        
        # Verify error handling
        orchestrator._handle_agent_failure.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_load_balancing(self, orchestrator, clean_shared_state):
        """Test load balancing across agents."""
        # Register multiple agents
        agents = ["implementation", "testing", "security"]
        for agent_id in agents:
            clean_shared_state.register_agent(agent_id, ["test_capability"])
            
        # Set different workloads
        clean_shared_state.update_agent_status("implementation", AgentStatus.WORKING, "Task 1", 0.8)
        clean_shared_state.update_agent_status("testing", AgentStatus.IDLE, None, 0.0)
        clean_shared_state.update_agent_status("security", AgentStatus.WORKING, "Task 2", 0.3)
        
        # Test load balancing logic
        least_loaded = orchestrator._find_least_loaded_agent(agents)
        assert least_loaded == "testing"  # Should pick the idle agent
        
    @pytest.mark.asyncio
    async def test_resource_management(self, orchestrator):
        """Test resource management capabilities."""
        # Mock resource tracking
        orchestrator._track_resource_usage = AsyncMock(return_value={
            "cpu_usage": 45.2,
            "memory_usage": 68.1,
            "active_tasks": 3
        })
        orchestrator._optimize_resource_allocation = AsyncMock(return_value={"status": "optimized"})
        
        # Test resource management
        await orchestrator._manage_resources()
        
        # Verify resource management
        orchestrator._track_resource_usage.assert_called_once()
        orchestrator._optimize_resource_allocation.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_workflow_state_management(self, orchestrator, clean_shared_state):
        """Test workflow state management."""
        # Create a project
        project_id = clean_shared_state.create_project(
            "TestApp", "Test application", ["requirement1"]
        )
        
        # Mock workflow state operations
        orchestrator._update_workflow_state = AsyncMock()
        orchestrator._checkpoint_workflow = AsyncMock()
        
        # Update workflow state
        await orchestrator._advance_workflow_phase(project_id, "implementation")
        
        # Verify state management
        orchestrator._update_workflow_state.assert_called()
        
    def test_priority_queue_management(self, orchestrator):
        """Test priority queue management for tasks."""
        # Create tasks with different priorities
        tasks = [
            {"id": "task1", "priority": 1, "description": "Low priority"},
            {"id": "task2", "priority": 5, "description": "High priority"},
            {"id": "task3", "priority": 3, "description": "Medium priority"}
        ]
        
        # Test priority sorting
        sorted_tasks = orchestrator._sort_tasks_by_priority(tasks)
        
        # Verify highest priority comes first
        assert sorted_tasks[0]["priority"] == 5
        assert sorted_tasks[1]["priority"] == 3
        assert sorted_tasks[2]["priority"] == 1
