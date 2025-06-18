"""
Integration tests for CLI functionality.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from io import StringIO

from cli import FlutterSwarmCLI, main
from flutter_swarm import FlutterSwarm
from tests.mocks.mock_implementations import MockAgent, MockConfigManager
from tests.fixtures.test_constants import SAMPLE_PROJECT_DATA, TEST_CONFIG_DATA


@pytest.mark.integration
class TestCLIIntegration:
    """Test suite for CLI integration with FlutterSwarm system."""
    
    @pytest.fixture
    def mock_cli_dependencies(self):
        """Mock CLI dependencies."""
        with patch('cli.FlutterSwarm') as mock_swarm_class, \
             patch('cli.get_config') as mock_get_config, \
             patch('cli.console') as mock_console:
            
            # Mock FlutterSwarm instance
            mock_swarm = MagicMock()
            mock_swarm_class.return_value = mock_swarm
            
            # Mock configuration
            mock_config = MockConfigManager(TEST_CONFIG_DATA)
            mock_get_config.return_value = mock_config
            
            # Mock console
            mock_console.print = MagicMock()
            mock_console.input = MagicMock()
            
            yield {
                'swarm': mock_swarm,
                'config': mock_config,
                'console': mock_console
            }
    
    @pytest.fixture
    def cli_instance(self, mock_cli_dependencies):
        """Create CLI instance for testing."""
        return FlutterSwarmCLI()
    
    @pytest.mark.asyncio
    async def test_create_project_command(self, cli_instance, mock_cli_dependencies):
        """Test create project CLI command."""
        mock_swarm = mock_cli_dependencies['swarm']
        mock_swarm.create_project.return_value = "test_project_123"
        
        # Mock arguments
        args = MagicMock()
        args.name = "TestApp"
        args.description = "A test application"
        args.requirements = "auth,database"
        args.features = "login,crud"
        args.platforms = "android,ios"
        args.build = False
        
        # Execute create command
        await cli_instance.create_project(args)
        
        # Verify project creation
        mock_swarm.create_project.assert_called_once_with(
            name="TestApp",
            description="A test application",
            requirements=["auth", "database"],
            features=["login", "crud"]
        )
        
    @pytest.mark.asyncio
    async def test_create_project_with_build(self, cli_instance, mock_cli_dependencies):
        """Test create project with immediate build."""
        mock_swarm = mock_cli_dependencies['swarm']
        mock_swarm.create_project.return_value = "test_project_123"
        mock_swarm.build_project.return_value = asyncio.Future()
        mock_swarm.build_project.return_value.set_result({
            "status": "completed",
            "files_created": 15
        })
        
        # Mock build progress monitoring
        cli_instance.build_project_with_progress = AsyncMock()
        
        # Mock arguments  
        args = MagicMock()
        args.name = "TestApp"
        args.description = "A test application"
        args.requirements = None
        args.features = None
        args.platforms = "android,ios"
        args.build = True
        
        # Execute create command with build
        await cli_instance.create_project(args)
        
        # Verify build was triggered
        cli_instance.build_project_with_progress.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_status_command_project(self, cli_instance, mock_cli_dependencies):
        """Test status command for specific project."""
        mock_swarm = mock_cli_dependencies['swarm']
        mock_swarm.get_project_status.return_value = {
            "project": {
                "id": "test_project_123",
                "name": "TestApp",
                "current_phase": "implementation",
                "progress": 0.65,
                "files_created": 12,
                "architecture_decisions": 3,
                "security_findings": 1
            },
            "agents": {
                "implementation": {
                    "status": "working",
                    "current_task": "Creating models",
                    "progress": 0.7,
                    "last_update": "2024-01-01T12:00:00"
                }
            }
        }
        
        # Mock display method
        cli_instance.display_project_status = MagicMock()
        
        # Mock arguments
        args = MagicMock()
        args.project_id = "test_project_123"
        
        # Execute status command
        await cli_instance.status(args)
        
        # Verify status retrieval and display
        mock_swarm.get_project_status.assert_called_once_with("test_project_123")
        cli_instance.display_project_status.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_status_command_agents(self, cli_instance, mock_cli_dependencies):
        """Test status command for all agents."""
        mock_swarm = mock_cli_dependencies['swarm']
        mock_swarm.get_agent_status.return_value = {
            "orchestrator": {
                "status": "idle",
                "current_task": None,
                "progress": 0.0,
                "last_update": "2024-01-01T12:00:00"
            },
            "implementation": {
                "status": "working",
                "current_task": "Creating models",
                "progress": 0.7,
                "last_update": "2024-01-01T12:05:00"
            }
        }
        
        # Mock display method
        cli_instance.display_agent_status = MagicMock()
        
        # Mock arguments
        args = MagicMock()
        args.project_id = None
        
        # Execute status command
        await cli_instance.status(args)
        
        # Verify agent status retrieval and display
        mock_swarm.get_agent_status.assert_called_once()
        cli_instance.display_agent_status.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_interactive_mode(self, cli_instance, mock_cli_dependencies):
        """Test interactive CLI mode."""
        mock_swarm = mock_cli_dependencies['swarm']
        mock_console = mock_cli_dependencies['console']
        
        # Mock swarm start
        mock_swarm.start.return_value = asyncio.Future()
        mock_swarm.start.return_value.set_result(None)
        mock_swarm.stop = AsyncMock()
        
        # Mock interactive commands
        commands = ["help", "create TestApp A test app", "list", "quit"]
        mock_console.input.side_effect = commands
        
        # Mock command handlers
        cli_instance.show_interactive_help = MagicMock()
        cli_instance.handle_interactive_create = AsyncMock()
        cli_instance.handle_interactive_list = MagicMock()
        
        # Mock arguments
        args = MagicMock()
        
        # Execute interactive mode
        await cli_instance.run_interactive(args)
        
        # Verify commands were processed
        cli_instance.show_interactive_help.assert_called_once()
        cli_instance.handle_interactive_create.assert_called_once()
        cli_instance.handle_interactive_list.assert_called_once()
        mock_swarm.stop.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_build_progress_monitoring(self, cli_instance, mock_cli_dependencies):
        """Test build progress monitoring with live updates."""
        mock_swarm = mock_cli_dependencies['swarm']
        
        # Mock project status updates
        status_updates = [
            {
                "project": {
                    "current_phase": "planning",
                    "progress": 0.1
                }
            },
            {
                "project": {
                    "current_phase": "implementation", 
                    "progress": 0.5
                }
            },
            {
                "project": {
                    "current_phase": "testing",
                    "progress": 0.8
                }
            }
        ]
        
        mock_swarm.get_project_status.side_effect = status_updates
        
        # Mock build task
        build_future = asyncio.Future()
        build_future.set_result({
            "status": "completed",
            "files_created": 15,
            "test_results": {"unit": {"status": "passed", "count": 20}}
        })
        mock_swarm.build_project.return_value = build_future
        
        # Mock display method
        cli_instance.display_build_results = MagicMock()
        
        # Execute build with progress monitoring
        await cli_instance.build_project_with_progress("test_project_123")
        
        # Verify build was initiated and results displayed
        mock_swarm.build_project.assert_called_once()
        cli_instance.display_build_results.assert_called_once()
        
    def test_display_project_status(self, cli_instance, mock_cli_dependencies):
        """Test project status display formatting."""
        mock_console = mock_cli_dependencies['console']
        
        status = {
            "project": {
                "name": "TestApp",
                "current_phase": "implementation",
                "progress": 0.65,
                "files_created": 12,
                "architecture_decisions": 3,
                "security_findings": 1
            },
            "agents": {
                "implementation": {
                    "status": "working",
                    "current_task": "Creating models",
                    "progress": 0.7
                }
            }
        }
        
        # Execute display
        cli_instance.display_project_status(status)
        
        # Verify console output was called
        assert mock_console.print.call_count > 0
        
    def test_display_build_results(self, cli_instance, mock_cli_dependencies):
        """Test build results display formatting."""
        mock_console = mock_cli_dependencies['console']
        
        build_result = {
            "status": "completed",
            "files_created": 15,
            "architecture_decisions": 3,
            "security_findings": [],
            "documentation": ["README.md"],
            "test_results": {
                "unit": {"status": "passed", "count": 20},
                "widget": {"status": "passed", "count": 8}
            }
        }
        
        # Execute display
        cli_instance.display_build_results(build_result)
        
        # Verify console output was called
        assert mock_console.print.call_count > 0
        
    @pytest.mark.asyncio
    async def test_interactive_create_command(self, cli_instance, mock_cli_dependencies):
        """Test interactive create command."""
        mock_swarm = mock_cli_dependencies['swarm']
        mock_console = mock_cli_dependencies['console']
        mock_swarm.create_project.return_value = "test_project_123"
        
        # Test create command with description
        await cli_instance.handle_interactive_create("create TestApp A test application")
        
        # Verify project creation
        mock_swarm.create_project.assert_called_once_with("TestApp", "A test application")
        
        # Test create command without description
        mock_swarm.create_project.reset_mock()
        await cli_instance.handle_interactive_create("create SimpleApp")
        
        mock_swarm.create_project.assert_called_once_with("SimpleApp", "Flutter application: SimpleApp")
        
    @pytest.mark.asyncio
    async def test_interactive_status_command(self, cli_instance, mock_cli_dependencies):
        """Test interactive status command."""
        mock_swarm = mock_cli_dependencies['swarm']
        
        # Mock project status
        mock_swarm.get_project_status.return_value = {
            "project": {"name": "TestApp", "progress": 0.5}
        }
        
        # Mock display method
        cli_instance.display_project_status = MagicMock()
        
        # Test status with project ID
        await cli_instance.handle_interactive_status("status test_project_123")
        
        # Verify status call
        mock_swarm.get_project_status.assert_called_once_with("test_project_123")
        cli_instance.display_project_status.assert_called_once()
        
    def test_interactive_list_command(self, cli_instance, mock_cli_dependencies):
        """Test interactive list command."""
        mock_swarm = mock_cli_dependencies['swarm']
        mock_console = mock_cli_dependencies['console']
        
        # Mock project list
        mock_swarm.list_projects.return_value = [
            {
                "id": "project_123",
                "name": "TestApp",
                "current_phase": "implementation",
                "progress": 0.65
            }
        ]
        
        # Execute list command
        cli_instance.handle_interactive_list()
        
        # Verify projects were listed
        mock_swarm.list_projects.assert_called_once()
        assert mock_console.print.call_count > 0
        
    def test_show_interactive_help(self, cli_instance, mock_cli_dependencies):
        """Test interactive help display."""
        mock_console = mock_cli_dependencies['console']
        
        # Execute help command
        cli_instance.show_interactive_help()
        
        # Verify help was displayed
        assert mock_console.print.call_count > 0
        
    @pytest.mark.asyncio
    async def test_error_handling_invalid_project(self, cli_instance, mock_cli_dependencies):
        """Test error handling for invalid project ID."""
        mock_swarm = mock_cli_dependencies['swarm']
        mock_console = mock_cli_dependencies['console']
        
        # Mock error response
        mock_swarm.get_project_status.return_value = {"error": "Project not found"}
        
        # Mock arguments
        args = MagicMock()
        args.project_id = "invalid_project"
        
        # Execute status command
        await cli_instance.status(args)
        
        # Verify error was displayed
        mock_console.print.assert_called()
        call_args = mock_console.print.call_args[0][0]
        assert "Project not found" in call_args
        
    @pytest.mark.asyncio
    async def test_configuration_integration(self, cli_instance, mock_cli_dependencies):
        """Test CLI integration with configuration system."""
        mock_config = mock_cli_dependencies['config']
        
        # Verify CLI uses configuration
        assert cli_instance.config == mock_config
        assert cli_instance.cli_config == mock_config.get_cli_config()
        assert cli_instance.display_config == mock_config.get_display_config()
        assert cli_instance.messages == mock_config.get_messages_config()
        
    @pytest.mark.asyncio
    async def test_command_line_argument_parsing(self):
        """Test command line argument parsing."""
        with patch('argparse.ArgumentParser.parse_args') as mock_parse_args, \
             patch('cli.FlutterSwarmCLI') as mock_cli_class:
            
            mock_cli = MagicMock()
            mock_cli_class.return_value = mock_cli
            
            # Mock arguments for create command
            mock_args = MagicMock()
            mock_args.command = "create"
            mock_args.name = "TestApp"
            mock_args.description = "Test description"
            mock_parse_args.return_value = mock_args
            
            # Mock CLI methods
            mock_cli.create_project = AsyncMock()
            
            # Execute main function
            with patch('asyncio.run') as mock_run:
                main()
                
                # Verify asyncio.run was called
                mock_run.assert_called_once()
                
    @pytest.mark.asyncio
    async def test_cli_graceful_shutdown(self, cli_instance, mock_cli_dependencies):
        """Test CLI graceful shutdown on interrupt."""
        mock_swarm = mock_cli_dependencies['swarm']
        mock_console = mock_cli_dependencies['console']
        
        # Mock swarm methods
        mock_swarm.start.return_value = asyncio.Future()
        mock_swarm.start.return_value.set_result(None)
        mock_swarm.stop = AsyncMock()
        
        # Mock keyboard interrupt during interactive mode
        mock_console.input.side_effect = KeyboardInterrupt()
        
        # Mock arguments
        args = MagicMock()
        
        # Execute interactive mode
        await cli_instance.run_interactive(args)
        
        # Verify graceful shutdown
        mock_swarm.stop.assert_called_once()
        
    @pytest.mark.asyncio
    async def test_concurrent_cli_operations(self, cli_instance, mock_cli_dependencies):
        """Test handling of concurrent CLI operations."""
        mock_swarm = mock_cli_dependencies['swarm']
        
        # Mock multiple operations
        mock_swarm.create_project.return_value = "project_1"
        mock_swarm.get_project_status.return_value = {"project": {"name": "TestApp"}}
        mock_swarm.get_agent_status.return_value = {"implementation": {"status": "idle"}}
        
        # Mock display methods
        cli_instance.display_project_status = MagicMock()
        cli_instance.display_agent_status = MagicMock()
        
        # Create mock arguments
        create_args = MagicMock()
        create_args.name = "TestApp"
        create_args.description = "Test app"
        create_args.requirements = None
        create_args.features = None
        create_args.build = False
        
        status_args = MagicMock()
        status_args.project_id = "project_1"
        
        agent_status_args = MagicMock()
        agent_status_args.project_id = None
        
        # Execute operations concurrently
        tasks = [
            cli_instance.create_project(create_args),
            cli_instance.status(status_args),
            cli_instance.status(agent_status_args)
        ]
        
        await asyncio.gather(*tasks)
        
        # Verify all operations completed
        mock_swarm.create_project.assert_called_once()
        mock_swarm.get_project_status.assert_called_once()
        mock_swarm.get_agent_status.assert_called_once()
