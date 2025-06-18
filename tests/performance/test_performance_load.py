"""
Performance and load tests for FlutterSwarm system.
"""

import pytest
import asyncio
import time
from unittest.mock import patch, MagicMock, AsyncMock
from concurrent.futures import ThreadPoolExecutor
import psutil
import gc

from flutter_swarm import FlutterSwarm
from shared.state import shared_state, AgentStatus
from tests.mocks.mock_implementations import MockAgent, MockToolManager
from tests.fixtures.test_constants import SAMPLE_PROJECT_DATA, TIMING_CONSTANTS


@pytest.mark.performance
class TestPerformance:
    """Performance test suite for FlutterSwarm."""
    
    @pytest.fixture
    def performance_swarm(self, mock_anthropic_client, mock_config, mock_tool_manager):
        """Create FlutterSwarm instance for performance testing."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
            return FlutterSwarm()
    
    @pytest.mark.asyncio
    async def test_swarm_startup_time(self, performance_swarm):
        """Test FlutterSwarm startup time performance."""
        # Mock agent start methods to be fast
        for agent in performance_swarm.agents.values():
            agent.start = AsyncMock()
            agent.stop = AsyncMock()
            agent._agent_loop = AsyncMock()
        
        # Measure startup time
        start_time = time.time()
        
        start_task = asyncio.create_task(performance_swarm.start())
        await asyncio.sleep(0.1)  # Let agents initialize
        
        startup_time = time.time() - start_time
        
        # Stop the swarm
        await performance_swarm.stop()
        
        # Verify startup is under acceptable threshold
        assert startup_time < TIMING_CONSTANTS["slow_operation"]
        assert performance_swarm.is_running
        
    @pytest.mark.asyncio
    async def test_project_creation_performance(self, performance_swarm):
        """Test project creation performance."""
        start_time = time.time()
        
        # Create multiple projects rapidly
        project_ids = []
        for i in range(10):
            project_id = performance_swarm.create_project(
                name=f"PerfTestApp{i}",
                description=f"Performance test application {i}",
                requirements=["auth", "database"],
                features=["login", "crud"]
            )
            project_ids.append(project_id)
        
        creation_time = time.time() - start_time
        
        # Verify all projects were created
        assert len(project_ids) == 10
        assert all(pid is not None for pid in project_ids)
        
        # Verify creation time is reasonable
        avg_creation_time = creation_time / 10
        assert avg_creation_time < TIMING_CONSTANTS["medium_operation"]
        
    @pytest.mark.asyncio
    async def test_concurrent_project_builds(self, performance_swarm):
        """Test concurrent project build performance."""
        # Mock agent behaviors
        for agent in performance_swarm.agents.values():
            agent.start = AsyncMock()
            agent.stop = AsyncMock()
            agent._agent_loop = AsyncMock()
        
        # Create multiple projects
        project_ids = []
        for i in range(5):
            project_id = performance_swarm.create_project(
                name=f"ConcurrentApp{i}",
                description=f"Concurrent build test {i}",
                requirements=["basic_functionality"],
                features=["core"]
            )
            project_ids.append(project_id)
        
        # Start the swarm
        start_task = asyncio.create_task(performance_swarm.start())
        await asyncio.sleep(0.1)
        
        # Mock build monitoring
        with patch.object(performance_swarm, '_monitor_build_progress') as mock_monitor:
            mock_monitor.return_value = {
                "status": "completed",
                "files_created": 10,
                "build_time": 30.0
            }
            
            # Build all projects concurrently
            start_time = time.time()
            
            build_tasks = [
                performance_swarm.build_project(project_id)
                for project_id in project_ids
            ]
            
            results = await asyncio.gather(*build_tasks)
            
            concurrent_build_time = time.time() - start_time
        
        # Verify all builds completed
        assert len(results) == 5
        assert all(result["status"] == "completed" for result in results)
        
        # Verify concurrent performance is better than sequential
        # (should be roughly same time as single build due to concurrency)
        assert concurrent_build_time < len(project_ids) * TIMING_CONSTANTS["slow_operation"]
        
        # Stop the swarm
        await performance_swarm.stop()
        
    @pytest.mark.asyncio
    async def test_message_throughput(self, performance_swarm, clean_shared_state):
        """Test message throughput performance."""
        # Register test agents
        for i in range(5):
            clean_shared_state.register_agent(f"test_agent_{i}", ["test_capability"])
        
        # Generate large number of messages
        num_messages = 1000
        start_time = time.time()
        
        for i in range(num_messages):
            from shared.state import AgentMessage, MessageType
            from datetime import datetime
            
            message = AgentMessage(
                message_id=f"perf_msg_{i}",
                from_agent="test_sender",
                to_agent=f"test_agent_{i % 5}",
                message_type=MessageType.TASK_REQUEST,
                content={"task": f"performance_task_{i}"},
                priority=3,
                timestamp=datetime.now()
            )
            
            clean_shared_state.send_message(message)
        
        message_send_time = time.time() - start_time
        
        # Calculate throughput
        throughput = num_messages / message_send_time
        
        # Verify acceptable throughput (should handle > 100 messages/second)
        assert throughput > 100
        
        # Verify messages were queued
        total_queued = sum(
            len(clean_shared_state.get_messages_for_agent(f"test_agent_{i}"))
            for i in range(5)
        )
        assert total_queued == num_messages
        
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, performance_swarm):
        """Test memory usage under load."""
        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Mock agent behaviors
        for agent in performance_swarm.agents.values():
            agent.start = AsyncMock()
            agent.stop = AsyncMock()
            agent._agent_loop = AsyncMock()
        
        # Create many projects to stress memory
        project_ids = []
        for i in range(50):
            project_id = performance_swarm.create_project(
                name=f"MemoryTestApp{i}",
                description=f"Memory stress test {i}" * 10,  # Larger description
                requirements=[f"req_{j}" for j in range(10)],  # Many requirements
                features=[f"feature_{j}" for j in range(15)]  # Many features
            )
            project_ids.append(project_id)
        
        # Start the swarm
        start_task = asyncio.create_task(performance_swarm.start())
        await asyncio.sleep(0.1)
        
        # Simulate build activity
        with patch.object(performance_swarm, '_monitor_build_progress') as mock_monitor:
            mock_monitor.return_value = {
                "status": "completed",
                "files_created": 20
            }
            
            # Build first 10 projects
            build_tasks = [
                performance_swarm.build_project(project_ids[i])
                for i in range(10)
            ]
            
            await asyncio.gather(*build_tasks)
        
        # Check memory usage after load
        peak_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = peak_memory - initial_memory
        
        # Stop the swarm
        await performance_swarm.stop()
        
        # Force garbage collection
        gc.collect()
        
        # Check memory after cleanup
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Verify memory usage is reasonable
        assert memory_increase < 500  # Should not use more than 500MB extra
        
        # Verify memory is released after cleanup (within 50MB of initial)
        assert abs(final_memory - initial_memory) < 50
        
    @pytest.mark.asyncio
    async def test_agent_response_time(self, performance_swarm, clean_shared_state):
        """Test agent response time performance."""
        # Register test agents
        test_agents = {}
        for agent_type in ["implementation", "testing", "security"]:
            agent = MockAgent(agent_type, [f"{agent_type}_capability"])
            test_agents[agent_type] = agent
            clean_shared_state.register_agent(agent_type, [f"{agent_type}_capability"])
            await agent.start()
        
        # Measure response times
        response_times = []
        
        for i in range(20):
            from shared.state import AgentMessage, MessageType
            from datetime import datetime
            
            start_time = time.time()
            
            # Send message to agent
            message = AgentMessage(
                message_id=f"response_test_{i}",
                from_agent="test_sender",
                to_agent="implementation",
                message_type=MessageType.TASK_REQUEST,
                content={"task": f"response_task_{i}"},
                priority=3,
                timestamp=datetime.now()
            )
            
            clean_shared_state.send_message(message)
            
            # Process message
            agent = test_agents["implementation"]
            await agent.process_message(message)
            
            response_time = time.time() - start_time
            response_times.append(response_time)
        
        # Calculate statistics
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        
        # Verify response times are acceptable
        assert avg_response_time < TIMING_CONSTANTS["medium_operation"]
        assert max_response_time < TIMING_CONSTANTS["slow_operation"]
        
        # Cleanup
        for agent in test_agents.values():
            await agent.stop()
            
    @pytest.mark.asyncio
    async def test_scalability_with_agent_count(self, clean_shared_state):
        """Test system scalability with increasing agent count."""
        scalability_results = {}
        
        # Test with different numbers of agents
        for agent_count in [5, 10, 20, 50]:
            start_time = time.time()
            
            # Register agents
            agents = []
            for i in range(agent_count):
                agent_id = f"scale_agent_{i}"
                agent = MockAgent(agent_id, ["scale_capability"])
                agents.append(agent)
                clean_shared_state.register_agent(agent_id, ["scale_capability"])
                await agent.start()
            
            # Send messages to all agents
            message_start_time = time.time()
            
            for i, agent in enumerate(agents):
                from shared.state import AgentMessage, MessageType
                from datetime import datetime
                
                message = AgentMessage(
                    message_id=f"scale_msg_{i}",
                    from_agent="scale_test",
                    to_agent=agent.agent_id,
                    message_type=MessageType.TASK_REQUEST,
                    content={"task": f"scale_task_{i}"},
                    priority=3,
                    timestamp=datetime.now()
                )
                
                clean_shared_state.send_message(message)
                await agent.process_message(message)
            
            message_time = time.time() - message_start_time
            total_time = time.time() - start_time
            
            scalability_results[agent_count] = {
                "total_time": total_time,
                "message_time": message_time,
                "avg_time_per_agent": message_time / agent_count
            }
            
            # Cleanup agents
            for agent in agents:
                await agent.stop()
            
            # Clear shared state
            clean_shared_state._agents.clear()
            clean_shared_state._message_queue.clear()
        
        # Verify scalability characteristics
        # Time per agent should remain relatively constant
        times_per_agent = [
            scalability_results[count]["avg_time_per_agent"]
            for count in [5, 10, 20, 50]
        ]
        
        # Max time per agent should not be more than 2x the min
        assert max(times_per_agent) / min(times_per_agent) < 3.0
        
    @pytest.mark.asyncio
    async def test_concurrent_user_simulation(self, performance_swarm):
        """Test performance under concurrent user load."""
        # Mock agent behaviors
        for agent in performance_swarm.agents.values():
            agent.start = AsyncMock()
            agent.stop = AsyncMock()
            agent._agent_loop = AsyncMock()
        
        # Simulate concurrent users
        num_users = 10
        
        async def simulate_user(user_id):
            """Simulate a single user workflow."""
            # Create project
            project_id = performance_swarm.create_project(
                name=f"UserApp{user_id}",
                description=f"Application for user {user_id}",
                requirements=["auth", "data"],
                features=["login", "profile"]
            )
            
            # Get project status
            status = performance_swarm.get_project_status(project_id)
            
            # Simulate some delay
            await asyncio.sleep(0.1)
            
            return {"user_id": user_id, "project_id": project_id, "status": status}
        
        # Start the swarm
        start_task = asyncio.create_task(performance_swarm.start())
        await asyncio.sleep(0.1)
        
        # Run concurrent user simulations
        start_time = time.time()
        
        user_tasks = [simulate_user(i) for i in range(num_users)]
        user_results = await asyncio.gather(*user_tasks)
        
        concurrent_time = time.time() - start_time
        
        # Verify all users completed successfully
        assert len(user_results) == num_users
        assert all(result["project_id"] is not None for result in user_results)
        
        # Verify reasonable performance under concurrent load
        avg_time_per_user = concurrent_time / num_users
        assert avg_time_per_user < TIMING_CONSTANTS["medium_operation"]
        
        # Stop the swarm
        await performance_swarm.stop()
        
    @pytest.mark.asyncio
    async def test_long_running_stability(self, performance_swarm):
        """Test system stability over extended period."""
        # Mock agent behaviors
        for agent in performance_swarm.agents.values():
            agent.start = AsyncMock()
            agent.stop = AsyncMock()
            agent._agent_loop = AsyncMock()
        
        # Start the swarm
        start_task = asyncio.create_task(performance_swarm.start())
        await asyncio.sleep(0.1)
        
        # Run continuous operations for a period
        operations_completed = 0
        start_time = time.time()
        test_duration = 5.0  # 5 seconds for testing
        
        while time.time() - start_time < test_duration:
            # Create project
            project_id = performance_swarm.create_project(
                name=f"StabilityApp{operations_completed}",
                description="Stability test application",
                requirements=["basic"],
                features=["core"]
            )
            
            # Get status
            status = performance_swarm.get_project_status(project_id)
            
            # Small delay to prevent overwhelming
            await asyncio.sleep(0.01)
            
            operations_completed += 1
        
        total_time = time.time() - start_time
        
        # Verify system remained stable
        assert operations_completed > 10  # Should complete many operations
        assert performance_swarm.is_running
        
        # Calculate operations per second
        ops_per_second = operations_completed / total_time
        assert ops_per_second > 2  # Should handle at least 2 ops/second
        
        # Stop the swarm
        await performance_swarm.stop()
        
    def test_configuration_loading_performance(self):
        """Test configuration loading performance."""
        from config.config_manager import ConfigManager
        
        start_time = time.time()
        
        # Load configuration multiple times
        for i in range(100):
            config = ConfigManager()
            _ = config.get("agents")
            _ = config.get("tools")
            _ = config.get("communication")
        
        config_time = time.time() - start_time
        avg_config_time = config_time / 100
        
        # Verify configuration loading is fast
        assert avg_config_time < TIMING_CONSTANTS["quick_operation"]
        
    @pytest.mark.asyncio
    async def test_shared_state_performance(self, clean_shared_state):
        """Test shared state performance under load."""
        # Register many agents
        num_agents = 20
        for i in range(num_agents):
            clean_shared_state.register_agent(f"perf_agent_{i}", ["test_capability"])
        
        # Update agent states rapidly
        start_time = time.time()
        
        num_updates = 1000
        for i in range(num_updates):
            agent_id = f"perf_agent_{i % num_agents}"
            clean_shared_state.update_agent_status(
                agent_id,
                AgentStatus.WORKING,
                f"Task {i}",
                (i % 100) / 100.0
            )
        
        update_time = time.time() - start_time
        
        # Calculate update throughput
        updates_per_second = num_updates / update_time
        
        # Verify acceptable performance
        assert updates_per_second > 100  # Should handle > 100 updates/second
        
        # Verify final state is correct
        final_states = clean_shared_state.get_agent_states()
        assert len(final_states) == num_agents
        
    @pytest.mark.asyncio
    async def test_memory_leak_detection(self, performance_swarm):
        """Test for memory leaks during repeated operations."""
        import gc
        
        # Force garbage collection
        gc.collect()
        initial_objects = len(gc.get_objects())
        
        # Mock agent behaviors
        for agent in performance_swarm.agents.values():
            agent.start = AsyncMock()
            agent.stop = AsyncMock()
            agent._agent_loop = AsyncMock()
        
        # Perform many create/destroy cycles
        for cycle in range(10):
            # Create projects
            project_ids = []
            for i in range(10):
                project_id = performance_swarm.create_project(
                    name=f"LeakTestApp{cycle}_{i}",
                    description="Memory leak test",
                    requirements=["test"],
                    features=["test"]
                )
                project_ids.append(project_id)
            
            # Force cleanup
            del project_ids
            gc.collect()
        
        # Check for object growth
        gc.collect()
        final_objects = len(gc.get_objects())
        object_growth = final_objects - initial_objects
        
        # Verify no significant object growth (allow some growth for test overhead)
        assert object_growth < 1000  # Should not create excessive objects
