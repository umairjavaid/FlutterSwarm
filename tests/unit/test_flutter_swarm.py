"""
Unit tests for the FlutterSwarm main orchestration system.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from flutter_swarm import FlutterSwarm


@pytest.mark.unit
class TestFlutterSwarm:
    """Test suite for FlutterSwarm main class."""
    
    def test_initialization(self, mock_anthropic_client, mock_config, mock_tool_manager):
        """Test FlutterSwarm initialization."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            swarm = FlutterSwarm()
            
            assert len(swarm.agents) == 9  # All agent types
            assert not swarm.is_running
            
            # Check all expected agents are initialized
            expected_agents = [
                "orchestrator", "architecture", "implementation", 
                "testing", "security", "devops", "documentation", 
                "performance", "quality_assurance"
            ]
            
            for agent_type in expected_agents:
                assert agent_type in swarm.agents
                
    @pytest.mark.asyncio
    async def test_start_and_stop(self, flutter_swarm_instance):
        """Test starting and stopping the swarm."""
        swarm = flutter_swarm_instance
        
        # Mock agent start/stop methods
        for agent in swarm.agents.values():
            agent.start = AsyncMock()
            agent.stop = AsyncMock()
        
        assert not swarm.is_running
        
        # Test start (run briefly then stop)
        start_task = asyncio.create_task(swarm.start())
        await asyncio.sleep(0.1)  # Let it start
        
        assert swarm.is_running
        
        # Verify all agents were started
        for agent in swarm.agents.values():
            agent.start.assert_called_once()
        
        # Test stop
        await swarm.stop()
        assert not swarm.is_running
        
        # Verify all agents were stopped
        for agent in swarm.agents.values():
            agent.stop.assert_called_once()
            
        # Clean up the start task
        start_task.cancel()
        try:
            await start_task
        except asyncio.CancelledError:
            pass
            
    def test_create_project(self, flutter_swarm_instance, sample_project_data):
        """Test creating a new project."""
        swarm = flutter_swarm_instance
        
        project_id = swarm.create_project(
            name=sample_project_data["name"],
            description=sample_project_data["description"],
            requirements=sample_project_data["requirements"],
            features=sample_project_data["features"]
        )
        
        assert project_id is not None
        assert isinstance(project_id, str)
        
    def test_create_project_minimal(self, flutter_swarm_instance):
        """Test creating a project with minimal parameters."""
        swarm = flutter_swarm_instance
        
        project_id = swarm.create_project(
            name="MinimalApp",
            description="A minimal Flutter app"
        )
        
        assert project_id is not None
        
    @pytest.mark.asyncio
    async def test_build_project(self, flutter_swarm_instance, sample_project_data):
        """Test building a project."""
        swarm = flutter_swarm_instance
        
        # Create a project first
        project_id = swarm.create_project(
            name=sample_project_data["name"],
            description=sample_project_data["description"],
            requirements=sample_project_data["requirements"]
        )
        
        # Mock the monitoring method to return quickly
        mock_result = {
            "status": "completed",
            "project_id": project_id,
            "files_created": 10,
            "architecture_decisions": 3,
            "test_results": {"unit": {"status": "passed"}},
            "security_findings": [],
            "performance_metrics": {},
            "documentation": ["README.md"],
            "deployment_config": {"status": "configured"}
        }
        
        with patch.object(swarm, '_monitor_build_progress', return_value=mock_result):
            result = await swarm.build_project(
                project_id,
                platforms=["android", "ios"],
                ci_system="github_actions"
            )
            
            assert result["status"] == "completed"
            assert result["project_id"] == project_id
            assert "files_created" in result
            assert "test_results" in result
            
    @pytest.mark.asyncio
    async def test_build_nonexistent_project(self, flutter_swarm_instance):
        """Test building a non-existent project raises error."""
        swarm = flutter_swarm_instance
        
        with pytest.raises(ValueError, match="Project nonexistent not found"):
            await swarm.build_project("nonexistent")
            
    @pytest.mark.asyncio
    async def test_monitor_build_progress(self, flutter_swarm_instance, clean_shared_state):
        """Test monitoring build progress."""
        swarm = flutter_swarm_instance
        
        # Create a mock project in shared state
        from shared.state import ProjectState
        project_id = "test_project"
        project = ProjectState(
            project_id=project_id,
            name="Test Project",
            description="Test",
            requirements=[],
            current_phase="implementation",
            progress=0.5,
            files_created={"main.dart": "content"},
            architecture_decisions=[],
            test_results={},
            security_findings=[],
            performance_metrics={},
            documentation={},
            deployment_config={}
        )
        
        clean_shared_state._projects[project_id] = project
        
        # Mock the project to complete quickly
        async def mock_progress():
            await asyncio.sleep(0.1)
            project.current_phase = "deployment"
            project.progress = 0.9
            clean_shared_state._agents.clear()  # No active agents
            
        # Run monitoring with mocked progress
        progress_task = asyncio.create_task(mock_progress())
        result_task = asyncio.create_task(swarm._monitor_build_progress(project_id))
        
        await asyncio.gather(progress_task, result_task)
        result = result_task.result()
        
        assert result["status"] == "completed"
        assert result["project_id"] == project_id
        
    def test_get_project_status(self, flutter_swarm_instance, clean_shared_state):
        """Test getting project status."""
        swarm = flutter_swarm_instance
        
        # Test non-existent project
        status = swarm.get_project_status("nonexistent")
        assert "error" in status
        
        # Create a project and test status
        from shared.state import ProjectState, AgentState, AgentStatus
        project_id = "test_project"
        project = ProjectState(
            project_id=project_id,
            name="Test Project",
            description="Test",
            requirements=[],
            current_phase="planning",
            progress=0.1,
            files_created={},
            architecture_decisions=[],
            test_results={},
            security_findings=[],
            performance_metrics={},
            documentation={},
            deployment_config={}
        )
        
        agent_state = AgentState(
            agent_id="test_agent",
            status=AgentStatus.WORKING,
            current_task="Testing",
            progress=0.5,
            last_update=datetime.now(),
            capabilities=["testing"],
            metadata={}
        )
        
        clean_shared_state._projects[project_id] = project
        clean_shared_state._agents["test_agent"] = agent_state
        
        status = swarm.get_project_status(project_id)
        
        assert "project" in status
        assert "agents" in status
        assert status["project"]["id"] == project_id
        assert status["project"]["name"] == "Test Project"
        assert "test_agent" in status["agents"]
        
    def test_list_projects(self, flutter_swarm_instance, clean_shared_state):
        """Test listing projects."""
        swarm = flutter_swarm_instance
        
        # Test with no projects
        projects = swarm.list_projects()
        assert projects == []
        
        # Add a project and test listing
        from shared.state import ProjectState
        project = ProjectState(
            project_id="test_project",
            name="Test Project",
            description="Test",
            requirements=[],
            current_phase="planning",
            progress=0.1,
            files_created={},
            architecture_decisions=[],
            test_results={},
            security_findings=[],
            performance_metrics={},
            documentation={},
            deployment_config={}
        )
        
        clean_shared_state._projects["test_project"] = project
        clean_shared_state._current_project_id = "test_project"
        
        projects = swarm.list_projects()
        assert len(projects) == 1
        assert projects[0]["id"] == "test_project"
        assert projects[0]["name"] == "Test Project"
        
    def test_get_agent_status_single(self, flutter_swarm_instance, clean_shared_state):
        """Test getting status of a single agent."""
        swarm = flutter_swarm_instance
        
        # Test non-existent agent
        status = swarm.get_agent_status("nonexistent")
        assert "error" in status
        
        # Add an agent and test status
        from shared.state import AgentState, AgentStatus
        agent_state = AgentState(
            agent_id="test_agent",
            status=AgentStatus.WORKING,
            current_task="Testing",
            progress=0.5,
            last_update=datetime.now(),
            capabilities=["testing"],
            metadata={}
        )
        
        clean_shared_state._agents["test_agent"] = agent_state
        
        status = swarm.get_agent_status("test_agent")
        
        assert status["agent_id"] == "test_agent"
        assert status["status"] == "working"
        assert status["current_task"] == "Testing"
        assert status["progress"] == 0.5
        
    def test_get_agent_status_all(self, flutter_swarm_instance, clean_shared_state):
        """Test getting status of all agents."""
        swarm = flutter_swarm_instance
        
        # Add multiple agents
        from shared.state import AgentState, AgentStatus
        agents = ["agent1", "agent2"]
        
        for agent_id in agents:
            agent_state = AgentState(
                agent_id=agent_id,
                status=AgentStatus.IDLE,
                current_task=None,
                progress=0.0,
                last_update=datetime.now(),
                capabilities=["capability"],
                metadata={}
            )
            clean_shared_state._agents[agent_id] = agent_state
        
        status = swarm.get_agent_status()
        
        assert len(status) == 2
        for agent_id in agents:
            assert agent_id in status
            assert status[agent_id]["status"] == "idle"
            
    @pytest.mark.asyncio
    async def test_start_already_running(self, flutter_swarm_instance):
        """Test starting swarm when already running."""
        swarm = flutter_swarm_instance
        swarm.is_running = True
        
        # Mock stdout to capture print
        with patch('builtins.print') as mock_print:
            await swarm.start()
            mock_print.assert_called_with("⚠️  FlutterSwarm is already running")
            
    @pytest.mark.asyncio
    async def test_stop_not_running(self, flutter_swarm_instance):
        """Test stopping swarm when not running."""
        swarm = flutter_swarm_instance
        swarm.is_running = False
        
        # Should not raise any errors
        await swarm.stop()
        assert not swarm.is_running
        
    def test_initialization_with_missing_env_var(self, mock_anthropic_client, mock_config, mock_tool_manager):
        """Test initialization fails gracefully without API key."""
        with patch.dict('os.environ', {}, clear=True):
            # Should still initialize but may have issues with LLM
            swarm = FlutterSwarm()
            assert len(swarm.agents) == 9
